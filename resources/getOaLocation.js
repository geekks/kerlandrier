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
    // TODO: (?) Tweak FuzeJS to return nothing when score is not high enough
    const options = {
        minScore: 0.4,
        scorePrecision: 4,
        threshold: 0.5,
    }

    const fuzeOptions = {
        includeScore: true,
        ignoreLocation: true,
        keys: [
            { name: 'name', weight: 1.5 },
            { name: 'address', weight: 0.3 },
        ],
    }
    const fuse = new Fuse(locationsData, fuzeOptions, debug=false)
    const results = fuse.search(eventlocation)
    if (results.length > 0) {
        if (debug) console.log("Best result: ", results[0].item, "score: ", results[0].score)
        const precision = 10 ** options.scorePrecision
        // FIXME: Understand what is the "best" score in order to sort results
        const SelectedResult = results
            .filter(entry => entry.score < options.minScore)
            .map(entry => ({
                OALocationUid: entry.item.uid,
                NameAdress: `${entry.item.name} - ${entry.item.address}`,
                roundedScore: Math.round(entry.score * precision) / 10 ** precision,
                score: entry.score
            }))[0];
        return SelectedResult ?? null
    }
    return null
};

/**
 * Get a good matching location in OpenAgenda or empty object.
 *
 * @param {string} inputLocations  - An adress or place name.
 * @return {Promise<Array>}     - Object with found OA location {OALocationuid, NameAdress, roundedScore}.
 *                                or {} if no match found.
 *                           
 */
const matchOaLocations = async (inputLocation, accessToken, debug=false) => {
        if (debug) console.log("Searching match for ", inputLocation);

    const OALocations = await getLocations(accessToken) ?? [];
        if (!inputLocation || OALocations?.length == 0) {
            console.log("[ERROR] inputLocation is null or OA Locations list is empty ")
                return {}
        }
        if (debug) console.log("Number of OAlocations: ", OALocations.length);
    const searchResultOA = searchOALocation(inputLocation, OALocations)
        if ( ! searchResultOA?.NameAdress) {
            if (debug) console.log("[ERROR] No match found in existing OA locations ")
                return {}
        }
    
        if (debug) console.log("[SUCCESS] Match with '", searchResultOA.NameAdress,"'")
    return searchResultOA

};

const getCorrespondingOaLocation = async (inputLocation, debug=false) => {
    const accessToken = await retrieveAccessToken(secretKey)

    // try to find an existing OALocation
    // CAVEAT : Fuze is lost with long string search. Keeping only first 15 characters
    const OALocation = await matchOaLocations(inputLocation.substring(0, 20), accessToken, debug)

    if (OALocation?.NameAdress && OALocation?.OALocationUid) {
        // Case 1: Best case scenario where match is found
        // FIXME: What if we have a false positive e.g. inputLocation = "Mediathèque Elliant" and OaLocation = "Médiathèque Concarneau"
        if (debug) console.log("--> Returning existing OALcocation: ", OALocation.OALocationUid)
        return OALocation.OALocationUid
    } else if (inputLocation) {
        // Case 2 :No match found so we try to create the event with Open Agenda GeoCoding API
        // CAVEAT:  Hard to distinguih location name from postal address. We sends all location info to AO API.
        //          NB: Spliting name and address is specific to Google Agenda syntax (cannot be used as is for other sources e.g. when scraping)
        const response = await postLocation(accessToken, inputLocation)
        if (!response?.location?.uid) {
            // Case 2.1 : Nothing created
            if (debug) console.log("--> Returning location  'To be defined' (Could not create location on OpenAgenda)")
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
            if (debug) console.log("--> Returning a valid new OA location: ", newOALocation.name, newOALocation.address)
            return newOALocation.uid    
        } else {
            // Case 2.3 : Invalid location, not in Breizh. Delete it.
            const data = await deleteLocation(accessToken, newOALocation.uid)
            if (debug) console.log("Location not in Breizh. Newly created OA Location was deleted :", newOALocation.uid, data.success ? "success" : "failed" + data)
            if (debug) console.log("--> Returning 'To be defined' location")
            return TBD_LOCATION_UID
        }
    } else {
        return TBD_LOCATION_UID
    }

}

module.exports = { getCorrespondingOaLocation }

/**
 * Test getCorrespondingOaLocation() with different exemples             
 */

// const LocationsExemples = [
//     { inputLocation: 'MJC Tregunc Le Sterenn, Rue Jacques Prévert, 29910 Trégunc, France'  },
//     { inputLocation: 'MJC Tregunc Le Sterenn, Rue Jacques Prévert'},
//     { inputLocation: 'MJC Tregunc Le Sterenn'},
//     { inputLocation: 'Le Sterenn'},
//     { inputLocation: 'MJC Tregunc'},
    // { inputLocation: 'Explore'  },
    // { inputLocation: "Bar de Test, 1 Pl. de l'Église, 29100 Pouldergat"  },
    // { inputLocation: 'qsdfg'  },
    // { inputLocation: '30 Rue Edgar Degas, 72000 Le Mans'  },
    // { inputLocation: '11 Lieu-dit, Quilinen, 29510 Landrévarzec'},
    // { inputLocation: 'Kerminy, Rosporden'},
    // { inputLocation: 'CONCARNEAU, Carré des larrons'}


// async function testLocations( locationArray) {
//     for (const loc of locationArray) {
//         const testUid = await getCorrespondingOaLocation(loc.inputLocation, debug=true);
//         console.log("matching --> OA Uid=", testUid);
//         console.log("--------------");
//     }
// };

// testLocations(LocationsExemples);