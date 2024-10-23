require('dotenv').config()

const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const moment = require('moment') // for date handling
const axios = require("axios"); // for http requests
const inquirer = require("inquirer") // deprecated version, should use import but mess up with other require
const fs = require('fs');

const { pullUpcomingIcsEvents, createOaEvent, updateOaEvent, patchOaEvent } = require("../utils")
const { getCorrespondingOaLocation } = require("../resources/getOaLocation")
const { retrieveAccessToken, getLocations } = require("../resources/manualHttpRequests")

const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID 

// OpenAgenda creds
const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const AGENDA_UID = process.env.AGENDA_UID

const now = moment().format("YYYY-MM-DD_HHmmss");

const importIcs = async (icsUrl) => {
  const oa = new OaSdk({
    publicKey,
    secretKey,
  });
  console.log("Connected to  oa");

  // Pull upcoming events from Google Agenda in Open Agenda schema
  const newOaEvents = await pullUpcomingIcsEvents(icsUrl)
  console.log("icsUrl - ", icsUrl);

// Build location prompt
  const accessToken = await retrieveAccessToken(secretKey)
    const locations = await getLocations(accessToken)
    // Sort by city and address
    locations.sort((a, b) => {
      if (a.city < b.city) return -1
      if (a.city > b.city) return 1
      if (a.name < b.name) return -1
      if (a.name > b.name) return 1
      return 0
    })
    // console.log("locations - ", locations);
    const locationsChoices = locations.map(l => {
      return {name: `${l.city} - ${l.name} - ${l.address}`, value: l.uid}
    });
locationsChoices.unshift({name: "=== DEFAULT LOCATION ===",value: TBD_LOCATION_UID})
    const locationsQuestion = {
          type: 'list',
          name: 'uid',
          message: 'Select the location corresponding to the event',
        choices: locationsChoices
    }


  // Iterate over upcoming events
  const uids = []
  let i = 0;
  console.log("newOaEvents - ", new Set(newOaEvents.map(e => e.locationName).sort((a, b) => a.localeCompare(b))));
  for (const newOaEvent of newOaEvents) {
    // console.log("\n======== Scanning newOaEvent ========");
    // // Skip guessing location for now
    // const locationResult = await getCorrespondingOaLocation(newOaEvent.locationName)
    // console.log("locationResult - ", locationResult);
    // if (locationResult) newOaEvent.locationUid = locationResult
    // console.log(newOaEvent.title, newOaEvent.timings[0].begin, newOaEvent.locationName);
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
      // Find existing oa event with same "uid-externe"
      const oaEvent = oaEvents.data.events.find(event => event["uid-externe"] === newOaEvent["uid-externe"]);
      if (!oaEvent && oaEvents && oaEvents.data.events.length > 0) {
        // No existing event, prompt the user to select an existing event or create a new one
        const oaEventsChoices = oaEvents.data.events.map((e) => {
          return {
            name: `${e.title} - ${e.location.name}`,
            value: e.uid
          }
        })

        oaEventsChoices.unshift({name: "Créer un nouvel événement",value: null})

        // Do this to auto-create new event
        const answer = null
        
        // // Do this to ask user
        // const question = {
        //   type: 'list',
        //   name: 'uid',
        //   message: 'Select the OA event corresponding to the GA event',
        //   choices: oaEventsChoices
        // }
        // const answer = await inquirer.prompt(question) 
        
        if (!answer || answer.uid === null) {
          
          // New oa event auto-creation or
          // User asks to create a new oa event
          console.log("\t[CREATE] Create new event - User decision")
          // Ask for location via user prompt
          console.log("newOaEvent - ", newOaEvent.title, newOaEvent.description.fr, newOaEvent.timings[0].begin);
         const location = await inquirer.prompt(locationsQuestion)
         if (location) newOaEvent.locationUid = location.uid
          const createdEvent = await createOaEvent(oa, AGENDA_UID, newOaEvent)
          console.log("\t[CREATE] uid", createdEvent.uid);
          uids.push(createdEvent.uid)
        } else {
          // User has selected an existing oa event
        //   console.log("\t[PATCH] Patch existing event - ", oaEventsChoices.find((e) => e.value === answer.uid).name);
        // const patchData = {"uid-externe": newOaEvent["uid-externe"]}
          const patchedEvent = await patchOaEvent(oa, AGENDA_UID, answer.uid, patchData)
          console.log("\t[PATCH] uid", patchedEvent.uid);
          // Do not add uid to the log list to avoid deleting an event that's not originally from the ics file
        }
      } else if (oaEvent) {
        // Option 1: SIMPLE - Existing event, do nothing. We trust first import only
        // console.log("\t[SKIP] Skip existing event - ", oaEvent.title);
        // Do not add uid to the log list to avoid deleting an event by mistake
        //  // Option 2: RISKY - Existing event, update it in case it has changed since creation. We trust ics live source.
        // console.log("\t[UPDATE] Update existing event - ", oaEvent.title);
        // const updatedEvent = await updateOaEvent(oa, AGENDA_UID, oaEvent.uid, newOaEvent)
        // console.log("\t[UPDATE] uid", updatedEvent.uid);
        // uids.push(updatedEvent.uid)
      } else {
        // Default: Create the event because nothing seems to be there
        console.log("\t[CREATE] Create new event - Default")
        // Ask for location via user prompt
          console.log("newOaEvent - ", newOaEvent.title, newOaEvent.description.fr, newOaEvent.timings[0].begin);
         const location = await inquirer.prompt(locationsQuestion)
        if (location) newOaEvent.locationUid = location.uid
        const createdEvent = await createOaEvent(oa, AGENDA_UID, newOaEvent)
        console.log("\t[CREATE] uid", createdEvent.uid);
        uids.push(createdEvent.uid)
      }
    } catch (err) {
      if (err.response.data.errors) {
        console.log("OA Error: ", err.response.data.errors);
      } else {
        console.log("Other Error: ", err);
      
      }
    } finally {
      // console.log("uids - ", uids) // Re-user ids for further update, delete...
      console.log("Uploaded " + i + " events from ICS URL");
      fs.writeFile(`ics/import_ics_${now}.txt`, uids.join('\n'), (err) => {
        if (err) throw err;
        // console.log('Log file saved.');
      });
      i++
    }
  }
}

module.exports = { importIcs }

