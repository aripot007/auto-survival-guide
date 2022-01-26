import cv2
import imutils
import os
import json
import argparse
import pytesseract


def get_text(image, box):
    x1, y1, x2, y2 = box
    cropped = image[y1:y1 + y2, x1:x1 + x2]
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    return pytesseract.image_to_string(cropped)


pytesseract.pytesseract.tesseract_cmd = "D:\\Programmes\\Tesseract\\tesseract.exe"

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to the image")
ap.add_argument("-r", "--resize", required=False, help="resize the image", action="store_true")
ap.add_argument("-o", "--output", required=False, help="output file", default=None)
args = vars(ap.parse_args())

img = cv2.imread(args["image"])

if args["resize"]:
    img = imutils.resize(img, width=900)

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

    partsRois.append((partTitleBox, textBoxes))

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

    parts.append({"title": part_title, "words": words})

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
