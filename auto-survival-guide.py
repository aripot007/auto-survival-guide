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

API_SERVER = "https://api.survival-guide.tk"

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


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", help="path to guide.json")
ap.add_argument("-l", "--latest", action="store_true", help="Get the latest survival guide from the internet")
ap.add_argument("-t", "--template", help="Path to the template file", default=settings.TEMPLATE_PATH)
ap.add_argument("-n", "--sentences-per-word", help="How many sentences should be used for a word", default=settings.SENTENCES_PER_WORD)
ap.add_argument("--list", action="store_true", help="Choose from available guides on the server")
ap.add_argument("-m", "--manual", help="Use manual mode", action="store_true")
ap.add_argument("-s", "--skip-not-found", "--skip", dest="skip-not-found", required=False, help="Skip words with no information found", action="store_true")
ap.add_argument("-o", "--output", required=False, help="output file", default=settings.DEFAULT_OUTPUT)
args = vars(ap.parse_args())


# Demande le guide manuellement
if args["manual"]:
    guide = manual_guide()

# Lit le guide depuis un fichier ou depuis le web
else:
    if args["list"]:
        print("Work in progress")
        exit(0)
    elif args["latest"]:
        print("Fetching latest guide from api.survival-guide.tk ...")
        try:
            response = requests.get(API_SERVER + "/latest")
            if response.status_code != 200:
                print("Could not get the guide from the server : ", response.status_code)
                exit(1)
            guide = json.loads(response.text)
        except requests.ConnectionError or IOError as e:
            print("Could not connect to the server :")
            print(e)
            exit(1)

        except json.decoder.JSONDecodeError as e:
            print("Error while decoding the guide :")
            print(e)
            exit(1)

    elif args["file"] != "":
        with open(args["file"], "r") as f:
            guide = json.load(f)
    else:
        # Menu de choix
        print("Menu work in progress")
        guide = manual_guide()

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
                    search = requests.get("https://en.wiktionary.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&profile=fuzzy&redirects=resolve&search={}".format(word))
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
                    search = requests.get("https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&profile=fuzzy&redirects=resolve&search={}".format(word))
                    search_result = json.loads(search.text)
                    article_title = search_result[1][0]
                    url = requests.get("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences={}&exlimit=1&explaintext=1&formatversion=2&format=json&titles={}".format(sentence_per_word, article_title))
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


latex = ""

for partie in parties:
    titre = partie[0]
    liste = partie[1]

    latex += "\section*{"+titre+"}\n"
    latex += "\\begin{itemize}\n"

    for mot, definition in liste.items():
        latex += "\item \\textbf{"+mot+"} : {"+definition+"}\n"

    latex += "\end{itemize}\n"

latex += "\end{document}"

template_file = open(args["template"], "r")
template = template_file.read()
template_file.close()

final_file = open(args["output"], "w")
final_file.write(template.replace("TITLE", titre_guide)+latex)
final_file.close()

print("Done !")
