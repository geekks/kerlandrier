require('dotenv').config()
const Fuse = require('fuse.js')

const { postLocation, retrieveAccessToken, deleteLocation, getLocations } = require("./manualHttpRequests");

// const AGENDA_UID = process.env.AGENDA_UID
const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID
// const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;

/**
 * Search a given adress in OA locations DB (using name & adress) with FuzeJS
 * 
 * @param {string} eventlocation - The event location to search for e.g. "MJC Le Sterenn, Tregunc"
 * @param {array} locationsData - The list of all locations fetched from OpenAgenda.
 * @return {array} An array of best matching locations with {OALocationUid,NameAdress, roundedScore} sorted by best score
 */
const searchOALocation = (eventlocation, locationsData) => {
    const options = {
        minScore: 0.7,
        scorePrecision: 4
    }

    const fuzeOptions = {
        includeScore: true,
        ignoreLocation: true,
        keys: [
            { name: 'name', weight: 0.8 },
            { name: 'address', weight: 0.7 },
        ],
    }
    const fuse = new Fuse(locationsData, fuzeOptions)
    const results = fuse.search(eventlocation)
    if (results.length > 0) {
        const precision = 10 ** options.scorePrecision
        // FIXME: Understand what is the "best" score in order to sort results
        const bestResults = results
            .filter(entry => entry.score < options.minScore)
            .map(entry => ({
                OALocationUid: entry.item.uid,
                NameAdress: `${entry.item.name} - ${entry.item.address}`,
                roundedScore: Math.round(entry.score * precision) / 10 ** precision,
                score: entry.score
            }));
        return bestResults.length > 0 ? bestResults : []
    }
    return []
};

/**
 * Get a good matching location in OpenAgenda or empty object.
 *
 * @param {string} GaLocations  - An adress or place name.
 * @return {Promise<Array>}     - Object with found OA location {OALocationuid, NameAdress, roundedScore}.
 *                                or {} if no match found.
 *                           
 */
const matchGaOaLocations = async (GaLocation, accessToken) => {
    const resultOAL = await getLocations(accessToken);
    const OALocations = resultOAL?.locations ?? []
    console.log("Searching match for ", GaLocation);
    if (!GaLocation || OALocations?.length == 0) {
        console.log("[ERROR] GaLocation is null or OA Locations list is empty ")
        return {}
    }
    const searchFullResultOA = searchOALocation(GaLocation, OALocations)
    if (!searchFullResultOA[0]?.NameAdress) {
        console.log("[ERROR] No match found in existing OA locations ")
        return {}
    }
    
    console.log("[SUCCESS] Match with '", searchFullResultOA[0].NameAdress,"'")
    return searchFullResultOA[0]

};

const getCorrespondingOaLocationFromGa = async (GaLocation) => {
    const accessToken = await retrieveAccessToken(secretKey)

    // try to find an existing OALocation
    const OALocation = await matchGaOaLocations(GaLocation, accessToken)

    if (OALocation?.NameAdress && OALocation?.OALocationUid) {
        // Case 1: Best case scenario where match is found
        // FIXME: What if we have a false positive e.g. GaLocation = "Mediathèque Elliant" and OaLocation = "Médiathèque Concarneau"
        // TODO: (?) Tweak FuzeJS to return nothing when score is not high enough
        console.log("--> Returning existing OALcocation: ", OALocation.OALocationUid)
        return OALocation.OALocationUid
    } else if (GaLocation) {
        // then try to create an OALocation with their search API
        // Case 2 : No match found so we try to create the event with Open Agenda GeoCoding API
        // CAVEAT: Trick to split name and address is specific to Google Agenda syntax (cannot be used as is for other sources e.g. when scraping)
        const response = await postLocation(accessToken, GaLocation.split(",")[0], GaLocation)
        if (!response?.location?.uid) {
            // Case 2.1 : Nothing created
            console.log("--> Returning location  'To be defined' (Could not create location on OpenAgenda)")
            return TBD_LOCATION_UID
        }
        const newOALocation = response.location
        console.log("New OAlocation created (to be validated): ", newOALocation.uid)
    
        // check if created location is more or less in Breizh
        const lat = newOALocation.latitude
        const long = newOALocation.longitude
        if (newOALocation?.uid
            && parseFloat(lat) < 49 && parseFloat(lat) > 47
            && parseFloat(long) < -1 && parseFloat(long) > -5.5
        ) {
            // Case 2.2 : Valid location in Breizh
            console.log("--> Returning a valid new OA location: ", newOALocation.name, newOALocation.address)
            return newOALocation.uid    
        } else {
            // Case 2.3 : Invalid location, not in Breizh. Delete it.
            const data = await deleteLocation(accessToken, newOALocation.uid)
            console.log("Location not in Breizh. Newly created OA Location was deleted :", newOALocation.uid, data.success ? "success" : "failed" + data)
            console.log("--> Returning 'To be defined' location")
            return TBD_LOCATION_UID
        }
    } else {
        return TBD_LOCATION_UID
    }

}

module.exports = { getCorrespondingOaLocationFromGa }

/**
 * Test getCorrespondingOaLocationFromGa() with different exemples             
 */

// const LocationsExemples = [
//     { GALocation: 'MJC Tregunc Le Sterenn, Rue Jacques Prévert, 29910 Trégunc, France'  },
//     { GALocation: 'Explore'  },
//     { GALocation: "Bar de Test, 1 Pl. de l'Église, 29100 Pouldergat"  },
//     { GALocation: 'qsdfg'  },
//     { GALocation: '30 Rue Edgar Degas, 72000 Le Mans'  },
//     { GALocation: '11 Lieu-dit, Quilinen, 29510 Landrévarzec'}
// ]

// async function testLocations( locationArray) {
//     for (const loc of locationArray) {
//         console.log("Searching for '", loc.GALocation,"'\n");
//         const testUid = await getCorrespondingOaLocationFromGa(loc.GALocation);
//         console.log("matching --> OA Uid=", testUid);
//         console.log("--------------");
//     }
// };

// testLocations(LocationsExemples);