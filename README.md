# Kerlandrier

_Le Kerlandrier est un site affiche. Il a vocation à **agréger** et **mettre à disposition** les événements sur le territoire de la CCA (et plus si affinités)._
_Ce dépôt stocke du code utile pour un administrateur du projet. Ce sont essentiellement des aides à la mise à jour du contenu du projet Kerlandrier._

* * *

Le [Kerlandrier](https://kerlandrier.cc/) utilise un [calendrier Openagenda](https://openagenda.com/fr/flux-cca-test) et son [api](https://developers.openagenda.com/00-structure-evenement/) pour générer son contenu à chaque ouverture de la page.

![alt text](/assets/screenshot_1.png)

## Contexte

La **mise à disposition** des événements se veut _numérique_ et _physique_. _Numérique_ via la [page web statique du Kerlandrier](https://hentou.cc/tsts/convivialites/).
_Physique_ via un usage Web2Print qui permet d'imprimer le contenu sur un format papier (A5, A4, A4, A0 pour les plus ambitieux).

L'**agrégation** des événements est l'obstacle principal à la réussite du projet.

### Freins à l'agrégation

*   Sources d'informations multiples:
    + Affichage papier
    + Newsletter de lieux et d'associations
    + Evénements et posts Facebbok
    + Sites Web
    + Bouche à oreille/ Discussions Whatsapp
*   Blocages techniques à l'automatisation:
    + Blocage par Facebook du scrap d'infos sur son contenu
    + Incompatibilités des formats de calendrier ouverts, Google, Apple, ...
    + Pas de solution simple, open source, trouvée pour faire ce travail
*   Temps de contribution manuel
    + [La flemme](https://yewtu.be/watch?v=ZdHupyZIfK0)


## Outils du dépôt

### Import via Google Agenda

*   Importer les événements d'un Google Agenda (`.ical`) à partir de son URL > `import_google_agenda.js`
    + Si aucune complication, l'événement Openagenda est créé et une valeur `uid-externe` est mise à jour
    + Si un événement avec le même `uid-externe` est trouvé dans Openagenda, on fait une mise à jour (à débattre, on pourrait aussi ne rien faire)
    + S'il existe des événements dans la même plage de date, on interagit avec l'administrateur
        - Soit de mettre à jour un événement existant de l'Openagenda (avec l'`uid-externe`)
        - Soit de créer un nouvel événements

### Import via csv

*   Importer les événements d'un csv
*   Template dans `csv/import_csv_template.csv`
*   Création d'un csv :
    +   Option 1 : Créer à la main pour shunter le formulaire OpenAgenda (parce qu'un jour on créera notre solution open-source mais pas aujourd'hui)
    +   Option 2 : Créer via web-scraping 
        - ([Extension Chrome](https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah?pli=1))
        - Scripting JS ou via lib python type `BeautifulSoup`
* Stockage des csv :
    + Stockage des extractions brutes dans le dossier `scraping`
    + Stockage des extractions reformatées au format d'import csv dans le dossier `csv`

### Détermination de `location_uid` via `location_name`

_OpenAgenda oblige à fournir un `location_uid` à la création d'un événement (pour les événements dits physiques)._
_Dans le cadre d'un import Google Agenda (Ga) ou d'un import csv, on ne dispose que d'un `location_name`_
_On expérimente des fonctionnalités pour trouver le lieu dans le base de données OpenAgenda correspondant au nom du lieu trouvé dans la nature._

* `getOaLocations.js`

*   Récupérer tous les lieux OpenAgenda avec `name` et `address`
*   Fuzzy search de l'input (Google Agenda ou csv) sur les lieux Open Agenda
*   Si correspondance avec un bon score, prendre le meilleur score
*   Sinon, créer un nouveau lieu en utilisant le geocoding de l'API OpenAgenda
*   Si le lieu créé n'est pas en Bretagne, emergency rollback de l'extrême

> **TODO:** Apprivoiser `Fuse.js`, sa configuration (`location`, `distance`, `threshold`, `ignoreLocation`... ) et l'interprétation du `score` pour éviter les faux positifs _e.g. "Fuse.js fait matcher `Médiathèque Tourc'h` avec `Médiathèque Tregunc` parce que `Médiathèque Tourc'h` n'existe pas dans OpenAgenda"_

### Import via Google doc

_[TO DO]_

### Evénements récurrents via Google Agenda

_[TO DO]_

### Validation de Lieux

*   Valider tous les [Lieux](https://openagenda.com/flux-cca-test/admin/locations) "à valider" > `validate_locations.js`
    + Pour éviter de devoir le faire via l'UI Openagenda,
    + Ca fait professionnel.

![Validate locations](./assets/validate_locations.png "Menu d'administration des Lieux")

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
$ node import_google_agenda.js
$ node validation_locations.js
$ node csv/import_csv.js name_of_your_file.csv
```

## `import_google_agenda.js`

### Détails sur la résolution des ambigüités

![update](./assets/update.png)\
*Evénement trouvé en auto : Mise à jour auto*

![prompt](./assets/prompt.png)\
*Evénement non trouvé automatiquement dans OA : On interagit avec l'administrateur.*

![Create](./assets/create.png "Create")\
*Evénement non trouvé automatiquement dans OA & l'administrateur souhaite créer l'événement issu de GA* 

![patch](./assets/patch.png)\
*Evénement non trouvé automatiquement dans OA mais l'administrateur l'a trouvé*

## `csv/import_csv.js`

### Format du csv

- OpenAgenda rend obligatoire un lieu (`location_uid`) et un horaire (`start_date`, `end_date`)
    + Par défaut, on utilise un lieu `A DEFINIR` pour simplifier (puis on modifie dans OpenAgenda pour trouver ou créer le lieu, cf. # pour les méthodes plus sioux)
    + Les horaires doivent être au format `YYYY-MM-DDTHH:mm:ss+0200` (+0200 pour le fuseau horaire France)

| title | desc | long_desc | start_date | end_date | location_uid | link | img | keyword | location_name |
|-------|------|-----------|------------|----------|--------------|------|-----|---------|---------------|
|   1   |   2  |     3     |      4     |     5    |      6       |  7   |   8 |    9    |    10         |
|Nom principal|(Très) courte description|Longue description|2024-08-07T19:00:00+0200|2024-08-07T20:30:00+0200|Laisser vide si inconnu|url externe d'info|url image d'illustration|Type d'événement|Lieu format Google Agenda si pas de location uid|

> On construit un `uid-externe` (`filename` + `row_index`) pour éviter les doublons en cas d'update frénétique et incontrôlable.

## `resources/getOaLocation.js`

```javascript
const { getCorrespondingOaLocationFromGa } = require("../resources/getOaLocation")

const main = async () => {
    const OaLocation = await getCorrespondingOaLocationFromGa("your_location_string")
}

main()
```

## Contribuer

Le projet dit oui à votre assistance si vous :

*   Êtes au courant de tous les bons plans du territoire,
*   Remplissez l'[Openagenda](https://openagenda.com/fr/flux-cca-test),
*   Partagez un Google Agenda personnel que vous remplissez consciencieusement d'événements de la CCA et que vous pouvez partager,
*   Scrappez les internets (et surtout les GAFAM) pour en extraire les substantifiques événements,
*   Faites de la spéculation sur le marché du nom de domaine pour inonder les internets de Kerlandrier,
*   Collez des affiches à vos heures perdues.

## Auteurs & remerciements

*   Convivialités Inc.
*   Le Jockey
*   Le [sdk oa](https://github.com/OpenAgenda/oa-public/tree/main/sdk-js)

### Licence

_Pas de licence_
