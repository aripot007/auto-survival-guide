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


ap = argparse.ArgumentParser()
ap.add_argument("file", help="path to guide.json")
ap.add_argument("-m", "--manual", required=False, help="Use manual mode", action="store_true")
ap.add_argument("-s", "--skip-not-found", "--skip", dest="skip-not-found", required=False, help="Skip words with no information found", action="store_true")
ap.add_argument("-o", "--output", required=False, help="output file", default=None)
args = vars(ap.parse_args())

with open(args["file"], "r") as f:
    guide = json.load(f)

titre_guide = escape_latex( guide["title"])
parties = []

for part in guide["parts"]:
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
