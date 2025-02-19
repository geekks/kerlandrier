"""_summary_
Ajoute un classement géographique à tous les lieux ('location') d'OpenAgenda
dans le champ "description". Les catégories sont:
- Aven
- Cornouaille
- Bretagne
Et valide le lieux dans OA ("state": 1 )
Les maigres sources: 
- https://fr.wikipedia.org/wiki/Pays_de_Bretagne#/media/Fichier:Pays_Bretagne_map.jpg
-  http://www.heritaj.bzh/website/image/ir.attachment/4925_2e00c37/datas
"""
import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import json
from HttpRequests import( 
        retrieve_access_token,
        get_locations,
        patch_location,
        )

SECRET_KEY = os.getenv("OA_SECRET_KEY")

aven_cities = [
    "Bannalec", "Beg-Meil", "Concarneau", "Elliant", "LaForêt-Fouesnant", "Pleuven",
    "Pont-Aven", "Rosporden", "Fouesnant", "Melgven", "Moelansurmer", "Moëlan-sur-Mer",
    "Kervaziou", "Scaër", "Névez", "Nizon", "Port-la-Forêt", "Quimperlé", "Saint-Philibert",
    "Saint-Yvi", "Tourch", "Trégunc", "La Forêt-Fouesnant", "Mellac", "Querrien", "Autre"
]

cornouaille_cities = [
    "Aber-Wrac'h", "Quimper", "Pont-l'Abbé", "Briec", "Douarnenez", "Penmarc'h", "Lechiagat",
    "Léchiagat", "Ergué Gaberic", "Ergué-Gabéric", "Chateaulin", "Châteaulin", "Plobannalec",
    "Plobannalec-Lesconil", "Pluguffan", "Trégornan", "Combrit", "Île-Tudy", "Saint-Goazec",
    "Saint-Brieuc", "Plomelin", "Clohars-Carnoët", "Clohars-Fouesnant", "Quéménéven", "Le Faouët", 
    "Locronan", "Tréguennec", "Coray", "Châteauneuf-du-Faou", "Plomodiern", "Plouhinec"
]

breizh_postal = ['29', '56', '22', '35', '44']  # Postal codes of Bretagne and more

access_token = retrieve_access_token(SECRET_KEY)
locations = get_locations(access_token)

print(f"Nombre total de lieux: {len(locations)}")

if locations and len(locations) > 1:
    for location in locations:
        desc = location.get("description").get('fr')
        if desc and desc.upper() in ["AVEN", "CORNOUAILLE", "BRETAGNE"]:
            continue
        
        if location.get("city") in aven_cities:
            patch_location( access_token, location["uid"], {"description": {"fr": "AVEN"}, "state": 1 })
            print(f"Lieu: '{location['name']}' ajouté dans AVEN")
            
        elif location.get("city") in cornouaille_cities:
            patch_location( access_token, location["uid"], {"description": {"fr": "CORNOUAILLE"},"state": 1 })
            print(f"Lieu: '{location['name']}' ajouté dans CORNOUAILLE")
            
        elif location.get("postalCode", "")[:2] in breizh_postal:
            patch_location( access_token, location["uid"], {"description": {"fr": "BRETAGNE"},"state": 1 })
            print(f"Lieu: '{location['name']}' ajouté dans BRETAGNE")
            
        else:
            print(f"🔴 Pas de catégorie pour lieu : '{location['name']}' . Adresse: {location.get('address')}, {location.get('city')}, {json.dumps(location.get('description'))}")
            print("  -> Ajouter la ville dans un des territoires dans le script: AVEN, CORNOUAILLE, BRETAGNE")
    print("Tous les lieux ont été mis à jour.")
else:
    print("No locations.")
