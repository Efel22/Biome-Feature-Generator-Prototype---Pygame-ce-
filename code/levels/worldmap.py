from levels.chunk import *

MAP_SIZE = 5

class Worldmap():
    def __init__(self):
        # Array of Chunks of the world map
        self.Chunks = [[Chunk((-1,-1),"","","") for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        self.levelName = ""

    # This will asign each chunk with its corresponding index in the saved file
    # This will only take place if the file exists
    def load_chunks(self, levelName, instr = "load"):   
        # Change the current directory to 'levels' levelName 'chunks' chunkName 
        # This is supposed to prevent the game from creating an alternate copy of the level outside
        # the 'levels' directory

        # # Define the fixed path to THIS chunk
        # fixed_path = os.path.join('factioncraft', 'levels', levelName, 'chunks')
        # This is the original path in which the code is executing in
        # original_path = os.getcwd()

        # change the path to the fixed one
        # os.chdir(fixed_path)

        self.levelName = levelName
        for row in range(MAP_SIZE):
            for column in range(MAP_SIZE):
                self.Chunks[row][column].assignIndex(row,column)
                self.Chunks[row][column].load(levelName, instr)
                
        # change the path to the ORIGINAL one
        # os.chdir(original_path)

    def getChunk(self, x, y):
        if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
            return self.Chunks[x][y]

    def getChunkData(self, x, y):
        if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
            return self.Chunks[x][y].chunkData
        
    def copyChunkFromFile(self, x, y):
        level_name = self.level_name  # Assuming self.level_name contains the current level's name
        file_path = f"factioncraft/levels/{level_name}/chunks/{x}_{y}.json"
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return None
        
        try:
            with open(file_path, "r") as file:
                chunk_data = json.load(file)
                return chunk_data
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {file_path}.")
            return None

    # Debug
    def print(self):
        for row in range(MAP_SIZE):
            for column in range(MAP_SIZE):
                print(self.Chunks[row][column].index)

# worldmap = Worldmap()
# worldmap.print()
# chunk1 = Chunk((1,1), "generic", "forest")

