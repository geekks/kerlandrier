
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

const uids = [
  89721514, 25750910, 38531757,
  81696628, 89773403, 38979587,
  10605348, 12466651,  9229408,
  56278689, 79951126, 27164362,
  99314100,  5167500, 19974243,
  25708762, 80988633, 69555136,
  18949548, 54577884, 47343115,
  27560111, 35820481,   185325,
   9836063, 68991050, 49429076,
  77717612, 10670289
]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()