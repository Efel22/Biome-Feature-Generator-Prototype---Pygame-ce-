from settings import *
from graphics.player import Player
from graphics.sprites import *
from pytmx.util_pygame import load_pygame
from graphics.groups import AllSprites
from graphics.tiles import *
import time

from levels.levelsmain import *

from gui.button import *

from random import random, choices


PATH_IMG = join('assets', 'images')
PATH_AUDIO = join('assets', 'audio')

UP, DOWN, LEFT, RIGHT = "up", "down", "left", "right"

class Game_2:
    def __init__(self, worldindex, levelName, screen):

        # setup
        pygame.init()
        self.display_surface = screen
        self.clock = pygame.time.Clock()

        # Used to determine whether to change chunks or not
        self.running = True

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()

        # index of the world 
        self.index = worldindex
        # print("World Index:" + str(self.index) ) # Debug

        # level name, get it based on the world index (TODO: Add this functionality)
        self.levelName = levelName
        # print("Found level name:" + str(self.levelName) ) # Debug

        # current worldmap (TODO: get the worldmap based on the name)
        self.currentWorld = Worldmap()
        self.currentWorld.load_chunks(self.levelName)
        # print("Found worldmap") # Debug

        # player's position on the world based on the chunk (3,3) this should be the middle
        # of the world, on chunk 3, 3
        self.player_ChunkPos_on_world = [0,0]

        self.ingame_player_world_position = [0,0]
        self.future_world_pos = [CHUNK_SIZE/2,CHUNK_SIZE/2]
        self.last_available_dirs = []

        # setup
        # self.setup()

        # Music# Start playing the Startup Music
        self.music = pygame.mixer.Sound(join('assets','audio','music','combat1.mp3'))
        self.music.set_volume(0.5)

        # Timer for the update of each animated tile
        self.timerData_updateAnimTiles = {
            "delay": 500,
            "last_time": pygame.time.get_ticks(),
            "current_time": 0
        }

        # Timer for the update of the animated background
        self.timerData_updateBackground = {
            "delay": 1000,
            "last_time": pygame.time.get_ticks(),
            "current_time": 0
        }

        # Timer for the update of the animated background
        self.timerData_updateEntityFrames = {
            "delay": 200,
            "last_time": pygame.time.get_ticks(),
            "current_time": 0
        }

        self.load_images()

    # Load the images so the game doesn't lag
    def load_images(self):

        self.textures = {
            "LOADING_BG": pygame.image.load(join('assets', 'images', 'gui', 'loading_bg.png')),
            "BACK_BUTTON_IMG": pygame.image.load(join('assets', 'images', 'gui', 'back_button.png')),
            "BACK_BUTTON_HOVER_IMG": pygame.image.load(join('assets', 'images', 'gui', 'back_button_hover.png'))
        }

    # Removes all sprites from the game
    def reset(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.enemy_sprites.empty()

    # This function checks if the player is outside of the 
    def isPlayerOutOfWorldBound(self):

        # Get the player position (x and y)
        player_x = self.player.wrlpos.x
        player_y = self.player.wrlpos.y

        # Check if (both) VALUE is less than 0 or greater than the chunk size
        if player_x < 0 or player_x > CHUNK_SIZE or player_y < 0 or player_y > CHUNK_SIZE:
            return True

        # Return false 
        return False
    
    def getDirPlayerCanMoveTo(self):

        # Copy of the player_ChunkPos_on_world
        playerChunkPos_Y = self.player_ChunkPos_on_world[1] 
        playerChunkPos_X = self.player_ChunkPos_on_world[0] 

        print("playerChunkPos_X" + str(playerChunkPos_X))
        print("playerChunkPos_Y" + str(playerChunkPos_Y))
        
        # Create a list to store valid directions
        dirs_List = []

        # Check Y-axis (up and down)
        if playerChunkPos_Y > 0:  # Can move up if not at the top edge
            dirs_List.append("up")
        if playerChunkPos_Y < (MAP_SIZE - 1):  # Can move down if not at the bottom edge
            dirs_List.append("down")

        # Check X-axis (left and right)
        if playerChunkPos_X > 0:  # Can move left if not at the left edge
            dirs_List.append("left")
        if playerChunkPos_X < (MAP_SIZE - 1):  # Can move right if not at the right edge
            dirs_List.append("right")
        
        dirs_ToRemoveFromOg = self.getListDirectionsCannotMove()

        # Remove values from List1 that are in List2
        for value in dirs_ToRemoveFromOg:
            while value in dirs_List:
                dirs_List.remove(value)

        # Return the list of directions to return 
        return dirs_List

    # Checks if the chunk player is in is a "border" chunk
    def getListDirectionsCannotMove(self):

        # Copy of the player_ChunkPos_on_world
        playerChunkPos_X = self.player_ChunkPos_on_world[0] 
        playerChunkPos_Y = self.player_ChunkPos_on_world[1] 

        # Create a counter list that will be used to remove
        # values from a list of directions
        # E.g: 
        # --> dirsCanMove = ["left", "down"]
        # --> borderDirs = ["left", "up"]
        # --> dirsCanMove = ["down"] 
        borderDirs = []

        if playerChunkPos_X <= 0:
            borderDirs.append("left")
        
        if playerChunkPos_X >= MAP_SIZE - 1:
            borderDirs.append("right")

        if playerChunkPos_Y <= 0:
            borderDirs.append("up")
        
        if playerChunkPos_Y >= MAP_SIZE - 1:
            borderDirs.append("down")
        
        return borderDirs
    
    # Returns a string with the direction of where the player
    # should move to in terms of chunks
    def getDirectionOfChunkMove(self):
        
        direction = ""

        # Get the player position (x and y)
        player_x = self.player.wrlpos.x
        player_y = self.player.wrlpos.y

        if player_x < 0:
            direction = "left"

        if player_x >= CHUNK_SIZE:
            direction = "right"

        if player_y < 0:
            direction = "up"

        if player_y >= CHUNK_SIZE:
            direction = "down"

        print("getDir() = " + direction)
        return direction

    # Create a tile based on the id on x and y 
    def tileCreate(self, nameOfTile, i, j):

        # BORDER
        if (nameOfTile == "border_fog"):
            # Tile("border_fog", (i,j), (self.all_sprites, self.collision_sprites), "obj")
            Tile("border_fog", (i,j), (self.all_sprites), "obj")
        if (nameOfTile == "barrier_air"):
            Tile("barrier_air", (i,j), (self.all_sprites, self.collision_sprites), "obj")
        

        # GROUND (non water)
        if (nameOfTile == "temperate_grass"):
            createVariationTile(["temperate_grass_0","temperate_grass_1","temperate_grass_2"], (i,j), self.all_sprites, "ground")
        
        if (nameOfTile == "cold_grass"):
            createVariationTile(["cold_grass_0","cold_grass_1","cold_grass_2"], (i,j), self.all_sprites, "ground")
        
        if (nameOfTile == "swamp_grass"):
            createVariationTile(["swamp_grass_0","swamp_grass_1","swamp_grass_2"], (i,j), self.all_sprites, "ground")
        
        if (nameOfTile == "dead_grass"):
            createVariationTile(["dead_grass_0","dead_grass_1","dead_grass_2","dead_grass_3"], (i,j), self.all_sprites, "ground")
        
        if (nameOfTile == "snowy_grass"):
            createVariationTile(["snowy_grass_0","snowy_grass_1","snowy_grass_2"], (i,j), self.all_sprites, "ground")
        
        if (nameOfTile == "light_dirt"):
            Tile("light_dirt", (i,j), self.all_sprites, "ground")

        if (nameOfTile == "ice"):
            Tile("ice", (i,j), self.all_sprites, "ground", False)

        if (nameOfTile == "sand"):
            createVariationTile(["sand_0","sand_1","sand_with_dry_grass"], (i,j), self.all_sprites, "ground")

        if (nameOfTile == "sand_with_dry_grass"):
            Tile("sand_with_dry_grass", (i,j), self.all_sprites, "ground")

        # LIQUID
        if (nameOfTile == "water"):
            Tile("water",(i,j), self.all_sprites, "water")

        # TREES
        if (nameOfTile == "elm_tree"):
            Tile("elm_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        if (nameOfTile == "aspen_tree"):
            Tile("aspen_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        if (nameOfTile == "dead_tree"):
            Tile("dead_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        if (nameOfTile == "white_dead_tree"):
            Tile("white_dead_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        if (nameOfTile == "cypress_tree"):
            Tile("cypress_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        if (nameOfTile == "willow_tree"):
            Tile("willow_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        if (nameOfTile == "palm_tree"):
            Tile("palm_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        if (nameOfTile == "snowy_tree"):
            Tile("snowy_tree",(i,j), (self.all_sprites, self.collision_sprites), "obj")

        # FALLEN LOG
        if (nameOfTile == "fallen_log"):
            Tile("fallen_log",(i,j), (self.all_sprites,self.collision_sprites), "obj")

        # CACTI
        if (nameOfTile == "cactus"):
            Tile("cactus",(i,j), (self.all_sprites,self.collision_sprites), "obj")
        if (nameOfTile == "small_cactus"):
            Tile("small_cactus",(i,j), self.all_sprites, "air")

        # FLOWERS
        if (nameOfTile == "red_flowers"):
            Tile("red_flowers",(i,j), self.all_sprites, "air")

        if (nameOfTile == "yellow_flowers"):
            Tile("yellow_flowers",(i,j), self.all_sprites, "air")

        if (nameOfTile == "blue_flowers"):
            Tile("blue_flowers",(i,j), self.all_sprites, "air")

        if (nameOfTile == "frozen_flower"):
            Tile("frozen_flower",(i,j), self.all_sprites, "air")

        if (nameOfTile == "lily_pad"):
            createVariationTile(["lily_pad_0","lily_pad_1"], (i,j), self.all_sprites, "air")

        if (nameOfTile == "duckweed"):
            Tile("duckweed",(i,j), self.all_sprites, "air")

        # CATTAILS
        if (nameOfTile == "cattails"):
            Tile("cattails",(i,j), self.all_sprites, "air")

        # MUSHROOMS
        if (nameOfTile == "red_mushrooms"):
            Tile("red_mushrooms",(i,j), self.all_sprites, "air")

        if (nameOfTile == "magenta_mushrooms"):
            Tile("magenta_mushrooms",(i,j), self.all_sprites, "air")

        if (nameOfTile == "brown_mushrooms"):
            Tile("brown_mushrooms",(i,j), self.all_sprites, "air")

        # ROCKS
        if (nameOfTile == "rock"):
            createVariationTile(["rock_large","rock_medium","rock_small"], (i,j), (self.all_sprites,self.collision_sprites), "obj")

    # startup function that creates the game environment based on the chunk
    # of the player
    def setup(self):

        # get the chunk based on the index of the player position 
        self.currentChunk = self.currentWorld.getChunk(self.player_ChunkPos_on_world[0],self.player_ChunkPos_on_world[1])

        biomeToCheck = str(self.currentChunk.chunkData["biome"])
        print("currentBiome: " + biomeToCheck)

        # Change the music according to the biome
        if biomeToCheck == "swamp":
            self.music = pygame.mixer.Sound(join('assets','audio','music','swamp.mp3'))
            self.music.set_volume(0.5)
        elif biomeToCheck == "aspen_forest":
            self.music = pygame.mixer.Sound(join('assets','audio','music','aspen_forest.mp3'))
            self.music.set_volume(0.5)
        elif biomeToCheck == "dead_forest":
            self.music = pygame.mixer.Sound(join('assets','audio','music','dead_forest.mp3'))
            self.music.set_volume(0.5)
        elif biomeToCheck == "taiga":
            self.music = pygame.mixer.Sound(join('assets','audio','music','taiga.mp3'))
            self.music.set_volume(0.5)
        elif biomeToCheck == "prairie":
            self.music = pygame.mixer.Sound(join('assets','audio','music','prairie.mp3'))
            self.music.set_volume(0.5)
        elif biomeToCheck == "forest":
            self.music = pygame.mixer.Sound(join('assets','audio','music','forest.mp3'))
            self.music.set_volume(0.5)
        elif biomeToCheck == "desert":
            self.music = pygame.mixer.Sound(join('assets','audio','music','desert.mp3'))
            self.music.set_volume(0.5)
        elif biomeToCheck == "snowy_forest":
            self.music = pygame.mixer.Sound(join('assets','audio','music','snowy_forest.mp3'))
            self.music.set_volume(0.5)
        else:
            self.music = pygame.mixer.Sound(join('assets','audio','music','combat1.mp3'))
            self.music.set_volume(0.5)

        # self.currentChunkData = self.currentWorld.getChunkData(self.player_ChunkPos_on_world[0],self.player_ChunkPos_on_world[1])
        

        # print("currentBiome: " + self.currentChunkData["biome"])
        # print("currentBiome via currentChunk: " + self.currentChunk.chunkData["biome"])

        for i in range(CHUNK_SIZE):
            for j in range(CHUNK_SIZE):
                
                ground_tile_id = self.currentChunk.ground_tiles[i][j]
                object_tile_id = self.currentChunk.object_tiles[i][j]

                self.tileCreate(ground_tile_id, i, j)
                self.tileCreate(object_tile_id, i, j)

                # This part of the code determines if the chunk to load will have a barrier air
                # side or not! 
                # First, get the index of the chunk!
                chunkIndex_x = self.player_ChunkPos_on_world[0]
                chunkIndex_y = self.player_ChunkPos_on_world[1]

                # print("- - - - - - - - - - - - - - -")

                # print("chunkIndex_x:" + str(chunkIndex_x))
                # print("chunkIndex_y:" + str(chunkIndex_y))

                # print(" i (row):" + str(chunkIndex_x))
                # print(" j (column):" + str(chunkIndex_y))

                # print("- - - - - - - - - - - - - - -")

                # Then, create a bool variable that determines if 
                # a border_fog tile is to be created or not
                createBorderFog = True

                # Check for the north side (top border)
                if chunkIndex_x == 0 and i == 0:
                    self.tileCreate("barrier_air", i, j)
                    createBorderFog = False

                # Check for the south side (bottom border)
                if chunkIndex_x == MAP_SIZE - 1 and i == CHUNK_SIZE - 1:  
                    self.tileCreate("barrier_air", i, j)
                    createBorderFog = False

                # Check for the left side (left border)
                if chunkIndex_y == 0 and j == 0:
                    self.tileCreate("barrier_air", i, j)
                    createBorderFog = False

                # Check for the right side (right border)
                if chunkIndex_y == MAP_SIZE - 1 and j == CHUNK_SIZE - 1:
                    self.tileCreate("barrier_air", i, j)
                    createBorderFog = False

                # Place a border fog in the border of the chunks
                if (i <= 0 or i >= CHUNK_SIZE - 1 or j <= 0 or j >= CHUNK_SIZE - 1) and createBorderFog:
                    self.tileCreate("border_fog", i,j)

        # Set the working directory to the factioncraft folder (IMPORTANT, removing this will cause the game to crash)
        # os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '/..',))

        # Create player
        # self.player = Player(( (CHUNK_SIZE * 64) / 2 , (CHUNK_SIZE * 64) / 2 ), self.all_sprites, self.collision_sprites)
        chunkPos = self.currentChunk.getIndexTypeStr()

        playerPos = self.future_world_pos
        print("Player Pos on setup(): " + str(playerPos))
        self.player = Player(playerPos, chunkPos, self.all_sprites, self.collision_sprites)

    def quitGame(self, type = "load_other_chunk"):

        # Stop the music
        self.music.stop()

        if type == "load_other_chunk":
            # Return the player_ChunkPos_on_world (a touple)
            # so the start_level() function can work properly
            to_return = self.player_ChunkPos_on_world
            print("to_return (load):" + str(to_return))
            return to_return
        if type == "back_bttn":
            # Returning "finished" will cause the start_level()
            # to end
            to_return = "finished"
            print("to_return (back_bttn):" + str(to_return))
            return to_return

    def backButton(self):

        # Get the mouse position
        MOUSE_POS = pygame.mouse.get_pos()

        # Define and create the back button
        BACK_BUTTON_IMG = self.textures["BACK_BUTTON_IMG"]
        BACK_BUTTON_HOVER_IMG = self.textures["BACK_BUTTON_HOVER_IMG"]

        BACK_BUTTON = Button(image=BACK_BUTTON_IMG, pos=(WINDOW_WIDTH - ( WINDOW_WIDTH * 0.95), WINDOW_HEIGHT - ( WINDOW_HEIGHT * 0.95)), 
                            text_input="", font=get_font(75), base_color="White", hovering_color="Green", imageScale=6)

        # Set the hover image (as of 17/feb/2025,12:32am, the hovering function is "inverted" with the regular image)
        BACK_BUTTON.setHoverImg(BACK_BUTTON_HOVER_IMG)

        # event loop 
        for event in pygame.event.get():
            # Check if the player is touching the back button
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    self.music.fadeout(200)
                    # Go back to Cycle 1a.
                    # returning "finished" will end the cycle 
                    # and make it so the game returns to the main_menu()
                    self.running = False

        
        # draw the back button
        BACK_BUTTON.changeColor(MOUSE_POS)
        BACK_BUTTON.update(self.display_surface)

    def updatePlayerFuturePosition(self, availableDirs, playerCurrentPos):

        # Step 1: Receive the last available directions & and 
        # the last USED direction
        lastUsedDir = self.last_used_dir

        # Step 2: Store the player's current position
        # Step 3: Create a copy of them
        # Define the vars that hold the x and y to return as a list
        # also, store the player's current positions
        f_posx = playerCurrentPos[0]
        f_posy = playerCurrentPos[1]

        # Step 4: Run a series of conditionals to generate the new
        # coordinates
        if lastUsedDir == UP and UP in availableDirs: 
            f_posy = CHUNK_SIZE - 0.1
        if lastUsedDir == DOWN and DOWN in availableDirs: 
            f_posy = 0.1

        if lastUsedDir == LEFT and LEFT in availableDirs: 
            f_posx = CHUNK_SIZE - 0.1
        if lastUsedDir == RIGHT and RIGHT in availableDirs: 
            f_posx = 0.1

        # Step 5: Set the coordinates of the player to f_posx & f_posy
        self.future_world_pos = [f_posx, f_posy]

    # Calculates the timer stuff to determine if the timer is 
    # already done
    def updateTimer_UpdateAnimTiles(self):
        current_time = self.timerData_updateAnimTiles["current_time"]
        last_time = self.timerData_updateAnimTiles["last_time"]
        delay = self.timerData_updateAnimTiles["delay"]
        
        # Check if the timer is already done
        if (current_time - last_time >= delay):
            # Rewind the timer
            self.timerData_updateAnimTiles["last_time"] = pygame.time.get_ticks()
            # Return true because tiles can now proceed to the next drame
            return True

        # Return false :(
        return False
    
    # Calculates the timer stuff to determine if the timer is 
    # already done
    def updateTimer_UpdateBackground(self):
        current_time = self.timerData_updateBackground["current_time"]
        last_time = self.timerData_updateBackground["last_time"]
        delay = self.timerData_updateBackground["delay"]
        
        # Check if the timer is already done
        if (current_time - last_time >= delay):
            # Rewind the timer
            self.timerData_updateBackground["last_time"] = pygame.time.get_ticks()
            # Return true because tiles can now proceed to the next drame
            return True

        # Return false :(
        return False
    
    # Calculates the timer stuff to determine if the timer is 
    # already done
    def updateTimer_UpdateEntityFrames(self):
        current_time = self.timerData_updateEntityFrames["current_time"]
        last_time = self.timerData_updateEntityFrames["last_time"]
        delay = self.timerData_updateEntityFrames["delay"]
        
        # Check if the timer is already done
        if (current_time - last_time >= delay):
            # Rewind the timer
            self.timerData_updateEntityFrames["last_time"] = pygame.time.get_ticks()
            # Return true because tiles can now proceed to the next drame
            return True

        # Return false :(
        return False

    def run(self):
        
        self.music.stop()
        self.music.play(loops=-1)

        # This is the base path for the background
        base_path = join('assets','images','other','level_bg')

        # Current index for the background image
        current_index = 0

        # Background
        background = pygame.image.load(join(base_path, f"cloud_spiral{current_index}.png")).convert_alpha()

        # Continue executing if 'running
        while self.running:

            # DEBUG STUFF ONLY
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                # print("Key Event: Spawned Enemy!")
                entity_sprites = [sprite for sprite in self.all_sprites if hasattr(sprite, 'isEntity')]
                for sprite in entity_sprites:
                    if hasattr(sprite, "isEntity"):
                        sprite.death_time = 400

            if keys[pygame.K_2]:

                # Get the screen center
                # screen_center = self.display_surface.get_rect().center
                # Adjust the y coordinate by +32
                # adjusted_center = (screen_center[0], screen_center[1] + 28)
                # dmg_Path = join(PATH_IMG,'damage','generic','3.png')
                # damage_image = pygame.image.load(dmg_Path).convert_alpha()
                # damage_rect = damage_image.get_frect(center=adjusted_center)

                print("(GAME) Created damage sprite!")
                
                # self.player.playerData["health"] -= 10

                # i = self.player.wrlpos.x * 16
                # j = self.player.wrlpos.y * 16
                # print("x: " + str(i) + ", j: " + str(j))
                # i = 0 
                # j = 0



            # Create a scaled background variable that is basically
            # a copy of the start_game_panorama but scaled, uses the WIDTH and HEIGHT to
            # scale correctly
            scaled_background = scale_background(background, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            # Get the current time for the anim tiles timer
            self.timerData_updateAnimTiles["current_time"] = pygame.time.get_ticks()

            # Get the current time for the update background timer
            self.timerData_updateBackground["current_time"] = pygame.time.get_ticks()

            # Get the current time for the update background timer
            self.timerData_updateEntityFrames["current_time"] = pygame.time.get_ticks()

            # dt 
            dt = self.clock.tick() / 1000

            # Boolean value that detemines if the Animated Tiles are to be updated 
            nextFrameAnimTile = self.updateTimer_UpdateAnimTiles()

            # Boolean value that detemines if the Entities are to be updated 
            nextFrameEntities = self.updateTimer_UpdateEntityFrames()

            # Determines if the background is to be updated (animated) 
            if self.updateTimer_UpdateBackground():
                background, current_index = cycle_image(base_path, current_index)

            # event loop 
            for event in pygame.event.get():

                # Quit detection
                if event.type == pygame.QUIT:
                    self.music.fadeout(100)
                    self.running = False

            # update 
            self.player.getStandingOn(self.currentChunk.ground_tiles)
            self.player.getPassingThrough(self.currentChunk.object_tiles)
            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center, nextFrameAnimTile, nextFrameEntities, scaled_background)
            self.player.drawInfo(self.display_surface)

            # draw the back button & its functionalities
            self.backButton()

            self.player.drawWater(self.display_surface)
            self.player.drawAccessory(self.display_surface)
            self.player.updateEntity_Damaged(self.damage_sprites)

            # Update the display screen
            pygame.display.update()


            # if running is falce, do a back_bttn return
            if self.running == False:
                return self.quitGame("back_bttn")

            # This code handles the part of the game that loads an adjacent chunk
            # Checks if the player is within bounds and if it can load an adjacent chunk
            if self.isPlayerOutOfWorldBound():

                # get the direction of where the player's chosen chunk is located 
                dir = self.getDirectionOfChunkMove()
                # print("direction to move:" + dir)

                dirsPlayerCanMoveTo = self.getDirPlayerCanMoveTo()
                # print("directions Player CAN move to:" + str(dirsPlayerCanMoveTo))

                # Copy of the player_ChunkPos_on_world
                playerChunkPos_Y = self.player_ChunkPos_on_world[1] 
                playerChunkPos_X = self.player_ChunkPos_on_world[0] 

                # print("playerChunkPos_X: " + str(playerChunkPos_X))
                # print("playerChunkPos_Y: " + str(playerChunkPos_Y))

                if dir == "up" and dir in dirsPlayerCanMoveTo:
                    self.player_ChunkPos_on_world = [playerChunkPos_X, playerChunkPos_Y - 1]

                elif dir == "down" and dir in dirsPlayerCanMoveTo:
                    self.player_ChunkPos_on_world = [playerChunkPos_X, playerChunkPos_Y + 1]

                if dir == "left" and dir in dirsPlayerCanMoveTo:
                    self.player_ChunkPos_on_world = [playerChunkPos_X - 1, playerChunkPos_Y]

                elif dir == "right" and dir in dirsPlayerCanMoveTo:
                    self.player_ChunkPos_on_world = [playerChunkPos_X + 1, playerChunkPos_Y]

                # If the list is NOT an EMPTY list, then load another chunk
                if not dirsPlayerCanMoveTo == []:


                    self.last_used_dir = dir
                    self.last_available_dirs = dirsPlayerCanMoveTo

                    changeBgToLoading

                    # self.running = False
                    return self.quitGame("load_other_chunk")
            
            # After everything has loading, player can now move
            # This is to prevent a bug in which, after chunk loading, the player
            # could phase through tiles, causing a mismatch between the world pos
            # and the real player's position on the world
            self.player.canMove = True

        # Return the player_ChunkPos_on_world (a touple)
        # so the start_level() function can work properly
        return self.quitGame()
    
    def setPlayerChunkPosOnWorld(self, val):
        self.player_ChunkPos_on_world = val

# Function to scale the background image to the current screen size
def scale_background(image, width, height):#
    return pygame.transform.scale(image, (width, height))

# Function to cycle through images
def cycle_image(base_path, current_index):
    # Increment the index
    current_index += 1

    # Reset to 0 if the index exceeds 23
    if current_index > 23:
        current_index = 0

    # Construct the new image path
    image_path = join(base_path, f"cloud_spiral{current_index}.png")

    # Load the image
    image = pygame.image.load(image_path).convert_alpha()

    return image, current_index

# Change to a loading bg screen
def changeBgToLoading(screen):

    image = pygame.image.load(join('assets', 'images', 'gui', 'loading_bg.png')).convert_alpha()
    scaled_background = scale_background(image, WINDOW_WIDTH, WINDOW_HEIGHT)
    screen.blit(scaled_background)
    pygame.display.update()

    # Sleep for 1s
    time.sleep(1)




    # TE QUEDASTE EN HACER QUE HAGA DISPLAY DESPUES DEL UPDATE AL WATER SPLASH