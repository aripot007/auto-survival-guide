import re
import json
import argparse
import requests


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
    return title, guide_parts


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", help="path to guide.json")
ap.add_argument("-l", "--latest", action="store_true", help="Get the latest survival guide from the internet")
ap.add_argument("--list", action="store_true", help="Choose from available guides on the server")
ap.add_argument("-m", "--manual", help="Use manual mode", action="store_true")
ap.add_argument("-s", "--skip-not-found", "--skip", dest="skip-not-found", required=False, help="Skip words with no information found", action="store_true")
ap.add_argument("-o", "--output", required=False, help="output file", default=None)
args = vars(ap.parse_args())


parts = None
titre_guide = None

# Demande le guide manuellement
if args["manual"]:
    titre_guide, parts = manual_guide()

# Lit le guide depuis un fichier ou depuis le web
else:
    if args["list"]:
        print("Work in progress")
        exit(0)
    elif args["latest"]:
        print("Fetching latest guide from api.survival-guide.tk ...")
        response = requests.get("https://api.survival-guide.tk/latest")
        guide = json.loads(response.text)
        titre_guide = guide["title"]
        parts = guide["parts"]
    elif args["file"] != "":
        with open(args["file"], "r") as f:
            guide = json.load(f)
            titre_guide = guide["title"]
            parts = guide["parts"]
    else:
        # Menu de choix
        print("Menu work in progress")
        titre_guide, parts = manual_guide()

parties = []
titre_guide = escape_latex(titre_guide)

print("Getting words definitions ...")

for part in parts:
    definitions = {}
    titre_partie = escape_latex(part["title"])
    for word in part["words"]:
        trouve = False
        for s in part["sources"]:

            # Wiktionary
            if s == 2:
                url = requests.get("https://en.wiktionary.org/api/rest_v1/page/definition/{}".format(word.lower()))
                data = json.loads(url.text)
                try:
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
                    url = requests.get("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences=1&exlimit=1&explaintext=1&formatversion=2&format=json&titles={}".format(article_title))
                    data = json.loads(url.text)
                    reponse = data["query"]["pages"][0]["extract"]
                except:
                    reponse = ""

            else:
                print("Erreur : source invalide ({}) pour la partie {}".format(s, titre_partie))
                exit(1)

            if reponse != "":
                definitions[word] = reponse
                trouve = True
                break

        if not trouve:
            print("Avertissement : le mot '{}' n'a été trouvé dans aucune des sources données.".format(word))
            if not args["skip-not-found"]:
                definition = input("Entrez une définition manuellement pour '{}' ('s' = passer ce mot) : ".format(word))
                if definition.lower() != "s":
                    definitions[word] = definition

    parties.append((titre_partie, definitions))

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

template_file = open("template.tex", "r")
template = template_file.read()
template_file.close()

final_file = open("survival_guide.tex", "w")
final_file.write(template.replace("TITLE", titre_guide)+latex)
final_file.close()
