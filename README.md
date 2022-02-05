# Auto Survival Guide


## Dépendances

Les librairies nécessaires à l'ensemble du projet se trouvent dans le ficher `requirements.txt`, et les dépendances nécessaires uniquement à la génération du survival guide (script `auto-survival-guide.py` uniquement) sont dans `requirements_lite.txt`.

Les dépendances peuvent êtres installées avec la commande ```pip install -r requirements.txt```

## Utilisation

### Paramètres

Les différents paramètres nécessaires au fonctionnement du programme peuvent êtres facilements modifiés dans le fichier `settings.py`.


Les mots-clés utilisés dans la template peuvent également êtres modifiés ici

### Extraction du texte

Pour générer le fichier json contenant le titre et les différentes parties du survival guide, on peut utiliser le script `text-extract.py`.

```bash
text-extract <image_path> [-o output_file]
```

Ensuite, pour sélectionner une zone de l'image, sélectionnez la avec la souris et appuyez sur **[Entree]** pour valider.

Pour chaque partie, il faut sélectionner le titre, puis les zones contenant les mots, en validant avec **[Entree]** à chaque fois, puis **[Echap]** lorsque toutes les zones ont été sélectionnées.
Il faut alors entrer les sources à utiliser pour cette partie, dans l'ordre de préférence et séparées par des espaces. Vous pouvez appuyer sur **[Entree]** pour sélectionner les sources par défaut (Wikipédia puis Wiktionary).

Lorsqu'on a traité toutes les parties, il suffit d'appuyer sur **[C]** à la place de sélectionner un titre, le programme génèrera alors le fichier json correspondant au survival guide.


### Génération du guide

Le guide est généré depuis un fichier json contenant une description du guide. Ce fichier peut être spécifié manuellement (via l'option `-f`), ou peut être téléchargé depuis le serveur.
Il est également possible de rentrer manuellement le guide avec l'option `--manual` (ou `-m`).


Pour télécharger un guide depuis le serveur, vous pouvez utiliser l'option `--latest` (ou `-l`) pour télécharger le guide le plus récent, ou l'option `--list` pour choisir dans la liste de ceux disponibles.


Vous pouvez spécifier un nom de fichier de sortie avec l'option `-o`.


Vous pouvez également obtenir la liste des arguments disponibes avec  `--help`.

#### Exemples :
Génération du guide le plus récent : 
```commandline
auto-survival-guide -l -o guide.txt
```

### Template

La structure du fichier de template doit respecter un minimum de critères :
* Il doit y avoir exactement une balise de début puis de fin de partie dans le fichier, et entre ces deux balises exactement une balise de début puis de fin de mot.
* Le nom d'une balise ne doit pas être inclus dans le nom d'une autre, par exemple `TITLE` pour le titre du guide et `PART_TITLE` pour le titre d'une partie ne marchera pas.
* **TOUS** les caractères compris entre deux balises seront pris en compte, **y compris les retours à la ligne**. Si vous voulez éviter des sauts de lignes inutiles, vous pouvez coller les balises sans problème (vous pouvez regarder comment le fichier `template.txt` est fait)

Vous pouvez changer le nom du fichier de template par défaut dans le fichier `settings.py`, ou spécifier un fichier à utiliser lors de l'exécution avec l'option `--template`.