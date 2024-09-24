require('dotenv').config()
const fs = require('fs');
const AGENDA_UID = process.env.AGENDA_UID

const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const { retrieveAccessToken, getLocations } = require("./manualHttpRequests")

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
  const locationsUrls = []
  await oa.connect();
  const accessToken = await retrieveAccessToken(secretKey)
  const locations = await getLocations(accessToken)
  console.log("locations - ", locations.length);
  if (locations && locations.length > 1) {
    for (const location of locations) {
      locationsUrls.push(`"https://openagenda.com/kerlandrier/admin/locations/${location.uid}/edit",`)
      if (location.city.includes('Bannalec') || location.city.includes('Beg-Meil') || location.city.includes('Concarneau') || location.city.includes('Elliant') || location.city.includes('La Forêt-Fouesnant') || location.city.includes('Pleuven') || location.city.includes('Pluguffan') || location.city.includes('Pont-Aven') || location.city.includes('Pont-l\'Abbé') || location.city.includes('Quéven') || location.city.includes('Rosporden') || location.city.includes('Fouesnant') || location.city.includes('Melgven') || location.city.includes('Névez') || location.city.includes('Nizon') || location.city.includes('Port-la-Forêt') || location.city.includes('Quimper') || location.city.includes('Quimperlé') || location.city.includes('Saint-Philibert') || location.city.includes('Saint-Yvi') || location.city.includes('Tourch') || location.city.includes('Trégunc')
      ) {
        // CCA
        await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "CCA"} })
      } else if (location.city.includes('Aber-Wrac\'h') || location.city.includes('Brest') || location.city.includes('Briec') || location.city.includes('Douarnenez') || location.city.includes('La Rochelle') || location.city.includes('Lorient') || location.city.includes('Malestroit') || location.city.includes('Malguénac') || location.city.includes('Mellionnec') || location.city.includes('Penmarc\'h')
      ) {
        // FINISTERE
        await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "FINISTERE"} })
      } else if (location.city.includes('Rennes') || location.city.includes('Bréal-sous-Montfort')) {
        // BRETAGNE
        await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "BRETAGNE"} })
      } else {
        console.log("No update", location.name, location.address)
      }
    }
    fs.writeFile('./resources/listLocationUrls.txt', "[" + locationsUrls.join('\n') + "]", function (err) {
      if (err) return console.log(err)
    })
  } else {
    console.log("No locations.")
  }
})();