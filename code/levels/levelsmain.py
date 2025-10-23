import os
from os.path import join
from datetime import datetime
from levels.worldmap import *
from levels.levelname_registry import *

class LevelCreator():
    def __init__(self, index, levelName=""):
        
        # This dictionary is going to be used
        # to store the data in the level files
        self.levelData = {
            "name": "",
            "index": index,
            "last_time_played": " Never played!"
            # "last_time_played": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        }

        self.setLevelName(levelName)

        self.worldmap = Worldmap()

    # Sets thie level's name to be a random one if levelName == "" 
    # else, sets the levelName to be the level's name :D
    def setLevelName(self, levelName):
        if levelName == "":
            # Note: Currently, there is no way to detect whether a level name
            # is repeated or not, idk if i'll add this because the chance is 
            # really low so i'll think about it if its worth the time :/ .

            # Randomly select one word from each set
            first_word = choice(list(levelNameDict["first"]))
            second_word = choice(list(levelNameDict["second"]))
            third_word = choice(list(levelNameDict["third"]))
            
            # Combine the words into a level name
            space = " "
            self.levelData["name"] = first_word + space + second_word + space + third_word
        else:
            self.levelData["name"] = levelName

    # Loads the worldmap according to the level name :D
    def loadWorldMap(self, instr = "load"):
        self.worldmap.load_chunks(self.levelData["name"], instr)

    # Creates the files and directories for the chunks and other data 
    # to be stored.
    def create_files(self):
        # Check if the level name is "" <- Default One :/
        # If it is, then generate a random level name
        if self.levelData["name"] == "":
            self.setLevelName("")

# # # # Create the directories # # # # # # # # # # # # #
 
        # Create Level Folder
        os.chdir('levels')
        os.mkdir(self.levelData["name"])
                    
# # # # # Non Folder Files # # # # # # # # # # # # #

        # Create the level data file
        levelData_path = os.path.join(self.levelData["name"], 'leveldata.txt')

        # print(pathToTLevel)
        with open(levelData_path, 'w') as fileCreated:
            json.dump(self.levelData, fileCreated, indent=4)



