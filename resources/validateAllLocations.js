require('dotenv').config()

const AGENDA_UID = process.env.AGENDA_UID

const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk

const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;

const oa = new OaSdk({
  publicKey,
  secretKey,
});


/**
 * Validates all locations (status =1 ) in the OpenAgenda instance that are in the "to be validated" state.
 *
 * @return {Promise<void>} Resolves when all locations have been validated.
 */
(async () => {
  await oa.connect();
  const locations = await oa.locations.list(AGENDA_UID, { state: 0 });
  // console.log("locations - ", locations);
  if (locations && locations.locations && locations.locations.length > 1) {
    for (const location of locations.locations) {
      if (location.state === 0) {
        await oa.locations.patch(AGENDA_UID, location.uid, { state: 1 });
        console.log("Validated location: ", location.name)
      }
    }
    console.log("Total validated locations: ", locations.locations.length)
  } else {
    console.log("No locations require validation.")
  }
})();