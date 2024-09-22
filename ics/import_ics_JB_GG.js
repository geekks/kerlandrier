require('dotenv').config();
const ICS_URL = process.env.GA_PRIVATE_URL_JB;

const { importIcs } = require('./import_ics');


(async () => {
    await importIcs(ICS_URL);
})();