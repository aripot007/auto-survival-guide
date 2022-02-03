# Default output file name
DEFAULT_OUTPUT = "survival_guide.txt"

# How many sentences should the program use to describe each word (wikipedia only for now)
SENTENCES_PER_WORD = 1

# The path to the template file
TEMPLATE_PATH = "template.txt"

# The path to the tesseract OCR command
TESSERACT_CMD = "tesseract"

#############################################
#           Template Placeholders           #
#############################################

TEMPLATE_PLACEHOLDERS = {
    "guide_title": "GUIDE_TITLE",
    "part_start": "PART_START",
    "part_end": "PART_END",
    "part_title": "PART_TITLE",
    "word_start": "WORD_START",
    "word_end": "WORD_END",
    "word_word": "WORD_WORD",
    "word_def": "WORD_DEF"
}
