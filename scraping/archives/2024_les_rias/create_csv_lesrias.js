const fs = require('fs');
const CsvReadableStream = require('csv-reader');
const AutoDetectDecoderStream = require('autodetect-decoder-stream');

const { slugify } = require('../utils');
require('dotenv').config()
const AGGLO_QUIMPLERLE_LOCATION_UID = "87694536"

const FILE_NAME = "resources/2024_lesrias.csv";
let inputStream = fs.createReadStream(FILE_NAME).pipe(new AutoDetectDecoderStream({ defaultEncoding: '1255' }))

const lesRias = [];

const processCsv = () => {
    return new Promise((resolve, reject) => {
        inputStream
            .pipe(new CsvReadableStream({ parseNumbers: true, parseBooleans: true, trim: true, delimiter: ';' }))
            .on('data', function (row) {
                const dates = row[1].match(/\d{2}\/\d{2}/g);
                console.log(row[2], dates)
                if (dates && dates.length > 0) {
                    dates.forEach((date, idx) => {
                        const day = date.split('/')[0];
                        const month = date.split('/')[1];
                        lesRias.push({
                            "uid-externe": `2024_lesrias_${idx + 1}`,
                            slug: slugify(row[2]),
                            title: row[2],
                            description: { fr: "Les Rias"},
                            locationUid: AGGLO_QUIMPLERLE_LOCATION_UID,
                            longDescription: { fr: row[3] },
                            timings: [
                                {
                                    begin: `2024-${month}-${day}T17:00:00+0200`,
                                    end: `2024-${month}-${day}T22:00:00+0200`,
                                },
                            ],
                            image: {url: row[0]},
                            links: [ {link: "https://www.lesrias.com/programme/"}]
                        });
                    });
                }
            })
            .on('end', function () {
                console.log('Done');
                resolve(lesRias);
            })
            .on('error', function (err) {
                reject(err);
            });
    });
};

const main = async () => {
    try {
        const result = await processCsv();
        console.log('lesRias outside async sequence:', result);
        // You can now use lesRias here
        return result;
    } catch (error) {
        console.error('Error processing CSV:', error);
    }
};

module.exports = { processCsv };