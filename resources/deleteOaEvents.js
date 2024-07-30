
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
  53146713, 92983967,
  32577633, 65483785,
  62463049, 16339921,
  35441799, 82894402,
  79725204, 35230048,
  70957177, 55523790
]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()