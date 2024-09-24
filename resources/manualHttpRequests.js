require('dotenv').config()
const axios = require("axios");
const fs = require('fs');

const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const ACCESS_TOKEN_URL = process.env.ACCESS_TOKEN_URL
const AGENDA_UID = process.env.AGENDA_UID
const tokenFilePath = 'secret_token.json';
// const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID

const retrieveAccessToken = async (apiSecretKey) => {

    // check if token already exist
    if (fs.existsSync(tokenFilePath)) {
        const tokenFileContent = await fs.promises.readFile(tokenFilePath, 'utf8');
        const tokenData = JSON.parse(tokenFileContent);

        if (tokenData.access_token && tokenData.endate && Date.now() - tokenData.endate < 3600000) {
                // console.log("Using existing access token");
            const accessToken = tokenData.access_token;
            return accessToken;
        }
    };
        
    //else 
    console.log("Request a new token and save it in secret_token.json");
    const headers = {
        "Content-Type": 'application/json',
    };
    const body = {
        grant_type: "client_credentials",
        code: apiSecretKey,
    };

    try {
        const oauthResponse = await axios.post(ACCESS_TOKEN_URL, body, { headers });

        if (oauthResponse.status >= 200 && oauthResponse.status <= 299) {
            // Save token to token.json file
            const tokenData = {
                access_token: oauthResponse.data.access_token,
                endate: Date.now() + 3600000, // 1 hour from now
            };
            await fs.promises.writeFile(tokenFilePath, JSON.stringify(tokenData));

            return oauthResponse.data.access_token;
        }
    } catch (exc) {
        console.error("Error retrieving access token: ", exc.response ? exc.response.data : exc.message);
    }

    console.log("[Retrieve accessToken] Error - no access token retrieved");
    return null;
}

const getLocations = async (accessToken) => {

    const url = `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/locations`;

    try {
        let after=0
        let all_locations=[]
        
        const headers = {
            "Content-Type": 'application/json',
            "access-token": accessToken,
            "nonce": Date.now(),
            };
        const params = {
            "after":after,
            "detailed":1
        };

        while (after != null ){
            headers["nonce"] = Date.now();
            params["after"]  = after
            const response   = await axios.get(url, { headers, params });
                if (response.status >= 200 && response.status <= 299) {
                    all_locations =all_locations.concat(response.data.locations);
                    after=response.data.after
                }
            
        }
        return all_locations

    } catch (exc) {
        console.error("Error retrieving locations: ", exc.response ? exc.response.data : exc.message);
    }
}

const postLocation = async (accessToken, address) => {
    const headers = {
        "Content-Type": 'application/json',
        "access-token": accessToken,
        "nonce": Date.now(),
    };
    const body = {
        name: address,
        address: address,
        countryCode: "FR",
        state: 0, // means "not verified"
    };
    const url = `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/locations`;

    const response = await axios.post(url, body, { headers })
        .catch(function (error) {
            if (error.response) {
                // Catching OA response
                if (error.response.status = 400 
                    && error.response.data.message == "geocoder didn't find address") {
                    console.error("No existing address found by OA API");
                    return null;
                }
                console.log(error.response.status, error.response.data);
            } else {
                // Something happened in setting up the request that triggered an Error
                console.log('Error OA Post location', error);
            }

        });
        return response?.data ? response.data : null
}

const deleteLocation = async (accessToken, locationUid) => {
    const headers = {
        "Content-Type": 'application/json',
        "access-token": accessToken,
        "nonce": Date.now(),
    };

    const url = `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/locations/${locationUid}`;

    try {
        const response = await axios.delete(url, { headers });
        if (response.status >= 200 && response.status <= 299) {
            // console.log("Locations Response: ", response.data);
            return response.data;
        }
    } catch (exc) {
        console.error("Error deleting location: ", exc.response ? exc.response.data : exc.message);
    }
}

const createEvent = async (accessToken, event) => {
    const headers = {
        "Content-Type": 'application/json',
    };
    const body = {
        "access_token": accessToken,
        "nonce": Date.now(),
        "data": event,
    };
    const url = `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/events`;
    try {
        const eventCreationResponse = await axios.post(url, body, { headers });

        if (eventCreationResponse.status >= 200 && eventCreationResponse.status <= 299) {
            console.log("Event creation response: ", eventCreationResponse.data);
            return eventCreationResponse.data;
        }
    } catch (exc) {
        console.error("Error retrieving access token: ", exc.response ? exc.response.data : exc.message);
    }
}

const deleteEvent = async (accessToken, eventUid) => {
    const headers = {
        "Content-Type": 'application/json',
        "access-token": accessToken,
        "nonce": Date.now(),
    };
    const url = `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/events/` + eventUid.toString();
    try {
        const response = await axios.delete(url, { headers });
        if (response.status >= 200 && response.status <= 299) {
            console.log("Delete Event Response: ", response.data);
            return response.data;
        }
    } catch (exc) {
        console.error("Error deleting event: ", exc.response ? exc.response.data : exc.message);
    }
}

module.exports = { retrieveAccessToken, getLocations, postLocation, createEvent, deleteEvent, deleteLocation }

// (async () => {
//     console.log("START");

//     const accessToken = await retrieveAccessToken(secretKey);
//     if (accessToken) {
//         console.log("Access Token: ", accessToken);

//         // const locations = await getLocations(accessToken);
//         // console.log("Locations: ", locations);
//         // const event = {
//         //     title: {fr: "[TEST] Evénement ACN"},
//         //     description: {fr: "Description courte ACN"},
//         //     timings: [
//         //         {
//         //             begin: "2024-06-18T17:00:00+0200",
//         //             end: "2024-06-18T19:00:00+0200"
//         //         }
//         //     ],
//         //     locationUid: TBD_LOCATION_UID,
//         //     attendanceMode: 1
//         // }
//         // await createEvent(accessToken, event)
//         await deleteEvent(accessToken, 38636380)
//     }

//     console.log("END");
// })();
