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
 * @param {string} eventlocation - The event location to search for.
 * @param {array} locationsData - The list of locations fetched from OpenAgenda.
 * @return {array} An array of best matching locations with {OALocationUid,NameAdress, roundedScore}.
 */
const searchOALocation = (eventlocation, locationsData) => {

    const options = {
        minScore: 0.7,
        scorePrecision: 4
    }

    const fuzeOptions = {
        includeScore: true,
        keys: [
            { name: 'name', weight: 0.8 },
            { name: 'address', weight: 0.7 },
        ],
    }
    const fuse = new Fuse(locationsData, fuzeOptions)
    const results = fuse.search(eventlocation)
    if (results.length > 0) {
        const precision = 10 ** options.scorePrecision
        const bestResults = results
            .filter(entry => entry.score < options.minScore)
            .map(entry => ({
                OALocationUid: entry.item.uid,
                NameAdress: `${entry.item.name} - ${entry.item.address}`,
                roundedScore: Math.round(entry.score * precision) / 10 ** precision
                // score: entry.score
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
const matchGaOaLocations = async (GaLocation) => {
    const accessToken = await retrieveAccessToken(secretKey)

    const resultOAL = await getLocations(accessToken);
    const OALocations = resultOAL?.locations ?? []

    if (!GaLocation || OALocations?.length == 0) {
        console.log("ERROR : in GaLocation: '", GaLocation, "' or OA Locations list is empty ")
        return {}
    }
    const searchFullResultOA = searchOALocation(GaLocation, OALocations)
    if (!searchFullResultOA[0]?.NameAdress) {
        return {}
    }
    console.log("OK. match with '", searchFullResultOA[0].NameAdress,"'")
    return searchFullResultOA[0]

};

const getCorrespondingOALocation = async (GaLocation) => {

    // try to find an existing OALocation
    const OALocation = await matchGaOaLocations(GaLocation)
    if ( ! OALocation?.OALocationUid) {
        console.log("No match found in existing OA locations ")
    }

    if (OALocation?.NameAdress && OALocation?.OALocationUid) {
        console.log("--> Returning existing OALcocation: ", OALocation.OALocationUid)
        return OALocation.OALocationUid
    }
    // then try to create an OALocation with their search API (Which one ?)
    else if (GaLocation) {
        const accessToken = await retrieveAccessToken(secretKey)
        const response = await postLocation(accessToken, GaLocation.split(",")[0], GaLocation)
        if (!response?.location?.uid) {
            console.log("--> Returnng location  'To be defined'")
            return TBD_LOCATION_UID
        }
        const newOALocation = response.location
        console.log("New OAlocation created: ", newOALocation.uid)
    
        // check if created location is more or less in Breizh
        const lat = newOALocation.latitude
        const long = newOALocation.longitude
        if (newOALocation?.uid
            && parseFloat(lat) < 49 && parseFloat(lat) > 47
            && parseFloat(long) < -1 && parseFloat(long) > -5.5
        ) {
            console.log("--> Returning a valid new OA location: ", newOALocation.name, newOALocation.address)
            return newOALocation.uid    
        } else {
        const data = await deleteLocation(accessToken, newOALocation.uid)
        console.log("No location in Breizh.Deleteing new OA Location :", newOALocation.uid, data.success ? "success" : "failed" + data)
        console.log("--> Returning 'To be defined' location")
        return TBD_LOCATION_UID
        }
        // if not, delete created location
    } else {
        return TBD_LOCATION_UID
    }

}

module.exports = { getCorrespondingOALocation }

/**
 * Test getCorrespondingOALocation() with different exemples             
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
//         const testUid = await getCorrespondingOALocation(loc.GALocation);
//         console.log("matching --> OA Uid=", testUid);
//         console.log("--------------");
//     }
// };

// testLocations(LocationsExemples);