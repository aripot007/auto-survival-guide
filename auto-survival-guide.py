import os.path
import re
import json
import argparse
import requests

try:
    from tqdm import tqdm

    use_tqdm = True
except ImportError:
    use_tqdm = False

import settings
from settings import TEMPLATE_PLACEHOLDERS as placeholders

API_SERVER = "https://api.survival-guide.tk/api"


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    cleaned = re.sub(clean, '', text)
    return re.sub(r'\([^)]*\)', '', cleaned).replace("&", "\\&")


def escape_latex(text):
    return text.replace("&", "\\&")


def manual_guide():
    title = escape_latex(input("Titre du guide : "))
    guide_parts = []
    nb_parties = int(input("Nombre de parties : "))
    for i in range(nb_parties):
        part = {}
        part["title"] = input("Titre de la partie {} : ".format(i + 1))
        part["words"] = []
        print("Mots ('FIN' pour terminer)")
        while True:
            word = input()
            if word == "FIN":
                break
            part["words"].append(word)

        print("Sources à utiliser pour cette partie ? (dans l'ordre de préférence, séparées par des espaces)")
        valide = False
        while not valide:
            print("Sources disponibles :")
            print("1: Wikipedia     2: Wiktionary")
            s = input("Sources [1 2]: ")
            if s == "":
                sources = [1, 2]
                valide = True
            else:
                sources = []
                try:
                    for source in s.split():
                        source = int(source)
                        if source < 1 or source > 2:
                            raise Exception
                        sources.append(source)
                    valide = True
                except:
                    print("Source invalide : {}".format(source))
        part["sources"] = sources
        guide_parts.append(part)
    return {"title": title, "parts": guide_parts}


def online_guide(url):
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            print("Could not get the guide from the server : ", resp.status_code)
            exit(1)
        guide = json.loads(resp.text)
    except requests.ConnectionError or IOError as e:
        print("Could not connect to the server :")
        print(e)
        exit(1)

    except json.decoder.JSONDecodeError as e:
        print("Error while decoding the guide :")
        print(e)
        exit(1)

    return guide


def guide_from_server():
    guide_list = None
    try:
        response = requests.get(API_SERVER + "/guides")
        if response.status_code != 200:
            print("Could not get the guide list from the server : ", response.status_code)
            exit(1)
        guide_list = json.loads(response.text)
    except requests.ConnectionError or IOError as e:
        print("Could not connect to the server :")
        print(e)
        exit(1)

    except json.decoder.JSONDecodeError as e:
        print("Error while decoding the guide list :")
        print(e)
        exit(1)

    print("Select a guide : ")
    for i in range(len(guide_list)):
        print("{} : {}".format(i + 1, guide_list[i]["title"]))

    while True:
        try:
            choix = int(input("Choix : ")) - 1
            if choix < 0 or choix >= len(guide_list):
                raise Exception
        except:
            print("Merci d'entrer un choix valide !")
            continue
        break
    return online_guide(API_SERVER + "/guide/" + guide_list[choix]["id"])


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", help="path to guide.json")
ap.add_argument("-l", "--latest", action="store_true", help="Get the latest survival guide from the internet")
ap.add_argument("-t", "--template", help="Path to the template file", default=settings.TEMPLATE_PATH)
ap.add_argument("--json", help="Output the json description of this guide", action="store_true")
ap.add_argument("--test", help="Test run", action="store_true")
ap.add_argument("-n", "--sentences-per-word", dest="sentences-per-word",
                help="How many sentences should be used for a word", default=settings.SENTENCES_PER_WORD)
ap.add_argument("--list", action="store_true", help="Choose from available guides on the server")
ap.add_argument("-m", "--manual", help="Use manual mode", action="store_true")
ap.add_argument("-s", "--skip-not-found", "--skip", dest="skip-not-found", required=False,
                help="Skip words with no information found", action="store_true")
ap.add_argument("-o", "--output", required=False, help="output file", default=settings.DEFAULT_OUTPUT)
args = vars(ap.parse_args())

# Demande le guide manuellement
if args["manual"]:
    guide = manual_guide()

# Lit le guide depuis un fichier ou depuis le web
else:
    if args["list"]:
        guide = guide_from_server()

    elif args["latest"]:
        print("Fetching latest guide from api.survival-guide.tk ...")
        guide = online_guide(API_SERVER + "/guide/latest")

    elif args["test"]:
        guide = {"title": "Test Guide",
                 "parts": [
                     {
                         "title": "Part 1 - Definitions",
                         "words": [
                             "Processor",
                             "Binary"
                         ],
                         "sources": [2, 1]
                     },
                     {
                         "title": "Part 2",
                         "words": ["Hello world"],
                         "sources": [1, 2]
                     }
                 ]
                 }

    elif args["file"] is not None:
        with open(args["file"], "r") as f:
            guide = json.load(f)
    else:
        print("Choisissez le moyen d'obtention du guide : ")
        print("1 : Manuel")
        print("2 : Guide du chapitre en cours")
        print("3 : Choix parmi les guides disponibles sur le server")
        while True:
            try:
                choix = int(input("Choix : "))
                if choix < 1 or choix > 3:
                    raise Exception
            except:
                print("Merci d'entrer un choix valide !")
                continue
            break

        if choix == 1:
            guide = manual_guide()
        elif choix == 2:
            print("Fetching latest guide from api.survival-guide.tk ...")
            guide = online_guide(API_SERVER + "/guide/latest")
        else:
            guide = guide_from_server()

if args["json"]:
    out = "guide.json" if args["output"] == settings.DEFAULT_OUTPUT else args["output"]
    with open(out, "w") as f:
        json.dump(guide, f)
    print("Json guide saved to", out)
    exit(0)

if not os.path.isfile(args["template"]):
    print("Invalid template path !")
    exit(1)

sentence_per_word = int(args["sentences-per-word"])
titre_guide = guide["title"]
parts = guide["parts"]
parties = []
titre_guide = escape_latex(titre_guide)

if use_tqdm:
    nbWords = sum([len(p["words"]) for p in parts])
    progress = tqdm(total=nbWords, desc="Searching words definitions", unit="word")
else:
    print("Searching words definitions ...")
count = 0

for part in parts:
    definitions = {}
    titre_partie = escape_latex(part["title"])
    for word in part["words"]:
        if use_tqdm:
            progress.update()
        trouve = False
        for s in part["sources"]:

            # Wiktionary
            if s == 2:
                try:
                    search = requests.get(
                        "https://en.wiktionary.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&profile=fuzzy&redirects=resolve&search={}".format(
                            word))
                    search_result = json.loads(search.text)
                    page_title = search_result[1][0]
                    url = requests.get("https://en.wiktionary.org/api/rest_v1/page/definition/{}".format(page_title))
                    data = json.loads(url.text)
                    reponse = remove_html_tags(data["en"][0]["definitions"][0]["definition"])
                except:
                    reponse = ""

            # Wikipédia
            elif s == 1:
                # Recherche du mot
                try:
                    search = requests.get(
                        "https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&profile=fuzzy&redirects=resolve&search={}".format(
                            word))
                    search_result = json.loads(search.text)
                    article_title = search_result[1][0]
                    url = requests.get(
                        "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences={}&exlimit=1&explaintext=1&formatversion=2&format=json&titles={}".format(
                            sentence_per_word, article_title))
                    data = json.loads(url.text)
                    reponse = data["query"]["pages"][0]["extract"]
                except:
                    reponse = ""

            else:
                print("\nErreur : source invalide ({}) pour la partie {}".format(s, titre_partie))
                exit(1)

            if reponse != "":
                definitions[word] = reponse
                trouve = True
                break

        if not trouve:
            print("\nAvertissement : le mot '{}' n'a été trouvé dans aucune des sources données.".format(word))
            if not args["skip-not-found"]:
                definition = input("Entrez une définition manuellement pour '{}' ('s' = passer ce mot) : ".format(word))
                if definition.lower() != "s":
                    definitions[word] = definition
        count += 1

    parties.append((titre_partie, definitions))

print("\nGenerating guide ...")

with open(args["template"], "r") as f:
    template = f.read()

template = template.replace(placeholders["guide_title"], titre_guide)

# Get the text corresponding to a part
text_intro, part_template, text_outro = re.findall("(.*)" + placeholders["part_start"] + "(.*)" + placeholders["part_end"] + "(.*)", template, re.RegexFlag.DOTALL)[0]

# Get the text corresponding to a word
word_template = re.findall(placeholders["word_start"] + "(.*)" + placeholders["word_end"], part_template, re.RegexFlag.DOTALL)[0]

output = text_intro
for part in parties:
    title = part[0]
    words = part[1]
    words_text = ""
    for w, d in words.items():
        words_text += word_template.replace(placeholders["word_word"], w).replace(placeholders["word_def"], d)

    text = re.sub(placeholders["word_start"] + "(.*)" + placeholders["word_end"], words_text, part_template, flags=re.RegexFlag.DOTALL)
    text = text.replace(placeholders["part_title"], title)
    output += text

output += text_outro

with open(args["output"], "w") as f:
    f.write(output)

print("Done !")
