import json
import os 
from os.path import join 
from random import choices, random
from levels.worldgen_instr import *

# Adjust this to increase each chunk size!   
CHUNK_SIZE = 32

GRO_TILES_FILENAME = 'groundTiles.txt'
OBJ_TILES_FILENAME = 'objectTiles.txt'
ENT_POS_FILENAME = 'entityPositions.txt'
ENT_TYPE_FILENAME = 'entityType.txt'
CHUNK_DATA_FILENAME = 'chunkData.txt'

class Chunk():

    def __init__(self, index, chunkType, biome, levelName):
        # This will be a Touple (E.g: (2, 3), in which x = 2, and y = 3)
        # self.index = index

        # Init the tilemaps
        self.ground_tiles = [[0 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        self.object_tiles = [[0 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]

        # THESE TWO ARRAYS ARE LINKED
        # What this means is that the data for array_1[ 37 ] is the data of entity type array_2[ 37 ]
        self.entity_positions = [[0 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        self.entity_type = [[0 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]

        # This determines if the chunk has already been generated
        # Generated, in this context, means that a chunk has created
        # the environment (trees, grass, etc.).
        self.chunkData = {
            # Index of the chunk, can be returned
            "index": index,
            # Index of the chunk, can be returned
            "levelName": levelName,
            # This determines the chunk type (Generic, Marketplace, Dungeons, Quarry, etc.)
            "chunkType": chunkType,
            # This determines the biome of the chunk
            "biome": biome,
            "hasGenerated": False
        }

    # Updated Load Function
    def load(self, levelName, instr):

        # Update hasGenerated 
        self.chunkData["hasGenerated"] = self.check_chunk_generated(levelName)
        
        # self.chunkData["hasGenerated"] = False

        if self.chunkData["hasGenerated"]:
            
            # Get the path to THIS chunk
            pathToChunk = join('levels', levelName, 'chunks', self.getIndexTypeStr())

            # Create the paths for each type of file (for now, these 3)
            pathToGroundTiles = join(pathToChunk, GRO_TILES_FILENAME)
            pathToObjectTiles = join(pathToChunk, OBJ_TILES_FILENAME)

            pathToChunkData = join(pathToChunk, CHUNK_DATA_FILENAME)
            
            with open(pathToGroundTiles, "r") as chunkFile_gro:
                self.ground_tiles = json.load(chunkFile_gro)

            with open(pathToObjectTiles, "r") as chunkFile_obj:
                self.object_tiles = json.load(chunkFile_obj)

            with open(pathToChunkData, "r") as chunkFile_data:
                self.chunkData = json.load(chunkFile_data)

        else:
            self.generate(levelName, instr)

    # Generate Chunk Tilemaps
    def generate(self, levelName, instr):

        # TODO: Add biome generation (cypress trees for cold biomes, etc.)
        # I added a temporary code for the biome generation

        # List of biomes and their weights
        biomes = ["swamp", "taiga", "forest", "aspen_forest", "dead_forest", "prairie", "desert", "snowy_forest"]
        weights = [1, 1, 1, 1, 1, 1, 1, 1]  # Higher weight means higher probability
        # Randomly select a biome with weights
        biome = choices(biomes, weights=weights, k=1)[0]
        # biome = "" # Debug ONLY
        # This is the temp world size, for now, leave it as an int

        self.chunkData["biome"] = biome
        self.chunkData["chunkType"] = "generic"

        # Temporal chunk tiles arrays
        temp_ground_tiles = [["temperate_grass" for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        temp_object_tiles = [["air" for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]

        # FOREST
        if biome == "forest":

            # GROUND
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "light_dirt", 8, 0, random.randint(3, 6), 50)
            temp_ground_tiles = wrlGen_RandPos(temp_ground_tiles, "water", 32)

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "elm_tree", 0.6, 75)
            temp_object_tiles = wrlGen_Cellular(temp_object_tiles, "elm_tree", chanceOfPlacement=75)
            temp_object_tiles = wrlGen_RandPos(temp_object_tiles, "elm_tree", 32)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 5)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "fallen_log", 5)

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 3, 50, 2)

            # Offset for the paths to generate
            pathOffSet = random.randint(-4, 4)

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "red_mushrooms", 1)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "brown_mushrooms", 1)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "yellow_flowers", 5)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "red_flowers", 5)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "blue_flowers", 5)

        # DESERT
        if biome == "desert":

            # GROUND
            temp_ground_tiles = wrlGen_Chance(temp_ground_tiles, "sand", 100)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "light_dirt", 5, 0, random.randint(1, 3), 15)
            temp_ground_tiles = wrlGen_RandPos(temp_ground_tiles, "water", 16)

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "palm_tree", 0.9, 75, seed = random.randint(-100, 100))
            temp_object_tiles = wrlGen_RandPos(temp_object_tiles, "palm_tree", 12)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 5)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "cactus", 5)

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 3, 50, 2)

            # Offset for the paths to generate
            pathOffSet = random.randint(-8, 8)
            # 

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "small_cactus", 5)

        # ASPEN FOREST
        if biome == "aspen_forest":

            # GROUND
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "light_dirt", 5, 0, random.randint(1, 3), 35)
            temp_ground_tiles = wrlGen_RandPos(temp_ground_tiles, "water", 24)

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "aspen_tree", 0.3, 50)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 5)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "fallen_log", 3)
            temp_object_tiles = wrlGen_RandPos(temp_object_tiles, "aspen_tree", 100)

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 3, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 3, 50, 2)

            # Offset for the paths to generate
            pathOffSet = random.randint(-8, 8)
            # 

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "yellow_flowers", 5)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "red_flowers", 5)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "brown_mushrooms", 5)
        
        # PRAIRIE
        if biome == "prairie":

            # GROUND
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "light_dirt", 6, 0, random.randint(1, 3), 35)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "water", 8, 0, random.randint(1, 2), 90 )

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 10)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "fallen_log", 5)
            temp_object_tiles = wrlGen_RandPos(temp_object_tiles, "elm_tree", random.randint(16, 32))

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 1, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 1, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 1, 50, 2)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 1, 50, 2)

            # Offset for the paths to generate
            pathOffSet = random.randint(-8, 8)

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                1,
                70
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                1,
                70
            )

            offsetOnFlowers = random.randint(-100, 100)

            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "yellow_flowers", 0.75, 50, seed = offsetOnFlowers)
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "red_flowers", 0.75, 50, seed = offsetOnFlowers - 1)
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "blue_flowers", 0.75, 50, seed = offsetOnFlowers - 2)

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "yellow_flowers", 3)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "red_flowers", 3)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "blue_flowers", 3)

        # TAIGA
        if biome == "taiga":

            # GROUND
            temp_ground_tiles = wrlGen_Chance(temp_ground_tiles, "cold_grass", 100)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "light_dirt", 5, 0, random.randint(1, 3), 35)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "water", 8, 0, random.randint(2, 3), 80 )

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "cypress_tree", 0.35, 50)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 8)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "fallen_log", 5)
            temp_object_tiles = wrlGen_RandPos(temp_object_tiles, "cypress_tree", 100)

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 1, 50)

            # Offset for the paths to generate
            pathOffSet = random.randint(-8, 8)
            # 

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "red_mushrooms", 1)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "blue_flowers", 6)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "magenta_mushrooms", 3)
        
        # SNOWY FOREST
        if biome == "snowy_forest":

            # GROUND
            temp_ground_tiles = wrlGen_Chance(temp_ground_tiles, "snowy_grass", 100)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "light_dirt", 5, 0, random.randint(1, 3), 35)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "ice", 8, 0, random.randint(2, 3), 80 )

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "snowy_tree", 0.35, 50)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 8)
            temp_object_tiles = wrlGen_RandPos(temp_object_tiles, "snowy_tree", 100)

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 1, 50)

            # Offset for the paths to generate
            pathOffSet = random.randint(-8, 8)
            # 

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "frozen_flower", 3)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "magenta_mushrooms", 3)

        # DEAD FOREST
        if biome == "dead_forest":

            # GROUND
            temp_ground_tiles = wrlGen_Chance(temp_ground_tiles, "dead_grass", 100)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "light_dirt", 5, 0, random.randint(1, 3), 35)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "water", 8, 0, random.randint(2, 3), 80 )

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "white_dead_tree", 0.45, 50)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 8)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "fallen_log", 1)
            temp_object_tiles = wrlGen_RandPos(temp_object_tiles, "white_dead_tree", 100)

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 1, 50)

            # Offset for the paths to generate
            pathOffSet = random.randint(-8, 8)
            # 

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "magenta_mushrooms", 5)
        
        # SWAMP
        if biome == "swamp":

            # GROUND
            temp_ground_tiles = wrlGen_Chance(temp_ground_tiles, "swamp_grass", 100)
            temp_ground_tiles = wrlGen_SpreadRings(temp_ground_tiles, "water", 8, 0, random.randint(1, 2), 70)
            temp_ground_tiles = wrlGen_PerlinNoise(temp_ground_tiles, "water", 0.65, seed = random.randint(-50, 50), scale=5, octaves=1)

            # OBJECT - SOLID
            temp_object_tiles = wrlGen_PerlinNoise(temp_object_tiles, "willow_tree", 0.35, 80, seed = random.randint(-100, 100))
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "rock", 8)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "fallen_log", 1)

            # OBJECT - NON-SOLID
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "north", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "south", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "east", 2, 1, 50)
            temp_object_tiles = wrlGen_Wall(temp_object_tiles, "air", "west", 2, 1, 50)

            # Offset for the paths to generate
            pathOffSet = random.randint(-8, 8)
            # 

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (0, int(CHUNK_SIZE/2) + pathOffSet),
                (CHUNK_SIZE - 1, int(CHUNK_SIZE/2) + pathOffSet),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Path(
                temp_object_tiles, 
                "air", 
                (int(CHUNK_SIZE/2) + pathOffSet, 0),
                (int(CHUNK_SIZE/2) + pathOffSet, CHUNK_SIZE - 1),
                random.randint(1, 2),
                90
            )

            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "blue_flowers", 7)
            temp_object_tiles = wrlGen_Chance(temp_object_tiles, "cattails", 15)

            temp_object_tiles = wrlGen_MatchingTile(temp_object_tiles, "lily_pad", temp_ground_tiles, "water", 65)
            temp_object_tiles = wrlGen_MatchingTile(temp_object_tiles, "duckweed", temp_ground_tiles, "water", 35)

        # Remove all objects if the tile on the ground is an invalid one (water or ice)
        for row in range(len(temp_ground_tiles)):
            for col in range(len(temp_ground_tiles[row])):
                idToCheck = temp_ground_tiles[row][col]
                if idToCheck == "water" or idToCheck == "ice":
                    idFromObj = temp_object_tiles[row][col]
                    
                    # Check if the object is neither "lily_pad" nor "duckweed"
                    if idFromObj != "lily_pad" and idFromObj != "duckweed":
                        temp_object_tiles[row][col] = "air"

        # Assign the temporal arrays to the current ones
        self.ground_tiles = temp_ground_tiles
        self.object_tiles = temp_object_tiles

        # Entity Tile Creation
        for column in range(CHUNK_SIZE):
            for row in range(CHUNK_SIZE):
                self.entity_positions[column][row] = (128,128)

        
# # # # # EXPLANATION FOR THE pathToUse..if..else
        # I made it so, depending on the instruction, the generate will behave
        # in a different manner, this is to prevent duplicates (weird behavior tbh)
        # from the create files functions, etc.


# # # # # GROUND TILEMAP
        # Construct the full path to the file
        pathToUse = join(levelName, 'chunks', self.getIndexTypeStr(), GRO_TILES_FILENAME)
        if instr == "load":
            pathToUse = join('levels',levelName, 'chunks', self.getIndexTypeStr(), GRO_TILES_FILENAME)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(pathToUse), exist_ok=True)


        # Change the current directory to 'levels' levelName 'chunks' chunkName 
        # This is supposed to prevent the game from creating an alternate copy of the level outside
        # the 'levels' directory
        # Define the fixed path to THIS chunk
        # fixed_path = os.path.join('factioncraft', 'levels', levelName, 'chunks', self.getIndexTypeStr())
        # This is the original path in which the code is executing in
        # original_path = os.getcwd()

        # change the path to the fixed one
        # os.chdir(fixed_path)

        # Write the ground_tiles data to the file
        with open(pathToUse, 'w') as fileToHandle:
            json.dump(self.ground_tiles, fileToHandle, indent=4)


# # # # # OBJECTS TILEMAP
        # Construct the full path to the file
        pathToUse = join(levelName, 'chunks', self.getIndexTypeStr(), OBJ_TILES_FILENAME)
        if instr == "load":
            pathToUse = join('levels',levelName, 'chunks', self.getIndexTypeStr(), OBJ_TILES_FILENAME)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(pathToUse), exist_ok=True)

        # Write the object_tiles data to the file
        with open(pathToUse, 'w') as fileToHandle:
            json.dump(self.object_tiles, fileToHandle, indent=4)


# # # # # ENTITY POSITIONS TILEMAP
        # Construct the full path to the file
        # pathToUse = join('levels',levelName, 'chunks', self.getIndexTypeStr(), ENT_POS_FILENAME)

        # Ensure the directory exists
        # os.makedirs(os.path.dirname(pathToUse), exist_ok=True)

        # Write the object_tiles data to the file
        # with open(pathToUse, 'w') as fileToHandle:
        #     json.dump(self.entity_positions, fileToHandle, indent=4)


# # # # # ENTITY TYPE TILEMAP
        # Construct the full path to the file
        # pathToUse = join('levels',levelName, 'chunks', self.getIndexTypeStr(), ENT_TYPE_FILENAME)

        # Ensure the directory exists
        # os.makedirs(os.path.dirname(pathToUse), exist_ok=True)

        # Write the object_tiles data to the file
        # with open(pathToUse, 'w') as fileToHandle:
        #     json.dump(self.entity_type, fileToHandle, indent=4)

# # # # # OTHER DATA (CREATE A FILE) 

        self.chunkData["hasGenerated"] = True

        pathToUse = join(levelName, 'chunks', self.getIndexTypeStr(), CHUNK_DATA_FILENAME)
        if instr == "load":
            pathToUse = join('levels',levelName, 'chunks', self.getIndexTypeStr(), CHUNK_DATA_FILENAME)

        # Store hasGenerated in chunkdata.txt
        with open(join(pathToUse), 'w') as chunkDataFile:
            json.dump(self.chunkData, chunkDataFile, indent=4)

        
        # # change the path to the ORIGINAL one
        # os.chdir(original_path)

    def check_chunk_generated(self, nameOfTheLevel):
        """
        Check if a chunk has been generated by reading its chunkData.txt file.
        
        Args:
            nameOfTheLevel (str): The name of the level.
            nameOfChunk (str): The name of the chunk.
        
        Returns:
            bool: True if the chunk has been generated, False otherwise.
        """
        # Construct the path to chunkData.txt
        chunk_data_path = join("levels", nameOfTheLevel, "chunks", self.getIndexTypeStr(), "chunkData.txt")
        
        # Check if the file exists
        if not os.path.exists(chunk_data_path):
            print(f"Chunk data file not found: {chunk_data_path}")
            return False
        
        # Load the JSON data from the file
        try:
            with open(chunk_data_path, "r") as file:
                self.chunkData = json.load(file)
        except Exception as e:
            print(f"Error reading chunk data: {e}")
            return False
        
        # Check if the chunk has been generated
        if "hasGenerated" in self.chunkData and self.chunkData["hasGenerated"]:
            # print(f"Chunk '{self.getIndexTypeStr()}' in level '{nameOfTheLevel}' has been generated.")
            return True
        else:
            # print(f"Chunk '{self.getIndexTypeStr()}' in level '{nameOfTheLevel}' has NOT been generated.")
            return False

    # Debug function, has a default "type" var (value="all")
    # that determines what to print
    def print(self, type = "all"):

        if type == "ground" or type == "all":
            for i in range(CHUNK_SIZE):
                for j in range(CHUNK_SIZE):
                    print(self.ground_tiles[i][j])

        if type == "obj" or type == "all":
            for i in range(CHUNK_SIZE):
                for j in range(CHUNK_SIZE):
                    print(self.object_tiles[i][j])

    # Assigns the index received to the chunk (e.g.: assignIndex(31,45) = self.index = (31,45) <- Touple )
    # This can be later used to get back the touple as a string that matches the format of each
    # chunk saving
    def assignIndex(self, index_x, index_y):
        self.chunkData["index"] = (index_x,index_y)
        # self.index = (index_x,index_y)

    # Returns the index with the format "T1_T2" as a string
    def getIndexTypeStr(self):
        return str(self.chunkData["index"][0]) + "_" + str(self.chunkData["index"][1])

    # Returns the index as it is
    def getIndex(self):
        return self.chunkData["index"]  
