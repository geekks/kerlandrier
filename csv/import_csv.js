const fs = require('fs');
const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const moment = require('moment-timezone');
const TIMEZONE = 'Europe/Paris';
const axios = require("axios"); // for http requests
const csv = require('csv-parser');

const { slugify, updateOaEvent } = require('../utils');

const { createOaEvent } = require("../utils");
const { getCorrespondingOaLocation, matchOaLocations } = require("../resources/getOaLocation")

require('dotenv').config()
// OpenAgenda creds
const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const AGENDA_UID = process.env.AGENDA_UID
const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID



// from root: node import_csv.js <filename>
// node csv/import_csv.js 2024_cap_danse.csv
const filename = process.argv[2]
// csv format
//    0    1       2        3         4        5          6    7     8         9
// title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

const csvEvents = []
const csvToJson = async () => {
  const results = [];

    // Use a promise to handle the asynchronous nature of the stream
    const csvStream = new Promise((resolve, reject) => {
        fs.createReadStream(`csv\\${filename}`)
            .pipe(csv({separator: ';'}))
            .on('data', (data) => results.push(data))
            .on('end', () => resolve(results))
            .on('error', (error) => reject(error));
    });

    return await csvStream;
};


const main = async () => {
  const uids = []
  try {
    const oa = new OaSdk({
      publicKey,
      secretKey,
    });
    // Format csv data into oa events
    const jsonEvents = await csvToJson();
    for (let i = 0; i < jsonEvents.length; i++) {
      // if (i > 0) break // Testing purpose
      
      const event = jsonEvents[i];
      if (!event.location_uid) {
        const OaLocationUid = await getCorrespondingOaLocation(event.location_name)
        event.location_uid = OaLocationUid
      }

      const keywords = event.keyword.split('-');

      const timings = []
    if (moment.tz(event.end_date, TIMEZONE).diff(moment.tz(event.start_date, TIMEZONE), 'hours') < 24) {
      timings.push({
        begin: moment.tz(event.start_date, TIMEZONE).toISOString(),
        end: moment.tz(event.end_date, TIMEZONE).toISOString()
      })
    } else {
      // Split into an array of items that are maximum 24h
      let begin = moment.tz(event.start_date, TIMEZONE)
      const end = moment.tz(event.end_date, TIMEZONE)
      while (begin.isBefore(end)) {
        const endTiming = begin.clone().add(0.5, 'hours')
        timings.push({
          begin: begin.tz(TIMEZONE).format("YYYY-MM-DDTHH:mm:ss.SSSZ"),
          end: endTiming.tz(TIMEZONE).format("YYYY-MM-DDTHH:mm:ss.SSSZ")
        })
        begin = begin.add(1, 'days')
      }
    }

      csvEvents.push({
          "uid-externe": `${filename.split('.')[0]}_${i}`,
          title: event['title'],
          slug: slugify(event['title']),
          description: { fr: event.desc.length > 0 ? event.desc : "-" },
          longDescription: { fr: `${event.long_desc}${event.location_name ? `\n${event.location_name}` : ''}` },
          timings,
          // timings: [
          //   {
          //     begin: event.start_date,
          //     end: event.end_date,
          //   },
          // ],
          locationUid: event.location_uid ?? TBD_LOCATION_UID,
          links: [{ link: event.link, data: { url: event.link } }],
          image: { url: event.img },
          keywords: { fr: keywords },
          onlineAccessLink: event.link,
          attendanceMode: (event.link) ? 3 : 1, // 1 physique, 2 online, 3 mixte
      });
    }
    // Get upcoming events from Open Agenda to check duplicates
    const oaEvents = await axios.get(
      `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/events`,
      {
        params: { 
          key: publicKey,
          monolingual: "fr", "timings[gte]": moment().subtract(1, 'day').format("YYYY-MM-DD:00:00:00.000"), "size": 300 },
        headers: { 
          'Content-Type': 'application/json'
        }
      }
    )

    for (const event of csvEvents) {
      // console.log("event - ", event);
      // Check if an existing oa event is there with the same "uid-externe"
      const oaEvent = oaEvents.data.events.find(e => e["uid-externe"] === event["uid-externe"]);
      if (oaEvent) {
        console.log("Try to update event - ", event['uid-externe'], event.slug, oaEvent.slug);
        const updatedEvent = await updateOaEvent(oa, AGENDA_UID, oaEvent.uid, event)
        console.log("updatedEvent - ", updatedEvent.slug);
        continue;
      } else {
        const createdEvent = await createOaEvent(oa, AGENDA_UID, event)
        console.log("createdEvent - ", `https://openagenda.com/fr/kerlandrier/events/${createdEvent.slug}`);
        uids.push(createdEvent.uid)
      }
    }
  } catch (error) {
    console.error('Error processing CSV:');
    if (error.response && error.response.data) {
      console.error(error.response.data);
    }
  } finally {
    console.log("uids - ", uids);
    fs.writeFile(`csv/${filename.split('.')[0]}.txt`, uids.join('\n'), (err) => {
      if (err) throw err;
      console.log('Log file saved.');
    });
  }
}

main()