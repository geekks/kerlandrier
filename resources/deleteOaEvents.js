
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

const uids = [ 20298008, 23417707, 46873428, 38991016, 11517693, 99815747 ]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()