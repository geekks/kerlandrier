# Kerlandrier scripts

_Fourre-tout des outils utilisés pour mise à jour backoffice du OpenAgenda Kerlandrier._

## Outils du dépôt

### Import via ICS (export Google Agenda, Facebook events...)

*   Importer les événements d'un agenda au format `.ical` ou `.ics` (e.g. Google Agenda) à partir de son URL

### Import via csv

*   Importer les événements d'un csv
*   Pour la création du csv :
    +   Option 1 : Créer à la main pour shunter le formulaire OpenAgenda (parce qu'un jour on créera notre solution open-source mais pas aujourd'hui)
    +   Option 2 : Créer via web-scraping 
        - ([Extension Chrome](https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah?pli=1))
        - Scripting JS ou via lib python type `BeautifulSoup`
* Stockage des csv :
    + Stockage des extractions brutes dans le dossier `scraping`
    + Stockage des extractions reformatées au format d'import csv dans le dossier `csv`

> TODO: Faire du scraping industriel en Python pour faire _html > json oa_ et supprimer l'import via csv.

### Validation de Lieux

*   Valider tous les [Lieux](https://openagenda.com/flux-cca-test/admin/locations) "à valider" > `validate_locations.js`
    + Pour éviter de devoir le faire via l'UI Openagenda,
    + Ca fait professionnel.

## Installation

### Installer les librairies
```shell 
$ npm i
```
### Charger les credentials
_Demander à une bonne âme un .env_

Pour les secrets Open Agenda (API pub & secret keys):
*   Créer un compte [Open Agenda](https://openagenda.com/)
*   Récupérer votre clé publique dans les paramètres de votre compte
*   Envoyer une demande à support@openagenda.com pour demander votre clé privée (cf https://developers.openagenda.com/00-introduction/#utilisation-en-criture/)


## Utilisation

```shell
$ node ics/import_ics.js
$ node validation_locations.js
$ node csv/import_csv.js filename.csv
```

## ics/ical : `node ics/import_ics_FB_Kerlandrier.js`

_Script actif qui prend l'URL des events FB auxquels la page FB Kerlandrier a mis `Interested` et qui intéragit avec l'utilisateur pour éviter les doublons._

### Détails sur la résolution des ambigüités

* Événement trouvé en auto _> Mise à jour auto_
* Événement non trouvé automatiquement dans OA _> Interaction avec l'utilisateur_
    * L'administrateur souhaite créer l'événement _> Création nouvel événement OA_
    * L'administrateur a trouvé l'événement dans la liste _> Mise à jour événement OA_

## csv : `node csv/import_csv.js filename.csv`

_Script qui prend un fichier csv et crée une événement par ligne du csv._
_Pas d'interaction avec l'utilisateur, soit on trouve un `uid-externe` identique et on update, soit on crée._

### Format du csv

- OpenAgenda rend obligatoire un lieu (`location_uid`) et un horaire (`start_date`, `end_date`)
    + Par défaut, on utilise un lieu `A DEFINIR` pour simplifier (puis on modifie dans OpenAgenda pour trouver ou créer le lieu, cf. [ici](#resources-getOaLocationjs) pour les méthodes plus sioux)
    + Les horaires doivent être au format `YYYY-MM-DDTHH:mm:ss+0200` (+0200 pour le fuseau horaire France)

| title | desc | long_desc | start_date | end_date | location_uid | link | img | keyword | location_name | book_link |
|-------|------|-----------|------------|----------|--------------|------|-----|---------|---------------|-----------|
|   1   |   2  |     3     |      4     |     5    |      6       |  7   |   8 |    9    |    10         |     11    |
|Nom principal|(Très) courte description|Longue description|2024-08-07T19:00:00+0200|2024-08-07T20:30:00+0200|Laisser vide si inconnu|url externe d'info|url image d'illustration|Type d'événement|Lieu format Google Agenda si pas de location uid|Lien d'inscription|

> On construit un `uid-externe` (`filename` + `row_index`) pour éviter les doublons en cas d'update frénétique et incontrôlable (peu probable parce que c'est déjà chiant de le faire une fois).

## `resources/getOaLocation.js`

_Fonction qui prend une nom de lieu et qui trouve une correspondance ou crée le lieu si possible._


```javascript
const { getCorrespondingOaLocation } = require("../resources/getOaLocation")

const main = async () => {
    const OaLocation = await getCorrespondingOaLocation("your_location_string")
}

main()
```
