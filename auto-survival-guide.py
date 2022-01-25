import re
import json
import requests

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    cleaned = re.sub(clean, '', text)
    return re.sub(r'\([^)]*\)', '', cleaned)

titre_guide = input("Titre du guide ?\n")
nb_parties = int(input("Nombre de parties ?\n"))

parties = []

for i in range(nb_parties):
    definitions = {}
    titre_partie = input("Titre de la {}e partie ?\n".format(i+1))
    print("Veuillez saisir les mots/expressions que vous désirez, FIN pour passer à la partie suivante")
    fin = False

    while not fin:
        mots = input("")
        if "FIN" in mots:
            fin = True
        elif " DEF" in mots:
            mots = mots.replace(" DEF", "")
            url = requests.get("https://en.wiktionary.org/api/rest_v1/page/definition/{}".format(mots))
            data = json.loads(url.text)
            try:
                reponse = remove_html_tags(data["en"][0]["definitions"][0]["definition"])
            except:
                reponse = ""
        else:
            url = requests.get("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences=1&exlimit=1&titles={}&explaintext=1&formatversion=2&format=json".format(mots))
            data = json.loads(url.text)
            try:
                reponse = data["query"]["pages"][0]["extract"]
            except:
                reponse = ""

        if reponse == "" and fin == False:
            print("Pas trouvé !")
        elif fin == False:
            print("Trouvé !")
            definitions[mots] = reponse

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
