require('dotenv').config()

const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const moment = require('moment') // for date handling
const axios = require("axios"); // for http requests
const inquirer = require("inquirer") // deprecated version, should use import but mess up with other require
const fs = require('fs');

const { pullUpcomingIcsEvents, createOaEvent, updateOaEvent, patchOaEvent } = require("../utils")
const { getCorrespondingOaLocation } = require("../resources/getOaLocation")

// OpenAgenda creds
const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const AGENDA_UID = process.env.AGENDA_UID

const now = moment().format("YYYY-MM-DD");

const importIcs = async (icsUrl) => {
  const oa = new OaSdk({
    publicKey,
    secretKey,
  });
  console.log("Connected to  oa");

  // Pull upcoming events from Google Agenda in Open Agenda schema
  const newOaEvents = await pullUpcomingIcsEvents(icsUrl)
  console.log("icsUrl - ", icsUrl);

  // Iterate over upcoming events
  const uids = []
  let i = 0;
  for (const newOaEvent of newOaEvents) {
    console.log("\n======== Scanning newOaEvent ========");
    // // Skip guessing location for now
    // const locationResult = await getCorrespondingOaLocation(newOaEvent.locationName)
    // console.log("locationResult - ", locationResult);
    // if (locationResult) newOaEvent.locationUid = locationResult
    console.log(newOaEvent.title, newOaEvent.timings[0].begin, newOaEvent.locationName);
    try {
      // For each upcoming event, check if it already exists in Open Agenda
      // The key is the "uid-externe" but the API does not allow to filter on it
      // So we get all events in the timeframe and then find the "uid-externe"
      const isAfter = moment(newOaEvent.timings[0].begin).subtract(1, 'day').format("YYYY-MM-DD:00:00:00.000");
      const isBefore = moment(newOaEvent.timings[0].end).add(1, 'day').format("YYYY-MM-DD:00:00:00.000");
      const oaEvents = await axios.get(
        `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/events`,
        {
          params: { key: publicKey, monolingual: "fr", "timings[gte]": isAfter, "timings[lte]": isBefore, "size": 300 },
          headers: { 'Content-Type': 'application/json' }
        }
      )
      // Check if an existing oa event is there with the same "uid-externe"
      const oaEvent = oaEvents.data.events.find(event => event["uid-externe"] === newOaEvent["uid-externe"]);
      if (!oaEvent && oaEvents && oaEvents.data.events.length > 0) {
        // Prompt the user to select an existing event or create a new one
        const oaEventsChoices = oaEvents.data.events.map((e) => {
          return {
            name: `${e.title} - ${e.location.name}`,
            value: e.uid
          }
        })

        oaEventsChoices.unshift({name: "Créer un nouvel événement",value: null})

        const question = {
          type: 'list',
          name: 'uid',
          message: 'Select the OA event corresponding to the GA event',
          choices: oaEventsChoices
        }

        // const answer = await inquirer.prompt(question)
        const answer = null

        if (!answer || answer.uid === null) {
          // No existing event, create a new one
          console.log("\t[CREATE] Create new event")
          const createdEvent = await createOaEvent(oa, AGENDA_UID, newOaEvent)
          console.log("\t[CREATE] uid", createdEvent.uid);
          uids.push(createdEvent.uid)
        } else {
          // Patch externe-uid to the oa event
          console.log("\t[PATCH] Patch existing event - ", oaEventsChoices.find((e) => e.value === answer.uid).name);
        const patchData = {"uid-externe": newOaEvent["uid-externe"]}
          const patchedEvent = await patchOaEvent(oa, AGENDA_UID, answer.uid, patchData)
          console.log("\t[PATCH] uid", patchedEvent.uid);
          // Do not add uid to the log list to avoid deleting an event that's not originally from the ics file
        }
      } else if (oaEvent) {
        // Option 1: SIMPLE - Existing event, do nothing. We trust first import only
        console.log("\t[SKIP] Skip existing event - ", oaEvent.title);
        uids.push(oaEvent.uid)
        //  // Option 2: RISKY - Existing event, update it in case it has changed since creation. We trust ics live source.
        // console.log("\t[UPDATE] Update existing event - ", oaEvent.title);
        // const updatedEvent = await updateOaEvent(oa, AGENDA_UID, oaEvent.uid, newOaEvent)
        // console.log("\t[UPDATE] uid", updatedEvent.uid);
        // uids.push(updatedEvent.uid)
      } else {
        // Default: Create the event because nothing seems to be there
        console.log("\t[CREATE] Create new event")
        const createdEvent = await createOaEvent(oa, AGENDA_UID, newOaEvent)
        console.log("\t[CREATE] uid", createdEvent.uid);
        uids.push(createdEvent.uid)
      }
    } catch (err) {
      if (err.response.data.errors) {
        console.log("Error: ", err.response.data.errors);
      } else {
        console.log("Error: ", err);
      
      }
    } finally {
      console.log("uids - ", uids) // Re-user ids for further update, delete...
      fs.writeFile(`ics/import_ics_${now}.txt`, uids.join('\n'), (err) => {
        if (err) throw err;
        console.log('Log file saved.');
      });
      i++
    }
  }
}

module.exports = { importIcs }

