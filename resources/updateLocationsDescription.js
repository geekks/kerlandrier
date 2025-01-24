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

// Aven
const avenCities=['Bannalec','Beg-Meil','Concarneau','Elliant','LaForêt-Fouesnant','Pleuven',
  'Pont-Aven','Rosporden','Fouesnant','Melgven','Moelansurmer','Moëlan-sur-Mer',
  'Kervaziou','Scaër','Névez','Nizon','Port-la-Forêt','Quimperlé','Saint-Philibert',
  'Saint-Yvi','Tourch','Trégunc','La Forêt-Fouesnant', 'Mellac',
  'Autre' // Pour les lieux inconnus, localisés par défaut à BILBAO
];

const cornouailleCities=['Aber-Wrac\'h','Quimper','Pont-l\'Abbé','Briec','Douarnenez' ,'Penmarc\'h','Lechiagat',
  'Léchiagat','Ergué Gaberic','Ergué-Gabéric','Chateaulin','Châteaulin','Plobannalec',
  'Plobannalec-Lesconil','Pluguffan','Trégornan','Combrit','Île-Tudy','Saint-Goazec',
  'Saint-Brieuc','Plomelin','Clohars-Carnoët','Clohars-Fouesnant','Quéménéven', 'Le Faouët', 'Locronan',
  'Tréguennec', 'Coray', 'Châteauneuf-du-Faou', 'Plomodiern', 'Plouhinec'];

const breizhPostal = ['29', '56', '22', '35']; // Postal code of Bretagne

// TO DO: lowercase + slugify location name for better matching

// https://fr.wikipedia.org/wiki/Pays_de_Bretagne#/media/Fichier:Pays_Bretagne_map.jpg
// http://www.heritaj.bzh/website/image/ir.attachment/4925_2e00c37/datas
(async () => {
  const locationsUrls = []
  await oa.connect();
  const accessToken = await retrieveAccessToken(secretKey)
  const locations = await getLocations(accessToken)
  console.log("Nombre total de lieux: ", locations.length);
  if (locations && locations.length > 1) {
    for (const location of locations) {
      if (location.description.fr) continue
      locationsUrls.push(`"https://openagenda.com/kerlandrier/admin/locations/${location.uid}/edit",`)
      if      (avenCities.includes(location.city)) {
          await  oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "AVEN"} })
          console.log("Lieu: '"+ location.name + "' ajouté dans", "AVEN" )}
      else if (cornouailleCities.includes(location.city))  {
          await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "CORNOUAILLE"} })
          console.log("Lieu: '"+ location.name + "' ajouté dans", "CORNOUAILLE" )
        }
      else if (breizhPostal.includes(location.postalCode.slice(0, 2)))  {
          await oa.locations.patch(AGENDA_UID, location.uid, { description: {fr: "BRETAGNE"} })
          console.log("Lieu: '"+ location.name + "' ajouté dans", "BRETAGNE" )
        }
      else {
        console.log("🔴 Pas de catégorie pour lieu : '"  + location.name + "'" + 
          " .Adresse: " + location.address + ", " + location.city +  ", "  + JSON.stringify(location.description))
        console.log("  -> Ajouter la ville dans un des territoires dans le script: AVEN, CORNOUAILLE, BRETAGNE" )
      }
    }
    fs.writeFile(file='./resources/updateLocationsDescription.log', 
                callback = "[" + locationsUrls.join('\n') + "]",
                function (err) {if (err) return console.log(err)}
              )
  } else {
    console.log("No locations.")
  }
})();