"""
Get informations from an event poster
"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import base64
from mistralai import Mistral
from pprint import pprint
from pydantic import BaseModel
import argparse
from PIL import Image
from utils import showDiff



MISTRAL_PRIVATE_API_KEY = os.getenv("MISTRAL_PRIVATE_API_KEY")

# Define a class to contain the Mistral answer to a formatted JSON
class Event(BaseModel):
    titre: str
    date_debut: str
    heure_debut: str
    duree: str
    lieu: str
    description: str
    description_courte: str

# Encode the image to post on mistral
def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

def getMistralImageEvent(image_path:str)->Event:

    try:
        Image.open(image_path).verify()
    except Exception as e:
        print(f"❕ Image {image_path} is not valid image file")
        print(f"{e}")
        exit(1)
        
    base64_image = encode_image(image_path)
    model = "pixtral-12b-2409"
    client = Mistral(api_key=MISTRAL_PRIVATE_API_KEY)

    # Define the messages for the chat
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Cette image est une affiche donnant des informations sur un évènement qui a lieu dans les prochains mois de cette année.\
                    Retourne moi un objet JSON contenant les information suivantes:\
                    titre,\
                    date_debut (date de début au format ISO, sur le fuseau horaire de Paris, dans l'année 2025),\
                    heure_debut (heure de début au format hh:mm),\
                    duree (durée de l'évenementau format hh:mm, avec 0 en durée par défaut si la durée n'est pas indisquée sur l'affiche),\
                    lieu (le nom du lieu ou l'adresse du lieu),\
                    description (les apostrophes sont notées avec le caractère ’ et pas '),\
                    description_courte (un résumé de l'évènement en 1 phrase)"
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}" 
                }
            ]
        }
    ]

    chat_response = client.chat.parse(
        model=model,
        messages=messages,
        response_format=Event
    )

    return chat_response.choices[0].message.parsed


if __name__ == "__main__":
    from wasabi import color,msg
    
    TEST_FILE_NAME = "TEST_temps_foret.jpg"
    # string or list of string that must be present in the answer
    TEST_FILE_ANSWER = {"date_debut": "2025-01-31T20:00:00+01:00",
                        "description": [
                                        "Ce documentaire nous promène",
                                        "Morvan",
                                        "Landes ",
                                        "la forêt des Vosges ou l’Est de la France",
                                        "propriétaires", 
                                        "bûcherons", 
                                        "conducteurs d’engins forestiers",
                                        "patrons de scieries",
                                        "fonctionnaires de l’ONF",
                                        "patrimoine forestier",
                                        "l’État"
                                        ],
                        "description_courte": "Documentaire sur l'exploitation forestière en France",
                        "duree": "0",
                        "heure_debut": "20:00",
                        "lieu": "Cinéville de CONCARNEAU",
                        "titre": "Le Temps des forêts"}
    
    parser=argparse.ArgumentParser()
    parser.add_argument("-f", "--fileName",help="Image file name in images/sources path ")
    parser.add_argument("test",help="Test command with {TEST_FILE_NAME}")
    args=parser.parse_args()
    
    if args.fileName:
        image_path = os.path.join(git_root, "images/sources", args.fileName )
        if not os.path.isfile(image_path):
            raise argparse.ArgumentTypeError(f"Given image path ({image_path}) is not valid")
        response=getMistralImageEvent(image_path)
        response_json = response.model_dump(mode='json')
        print("Mistral answer:")
        pprint(response_json)
        
    elif args.test:
        image_path = os.path.join(git_root, "images/sources", TEST_FILE_NAME)
        # send request to mistral
        response=getMistralImageEvent(image_path)
        response_json = response.model_dump(mode='json')
        error=0
        for key in response_json:
            testPhrase=TEST_FILE_ANSWER.get(key)
            answerPhrase=response_json.get(key)
            # test value is a string
            if ( isinstance(testPhrase, str) and testPhrase.lower() not in str(answerPhrase).lower()):
                msg.fail(f"Test failed for:{key}")
                msg.info("Differences in answer vs expected:")
                print( showDiff(str(TEST_FILE_ANSWER.get(key)),
                                str(response_json.get(key))))
                error+=1
            # test values are an array of string (made dor long text like "description")
            if isinstance(testPhrase, list):
                for phrase in  TEST_FILE_ANSWER.get(key):
                    if str(phrase).lower() not in str(response_json.get(key)).lower():
                        msg.fail(f"Test failed for:{key}")
                        msg.info(f"Phrase {color(str(phrase), fg=120)} {color("not found in answer:", fg=4)} \
                                {color(str(response_json.get(key)), fg=80)}",
                                spaced = False
                                )
                        error+=1

        if error == 0:
            msg.good(f"Test passed for all keys !")
        else:
            msg.warn(f"Test failed for {error} keys")
        
    else:
        print(f"❕ Please give a valid file name")
        exit(1)

    exit(0)