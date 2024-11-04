
const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk

const { deleteOaEvents } = require("../utils");

require('dotenv').config()
// OpenAgenda creds
const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;
const AGENDA_UID = process.env.AGENDA_UID

const oa = new OaSdk({
  publicKey,
  secretKey,
});

const uids = [ 1361565, 21079772,
  36377526, 75909901,
  78571784, 70656147,
  80282272, 31019438,
  67743786,  7702025,
  44329178 ]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()