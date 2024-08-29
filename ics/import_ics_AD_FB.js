require('dotenv').config();
const ICS_URL = process.env.ICS_PRIVATE_URL_AD_FB;

const { importIcs } = require('./import_ics');


(async () => {
    await importIcs(ICS_URL);
})();