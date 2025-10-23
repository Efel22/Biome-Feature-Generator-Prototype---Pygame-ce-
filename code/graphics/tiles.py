from settings import *
from graphics.sprites import *
from random import choice, random
import os


class Tile(pygame.sprite.Sprite):
    def __init__(self, id, index, groups, type, canBeMirrored = True):
        super().__init__(groups)

        # Initialize Animated Texture vars
        self.isAnimated = False
        # This is the index for the current frame of the object
        self.frameIndex = 0
        self.amountOfFrames = 0
        # Initialize the empty list
        self.frames = []

        # This checks of there is a directory with the name being the "id" of this tile
        # If there is, then it going to establish the Tile has an animated texture!
        try:
            items = os.listdir(join('assets', 'images', 'tiles', id))
            if len(items) > 0:
                self.isAnimated = True
        except:
            pass

        if self.isAnimated:

            # List all items in the directory
            # Path to the directory based on the id of the tile
            items = os.listdir(join('assets', 'images', 'tiles', id))

            # Filter out only files (exclude directories)
            files = [item for item in items if os.path.isfile(os.path.join('assets', 'images', 'tiles', id, item))]

            # The amount of frames is set for this object
            self.amountOfFrames = len(files)

            # Get the images and import them, append them to the frames list
            for i in range(self.amountOfFrames):
                imgToImport = pygame.image.load(join('assets', 'images', 'tiles', id, str(id) + str(i) + ".png")).convert_alpha()
                self.frames.append(imgToImport)

            self.image = pygame.image.load(join('assets', 'images', 'tiles', id, str(id) + "0.png")).convert_alpha()
        else:
            self.image = pygame.image.load(join('assets', 'images', 'tiles', str(id) + ".png")).convert_alpha()
            

        self.image = pygame.transform.scale_by(self.image, TILE_SIZE / 16)

        # 50% chance of inverting a non-animated tile's texture
        if not self.isAnimated and ( random() < (50 / 100) ) and canBeMirrored:
            self.image = pygame.transform.flip(self.image, True, False)

        self.id = id
        self.index = index
        self.pos = (self.index[0] * TILE_SIZE, self.index[1] * TILE_SIZE)
        self.rect = self.image.get_frect(topleft = self.pos)
        self.type = type
        

        # Determines the orden on which it is rendered :D
        self.isGroundTile = False
        self.isObjectTile = False
        if type == "ground" or type == "water":
            self.isGroundTile = True
        else:
            self.isObjectTile = True

    def updateFrame(self):

        # Prevent any non animated tiles from having their tile updated
        if not self.isAnimated:
            return

        self.frameIndex = self.frameIndex + 1

        if self.frameIndex > self.amountOfFrames - 1:
            self.frameIndex = 0

        self.image = self.frames[self.frameIndex]
        self.image = pygame.transform.scale_by(self.image, TILE_SIZE / 16)

# Returns a random tile
def getRandomTile(listOfTiles):
    return choice(list(listOfTiles))

# Creates a Tile with a chosen id (ids = ["id1", "id2"...])
def createVariationTile(ids, index, groups, type):
    Tile(str(choice(list(ids))), index, groups, type)

