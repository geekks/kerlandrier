
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
363195,
48052117,
42757749,
52694461,
20292387,
71376219,
23946629,
21152586,
1922072,
72490667,
2130165,
30316475,
30267998,
92835254,
15846626,
57094347,
26212574,
53487155,
81685549,
47971793,
]

const main = async () => {
  await deleteOaEvents(oa, AGENDA_UID, uids)
}

main()