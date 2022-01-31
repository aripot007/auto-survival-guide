# Auto Survival Guide


## Dépendances

Les librairies nécessaires à l'ensemble du projet se trouvent dans le ficher `requirements.txt`, et les dépendances nécessaires uniquement à la génération du survival guide (script `auto-survival-guide.py` uniquement) sont dans `requirements_lite.txt`.

Les dépendances peuvent êtres installées avec la commande ```pip install -r requirements.txt```

## Utilisation

### Paramètres

Les différents paramètres nécessaires au fonctionnement du programme peuvent êtres facilements modifiés dans le fichier `settings.py`.

### Extraction du texte

Pour générer le fichier json contenant le titre et les différentes parties du survival guide, on peut utiliser le script `text-extract.py`.

```bash
text-extract <image_path> [-o output_file]
```

Ensuite, pour sélectionner une zone de l'image, sélectionnez la avec la souris et appuyez sur **[Entree]** pour valider.

Pour chaque partie, il faut sélectionner le titre, puis les zones contenant les mots, en validant avec **[Entree]** à chaque fois, puis **[Echap]** lorsque toutes les zones ont été sélectionnées.
Il faut alors entrer les sources à utiliser pour cette partie, dans l'ordre de préférence et séparées par des espaces. Vous pouvez appuyer sur **[Entree]** pour sélectionner les sources par défaut (Wikipédia puis Wiktionary).

Lorsqu'on a traité toutes les parties, il suffit d'appuyer sur **[C]** à la place de sélectionner un titre, le programme génèrera alors le fichier json correspondant au survival guide.