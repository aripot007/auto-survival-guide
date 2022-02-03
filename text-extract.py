import cv2
import imutils
import os
import json
import argparse
import pytesseract
import settings


def get_text(image, box):
    x1, y1, x2, y2 = box
    cropped = image[y1:y1 + y2, x1:x1 + x2]
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    return pytesseract.image_to_string(cropped)


pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

ap = argparse.ArgumentParser()
ap.add_argument("image", help="path to the image")
ap.add_argument("-r", "--resize", required=False, help="resize the image", default="900")
ap.add_argument("-o", "--output", required=False, help="output file", default=None)
args = vars(ap.parse_args())

img = cv2.imread(args["image"])

if args["resize"]:
    img = imutils.resize(img, width=int(args["resize"]))

# Sélection des zones de texte
titleBox = cv2.selectROI("Select the title", img, False)
cv2.destroyWindow("Select the title")

partsRois = []
while True:
    partTitleBox = cv2.selectROI("Select the part title or press c to cancel", img, False)
    cv2.destroyWindow("Select the part title or press c to cancel")
    
    if partTitleBox == (0, 0, 0, 0):
        break

    print("Select one ore more areas of text (Enter to confirm, esc when done)")
    textBoxes = cv2.selectROIs("Select text areas", img, False)
    cv2.destroyAllWindows()

    # Ask for the sources
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

    partsRois.append((partTitleBox, textBoxes, sources))

# extract the title
title = get_text(img, titleBox).strip()
parts = []
for p in partsRois:
    part_title = get_text(img, p[0]).strip()
    words = []
    for word_box in p[1]:
        words += get_text(img, word_box).split("\n")

    # Remove empty strings
    words = list(filter(lambda s: s != "", words))

    # Ask for sources

    parts.append({"title": part_title, "words": words, "sources": p[2]})

filename = args["output"]
if filename is None:
    filename = "guide.json"
    i = 0
    while os.path.isfile(filename):
        i += 1
        filename = "guide-{}.json".format(i)

guide = {
    "title": title,
    "parts": parts
}

with open(filename, "w+") as file:
    json.dump(guide, file)
