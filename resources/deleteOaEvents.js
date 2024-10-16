
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
  89180288, 70747606,
  38665884,  6387181,
  17223403,  4944233,
  28039707, 77223426,
  57660539
]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()