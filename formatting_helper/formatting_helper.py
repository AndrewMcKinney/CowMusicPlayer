import pathlib


ROOT = pathlib.Path().absolute()
FOLDER_NAME = "formatting_helper"
TEXT_FILE_PATH = ROOT / FOLDER_NAME / "format_me.txt"
OUTPUT_FILE_PATH = ROOT / FOLDER_NAME / "formatted.txt"

#editable constants:
#constants are used in the order they appear
#indicates the number of symbols to remove from the start of each line
REMOVE_FIRST = 0
#removes everything before the first occurance of the character
REMOVE_ALL_BEFORE = "."
#characters to eliminate:
CHAR_TO_ELIMINATE = "( ) . [ ]"
#has Dashes:
HAS_DASHES = False
#time stamps, valid values:  "before" or "after"
TIME_STAMP_LOCATION = "after"




def removeAll(input, x : str):
    return input.replace(x, "")

if(not "format_me.txt"):
    with open(TEXT_FILE_PATH, "w+") as file:
        print("formatting file created")
        exit(0)

with open(TEXT_FILE_PATH, "r") as file:
    with open(OUTPUT_FILE_PATH, "w+") as output:
        for line in file:
            outline = line
            outline = outline[REMOVE_FIRST:]
            outline = outline.strip()
            outline = outline[outline.index(REMOVE_ALL_BEFORE) + 1 :]
            outline = outline.strip()

            for x in CHAR_TO_ELIMINATE.split(" "):
                outline = removeAll(outline, x)
            outline = outline.strip()
            if(not HAS_DASHES):
                if(TIME_STAMP_LOCATION == "after"):
                    insert_location = outline.index(":") - 2
                    outline = outline[:insert_location] + " - " + outline[insert_location:]
                    outline = outline.replace("  ", " ")

                if(TIME_STAMP_LOCATION == "before"):
                    insert_location = outline.rindex(":") + 3
                    outline = outline[:insert_location] + " - " + outline[insert_location:]
                    outline = outline.replace("  ", " ")
                #this inserts a - if there is not one
                
            outline = outline + "\n"
            output.write(outline)


            
            



