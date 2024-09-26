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


// https://fr.wikipedia.org/wiki/Pays_de_Bretagne#/media/Fichier:Pays_Bretagne_map.jpg
(async () => {
  const locationsUrls = []
  await oa.connect();
  const accessToken = await retrieveAccessToken(secretKey)
  const locations = await getLocations(accessToken)
  console.log("locations - ", locations.length);
  if (locations && locations.length > 1) {
    for (const location of locations) {
      if (!location.description) console.log("!!! NO DESCRIPTION !!!", location.name, location.city)
      locationsUrls.push(`"https://openagenda.com/kerlandrier/admin/locations/${location.uid}/edit",`)
      if (location.city === 'Bannalec' ||
      // AVEN
       location.city === 'Beg-Meil' ||
       location.city === 'Concarneau' ||
       location.city === 'Elliant' ||
       location.city === 'La Forêt-Fouesnant' ||
       location.city === 'Pleuven'  ||
       location.city === 'Pont-Aven' ||
       location.city === 'Rosporden' ||
       location.city === 'Fouesnant' ||
       location.city === 'Melgven' ||
       location.city === 'Névez' ||
       location.city === 'Nizon' ||
       location.city === 'Port-la-Forêt' ||
       location.city === 'Quimperlé' ||
       location.city === 'Saint-Philibert' ||
       location.city === 'Saint-Yvi' ||
       location.city === 'Tourch' ||
       location.city === 'Trégunc'
      ) {
        await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "AVEN"} })
      } else if (location.city === 'Aber-Wrac\'h' ||
      // CORNOUAILLE
      location.city === 'Quimper' ||
      location.city === 'Pont-l\'Abbé' ||
      location.city === 'Briec' ||
      location.city === 'Douarnenez'  ||
      location.city === 'Penmarc\'h' ||
      location.city === 'Pluguffan'
    ) {
      await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "CORNOUAILLE"} })
    } else if (location.city === 'Rennes' ||
    // BRETAGNE
    location.city === 'Malestroit' ||
    location.city === 'Quéven' ||
    location.city === 'Malguénac' ||
    location.city === 'Mellionnec' ||
    location.city === 'Brest' ||
    location.city === 'Bréal-sous-Montfort' ||
    location.city === 'La Rochelle' ||
    location.city === 'Lorient') {
      await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "BRETAGNE"} })
      } else {
        console.log("No update", location.name, location.address)
      }
    }
    fs.writeFile('./resources/updateLocationsDescription.txt', "[" + locationsUrls.join('\n') + "]", function (err) {
      if (err) return console.log(err)
    })
  } else {
    console.log("No locations.")
  }
})();