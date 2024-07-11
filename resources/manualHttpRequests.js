require('dotenv').config()
const axios = require("axios");

const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const ACCESS_TOKEN_URL = process.env.ACCESS_TOKEN_URL
const AGENDA_UID = process.env.AGENDA_UID
// const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID

const retrieveAccessToken = async (apiSecretKey) => {
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
            console.log("OAuth Response: ", oauthResponse.data);
            return oauthResponse.data.access_token;
        }
    } catch (exc) {
        console.error("Error retrieving access token: ", exc.response ? exc.response.data : exc.message);
    }

    console.log("[Retrieve accessToken] Error - no access token retrieved");
    return null;
}

const getLocations = async (accessToken) => {
    const headers = {
        "Content-Type": 'application/json',
        "access-token": accessToken,
        "nonce": Date.now(),
    };
    const url = `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/locations`;

    try {
        const response = await axios.get(url, { headers });
        if (response.status >= 200 && response.status <= 299) {
            console.log("Locations Response: ", response.data);
            return response.data;
        }
    } catch (exc) {
        console.error("Error retrieving locations: ", exc.response ? exc.response.data : exc.message);
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
            return eventCreationResponse.data.access_token;
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

(async () => {
    console.log("START");

    const accessToken = await retrieveAccessToken(secretKey);
    if (accessToken) {
        console.log("Access Token: ", accessToken);

        // const locations = await getLocations(accessToken);
        // console.log("Locations: ", locations);
        // const event = {
        //     title: {fr: "[TEST] Evénement ACN"},
        //     description: {fr: "Description courte ACN"},
        //     timings: [
        //         {
        //             begin: "2024-06-18T17:00:00+0200",
        //             end: "2024-06-18T19:00:00+0200"
        //         }
        //     ],
        //     locationUid: TBD_LOCATION_UID,
        //     attendanceMode: 1
        // }
        // await createEvent(accessToken, event)
        await deleteEvent(accessToken, 38636380)
    }

    console.log("END");
})();
