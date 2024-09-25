require('dotenv').config()
const fs = require('fs');
const AGENDA_UID = process.env.AGENDA_UID

const { OaSdk } = require('@openagenda/sdk-js') // OpenAgenda Sdk
const { retrieveAccessToken, getLocations } = require("./manualHttpRequests")

const publicKey = process.env.OA_PUBLIC_KEY;
const secretKey = process.env.OA_SECRET_KEY;

// const oa = new OaSdk({
//   publicKey,
//   secretKey,
// });


// https://fr.wikipedia.org/wiki/Pays_de_Bretagne#/media/Fichier:Pays_Bretagne_map.jpg
(async () => {
  const locationsUrls = []
  await oa.connect();
  const accessToken = await retrieveAccessToken(secretKey)
  const locations = await getLocations(accessToken)
  console.log("locations - ", locations.length);
  if (locations && locations.length > 1) {
    for (const location of locations) {
      locationsUrls.push(`"https://openagenda.com/kerlandrier/admin/locations/${location.uid}/edit",`)
      if (location.city.includes('Bannalec') ||
      // AVEN
       location.city.includes('Beg-Meil') ||
       location.city.includes('Concarneau') ||
       location.city.includes('Elliant') ||
       location.city.includes('La Forêt-Fouesnant') ||
       location.city.includes('Pleuven')  ||
       location.city.includes('Pont-Aven') ||
       location.city.includes('Rosporden') ||
       location.city.includes('Fouesnant') ||
       location.city.includes('Melgven') ||
       location.city.includes('Névez') ||
       location.city.includes('Nizon') ||
       location.city.includes('Port-la-Forêt') ||
       location.city.includes('Quimper') ||
       location.city.includes('Quimperlé') ||
       location.city.includes('Saint-Philibert') ||
       location.city.includes('Saint-Yvi') ||
       location.city.includes('Tourch') ||
       location.city.includes('Trégunc')
      ) {
        await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "AVEN"} })
        console.log("Aven", location.name, location.city)
      } else if (location.city.includes('Aber-Wrac\'h') ||
      // CORNOUAILLE
      location.city.includes('Pont-l\'Abbé') ||
      location.city.includes('Briec') ||
      location.city.includes('Douarnenez')  ||
      location.city.includes('Penmarc\'h') ||
      location.city.includes('Pluguffan')
    ) {
      await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "CORNOUAILLE"} })
      console.log("Cornouaille", location.name, location.city)
    } else if (location.city.includes('Rennes') ||
    // BRETAGNE
    location.city.includes('Malestroit') ||
    location.city.includes('Quéven') ||
    location.city.includes('Malguénac') ||
    location.city.includes('Mellionnec') ||
    location.city.includes('Brest') ||
    location.city.includes('Bréal-sous-Montfort') ||
    location.city.includes('La Rochelle') ||
    location.city.includes('Lorient')) {
      await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "BRETAGNE"} })
      console.log("Bretagne", location.name, location.city)
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