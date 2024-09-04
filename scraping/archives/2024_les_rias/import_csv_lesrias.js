require('dotenv').config()
const fs = require('fs');
const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const moment = require('moment') // for date handling
const axios = require("axios"); // for http requests

const { createOaEvent } = require("./utils")
const { processCsv } = require("./resources/2024_lesrias")

// OpenAgenda creds
const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const AGENDA_UID = process.env.AGENDA_UID

const oa = new OaSdk({
  publicKey,
  secretKey,
});


const main = async () => {
  const uids = []
  try {
    // Format csv data into oa events
    const lesRias = await processCsv();
    // Get upcoming events from Open Agenda to check duplicates
    const oaEvents = await axios.get(
        `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/events`,
        {
          params: { key: publicKey, monolingual: "fr", "timings[gte]": moment().subtract(1, 'day').format("YYYY-MM-DD:00:00:00.000"), "size": 300 },
          headers: { 'Content-Type': 'application/json' }
        }
      )

    for (const event of lesRias) {
      // Check if an existing oa event is there with the same "uid-externe"
      const oaEvent = oaEvents.data.events.find(e => e["uid-externe"] === event["uid-externe"]);
      if (oaEvent) {
        console.log("Skipping event - ", event.slug);
        continue;
      } else {
        const createdEvent = await createOaEvent(oa, AGENDA_UID, event)
        console.log("createdEvent - ", createdEvent.slug);
        uids.push(createdEvent.uid)
      }
    }
  } catch (error) {
    console.error('Error processing CSV:', error);
  } finally {
    console.log("uids - ", uids);
    fs.writeFile('./resources/2024_lesrias.txt', uids.join('\n'), (err) => {
      if (err) throw err;
      console.log('Log file saved.');
    });
  }
}

main()