
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
  23395633, 20483924,  6567740,
  13321203, 70657071, 61028802,
  34589373,  6464032, 15785218,
  70391021, 88076927,  2933442,
   9210767, 59952443,  9777182,
  96818449,  9747451,  8856150,
  32473166, 96152659
]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()