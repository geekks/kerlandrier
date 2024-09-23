
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
  36616072, 85629677, 78057516,
  12000660, 43650104, 67225857,
  33749056, 69389396, 12384238,
  91855819, 18965872, 58322128,
  16675325, 57997484, 66872129,
  20445192,  1503668, 71256972,
  93222755
]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()