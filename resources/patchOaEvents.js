const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const axios = require("axios"); // for http requests
const moment = require('moment') // for date handling

const { patchOaEvent } = require("../utils");


require('dotenv').config()
// OpenAgenda creds
const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const AGENDA_UID = process.env.AGENDA_UID

const oa = new OaSdk({
    publicKey,
    secretKey,
});


const main = async () => {
    const oaEvents = await axios.get(
        `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/events`,
        {
            params: {
                key: publicKey,
                monolingual: "fr",
                "timings[gte]": moment().subtract(1, 'day').format("YYYY-MM-DD:00:00:00.000"),
                "size": 300,
                "locationUid": "87694536"
            },
            headers: { 'Content-Type': 'application/json' }
        }
    )
    
    const patch = {
        keywords: { fr: "Les Rias" }
    }

    for (const oaEvent of oaEvents.data.events) {
        try {
            await patchOaEvent(oa, AGENDA_UID, oaEvent.uid, patch)
        } catch (error) {
            console.error(error)
        }
    }
}

main()