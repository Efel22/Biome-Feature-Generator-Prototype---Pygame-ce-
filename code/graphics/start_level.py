from graphics.graphicsmain import *

def start_level(levelIndex, levelName, screen):

    # updateTileFrames = pygame.event.custom_type()
    # pygame.time.set_timer(updateTileFrames, 500)

    # updateBackgroundFrames = pygame.event.custom_type()
    # pygame.time.set_timer(updateBackgroundFrames, 1000)
 
    # This value can hold (as of 5th/march/2025, 10:34pm) 
    # two kind of values: 
    # - touple (chunk index)
    # - string ("finished", to stop the cycle)
    quitInfo = (-1,-1)

    openedPlaythrough = Game_2(levelIndex, levelName, screen)

    while(True):
        
        # Setup the graphics based on the chunk
        openedPlaythrough.setup()

        # Run the game, inside this function, the current chunk will 
        # change (player_ChunkPos_on_world[x&y])
        quitInfo = openedPlaythrough.run()
        
        # print("quitInfo:")
        # print(quitInfo)

        # if the quitInfo is "finished", stop the cycle
        if quitInfo == "finished":
            return

        # assumming the quitInfo is NOT a STRING, it is a LIST,
        # thus, it holds the value of the chunkIndex
        openedPlaythrough.setPlayerChunkPosOnWorld(quitInfo)

        # Create a copy of the last directions the player was able to move to
        lastDirs = openedPlaythrough.last_available_dirs
        # Create a copy of the player's current position on the world
        current_player_world_pos = openedPlaythrough.player.wrlpos

        # Update the player's future position after running this function
        # that returns a list of coordinates
        openedPlaythrough.updatePlayerFuturePosition(lastDirs, current_player_world_pos)

        # Deletes all of the all, collision, and enemy sprites
        openedPlaythrough.reset()

        changeBgToLoading(openedPlaythrough.display_surface)

        print("")
        print("---------------------------------")
        print("")# 

