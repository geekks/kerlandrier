
const fs = require('fs');
const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const moment = require('moment') // for date handling
const axios = require("axios"); // for http requests

const CsvReadableStream = require('csv-reader');
const AutoDetectDecoderStream = require('autodetect-decoder-stream');

const { slugify } = require('../utils');

const { createOaEvent } = require("../utils");

require('dotenv').config()
// OpenAgenda creds
const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const AGENDA_UID = process.env.AGENDA_UID
console.log("AGENDA_UID - ", AGENDA_UID);
const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID

const oa = new OaSdk({
  publicKey,
  secretKey,
});


const filename = process.argv[2]
//    0    1       2        3         4        5          6    7     8
// title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword

const csvEvents = []
const processCsv = () => {
  let inputStream = fs.createReadStream(`csv\\${filename}`).pipe(new AutoDetectDecoderStream({ defaultEncoding: '1255' }))
  let i = 1
  return new Promise((resolve, reject) => {
    inputStream
      .pipe(new CsvReadableStream({ parseNumbers: true, parseBooleans: true, trim: true, delimiter: ';' }))
      .on('data', function (row) {
        console.log("row - ", row);
        csvEvents.push({
          "uid-externe": `csv_${filename.split('.')[0]}_${i}`,
          title: row[0],
          slug: slugify(row[0]),
          description: { fr: row[1] },
          longDescription: { fr: row[2] },
          timings: [
            {
              begin: row[3],
              end: row[4],
            },
          ],
          locationUid: row[5] ?? TBD_LOCATION_UID,
          links: [{ link: row[7] }],
          image: { url: row[7] },
          keywords: { fr: [row[8]] }
        });
      })
      .on('end', function () {
        console.log('Done');
        i++
        resolve(csvEvents);
      })
      .on('error', function (err) {
        i++
        reject(err.data.errors);
      });
  });
};


const main = async () => {
  const uids = []
  try {
    // Format csv data into oa events
    const csvEvents = await processCsv();
    // Get upcoming events from Open Agenda to check duplicates
    const oaEvents = await axios.get(
      `https://api.openagenda.com/v2/agendas/${AGENDA_UID}/events`,
      {
        params: { key: publicKey, monolingual: "fr", "timings[gte]": moment().subtract(1, 'day').format("YYYY-MM-DD:00:00:00.000"), "size": 300 },
        headers: { 'Content-Type': 'application/json' }
      }
    )

    for (const event of csvEvents) {
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
    console.error('Error processing CSV:', error.response.data.errors);
  } finally {
    console.log("uids - ", uids);
    fs.writeFile(`csv/${filename.split('.')[0]}.txt`, uids.join('\n'), (err) => {
      if (err) throw err;
      console.log('Log file saved.');
    });
  }
}

main()