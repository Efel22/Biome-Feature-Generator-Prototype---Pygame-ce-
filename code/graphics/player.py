from settings import * 
import math
import os
from os.path import join
# from levels.chunk import CHUNK_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_onScreen, chunkPos, groups, collision_sprites):
        super().__init__(groups)
        # self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(join('assets','images', 'player', '0.png')).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 4.0)

        # The player's position on the scren
        self.screenPos = pos_onScreen

        rect_center_coords = (pos_onScreen[0] * (16*4), pos_onScreen[1] * (16*4))
        self.rect = self.image.get_frect(center = rect_center_coords)
        # Create a hitbox that has the .inflate func(), this 
        # expands the rectangle in width BUT remains the same in height
        self.hitbox_rect = self.rect
        self.hitbox_rect = self.rect.inflate(-60, -60)
     
        # movement 
        self.direction = pygame.Vector2()
        self.speed = 350
        self.runningSpeed = 500
        # The true speed of the player (not the base)
        self.actualSpeed = self.speed

        # The collision sprites
        self.collision_sprites = collision_sprites

        # Chunk position as in the MAP_SIZE (e.g.: 3_2)
        self.chunkPos = chunkPos

        # This is the world position of the player
        self.wrlpos = pygame.Vector2()
        self.wrlpos.x += (pos_onScreen[0]) # See explanation for the (16 * 4) thingie
        self.wrlpos.y += (pos_onScreen[1])

        # Holds the value for the ground tile player is standing on
        self.standingOn = "none"
        # Holds the value for the object tile player is passing through
        self.passingThrough = "none"

        # WALKING ANIMATION VALUES
        self.isPlayer = True
        self.state = "right"

        self.isImageFlipped = False
        if self.state == "left":
            self.isImageFlipped = True

        self.frameIndex = 0
        self.updateFrame = False
        self.isMoving = False

        # SPLASH WATER ANIMATION VALUES
        self.current_frame = 0  # Current frame of the water splash animation
        self.animation_speed = 0.05  # Speed of the animation (frames per update)
        self.frame_timer = 0  # Timer to control frame upda

        # Load the images so the game doesn't lag
        self.load_images()

        # This is the data that will be passed on to the next chunk loading
        # Can also be stored
        self.playerData = {
            
            "state": self.state,
            "accessory": "",
            "health": 100,
            "max_health": 100,
            "main_weapon": "sword"
        }

        # This is to prevent the player from instantly getting
        # into a level after pressing "play"
        self.timerData_CanTakeDamage = {
            "delay": 500,
            "last_time": 0,
            "current_time": 0
        }

        # This is to prevent a bug in which, after chunk loading, the player
        # could phase through tiles, causing a mismatch between the world pos
        # and the real player's position on the world
        self.canMove = False

    def load_images(self):

        """
        Loads all images from a specified directory and returns them as a list of frames.

        Args:
            base_dir (str): The base directory (e.g., "assets").
            subfolder (str): The subfolder path (e.g., "images/player").

        Returns:
            list: A list of Pygame surfaces (frames).
        """

        base_dir = "assets"
        subfolder = join("images", "player")

        # Construct the full path to the image folder
        image_folder = join(base_dir, subfolder)

        # List to store the frames (images)
        self.frames = []

        # Check if the directory exists
        if not os.path.exists(image_folder):
            print(f"Directory not found: {image_folder}")
            return

        # Get a list of all files in the directory
        file_names = [f for f in os.listdir(image_folder) if os.path.isfile(join(image_folder, f))]

        # Filter for image files (e.g., PNG, JPG)
        image_files = [f for f in file_names if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        # Sort files numerically (if named as 0.png, 1.png, etc.)
        image_files.sort(key=lambda name: int(name.split('.')[0]))

        # Load each image and store it as a frame
        for file_name in image_files:
            full_path = join(image_folder, file_name)
            try:
                image = pygame.image.load(full_path).convert_alpha()  # Load and optimize the image
                self.frames.append(image)
                # print(f"Loaded frame: {file_name}")
            except pygame.error as e:
                print(f"Failed to load {file_name}: {e}")

        self.amountOfFrames = len(self.frames)

        # Load water splash frames and scale them by 4.0
        self.water_splash_frames = []
        # scale_factor = 4.0  # Scaling factor
        for i in range(3):  # Assuming frames are named 0.png, 1.png, 2.png
            frame_path = join("assets", "images", "player", "splash", f"{i}.png")
            frame = pygame.image.load(frame_path).convert_alpha()
            
            # Scale the frame
            # original_size = frame.get_size()
            # new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
            # scaled_frame = pygame.transform.scale_by(frame, new_size)
            
            scaled_frame = pygame.transform.scale_by(frame, 4.0)

            self.water_splash_frames.append(scaled_frame)
        
    def getStandingOn(self, ground_tiles):
        # Update the standing on to be the equivalent of the player's world pos
        # to that of the ground tiles of the current chunk
        max_x = len(ground_tiles) - 1 # These are the rows
        max_y = len(ground_tiles[0]) - 1 if ground_tiles else 0  # These are the columns

        tile_x = math.floor(self.wrlpos.x)
        tile_y = math.floor(self.wrlpos.y)

        # Ensure indices are within bounds
        if 0 <= tile_x <= max_x and 0 <= tile_y <= max_y:
            self.standingOn = ground_tiles[tile_x][tile_y]
        else:
            self.standingOn = "none"

        return self.standingOn

    def getPassingThrough(self, object_tiles):
        # Update the standing on to be the equivalent of the player's world pos
        # to that of the ground tiles of the current chunk
        max_x = len(object_tiles) - 1 # These are the rows
        max_y = len(object_tiles[0]) - 1 if object_tiles else 0  # These are the columns

        tile_x = math.floor(self.wrlpos.x)
        tile_y = math.floor(self.wrlpos.y)

        # Ensure indices are within bounds
        if 0 <= tile_x <= max_x and 0 <= tile_y <= max_y:
            self.passingThrough = object_tiles[tile_x][tile_y]
        else:
            self.passingThrough = "none"

        return self.passingThrough

    # Displays Info. to the player screen.
    # Remove the "return" to view information on-screen.
    def drawInfo(self, screen):

        return

        text_color = pygame.Color("white")
        shadow_color = pygame.Color("black")

        info = "wPos: " + str(self.wrlpos) 
        info += "\non: " + str(self.standingOn) 
        info += "\nin: " + str(self.passingThrough) 
        info += "\nstate: " + str(self.state) 
        info += "\ncPos: " + str(self.chunkPos)

        font =  pygame.font.Font(join('assets','font','gen.ttf'), 28)  # Font for the text

        text_surface1 = font.render(info, True, text_color)

        # shadow
        shadow_text_surface1 = font.render(info, True, shadow_color)

        # Position the text in the center of the button
        text_rect1 = text_surface1.get_rect(center=(960, 200))

        shadow_text_rect1 = text_surface1.get_rect(center=(960 + 2, 200 + 2))

        # Draw the text
        screen.blit(shadow_text_surface1, shadow_text_rect1)
        screen.blit(text_surface1, text_rect1)

    def tp(self, pos):
        self.wrlpos = pos

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        if keys[pygame.K_2]:
            self.playerData["accessory"] == "caca"
            # print("set accessory to caca")

        if keys[pygame.K_3]:
            self.playerData["accessory"] == "balloon"
            # print("set accessory to balloon")

    def move(self, dt):
        
        # This is to prevent a bug in which, after chunk loading, the player
        # could phase through tiles, causing a mismatch between the world pos
        # and the real player's position on the world
        if not self.canMove:
            return

        keys = pygame.key.get_pressed()

        # Check if the player is on water
        if self.standingOn == "water":
            # If on water and not pressing shift, set speed to 200
            if not keys[pygame.K_LSHIFT]:
                self.actualSpeed = 200
            # If on water and pressing shift, increase speed by 50
            elif keys[pygame.K_LSHIFT]:
                self.actualSpeed = 200 + 50

            if self.passingThrough == "lily_pad":
                self.actualSpeed += 50
        # If not on water and pressing shift, set speed to running speed
        elif keys[pygame.K_LSHIFT]:
            self.actualSpeed = self.runningSpeed
        else:
            self.actualSpeed = self.speed

        self.hitbox_rect.x += self.direction.x * self.actualSpeed * dt
        self.collision('horizontal', dt)
        self.hitbox_rect.y += self.direction.y * self.actualSpeed * dt
        self.collision('vertical', dt)

        # Set the center of the self.rect to the self.hitbox
        self.rect.center = self.hitbox_rect.center

        # This makes it so the player is tracked throughout the world, as of (4th march 2025, 11:53am),
        # it seems to be working fairly well. 
        # The speed is divided by (take with a grain of salt):
        # texture size = 16x16 = 16
        # scale of texture = 4
        self.wrlpos.x += (self.direction.x * (self.actualSpeed / (16 * 4)) * dt)
        self.wrlpos.y += (self.direction.y * (self.actualSpeed / (16 * 4)) * dt)

        if self.direction.x != 0 or self.direction.y != 0:
            self.isMoving = True
        else:
            self.isMoving = False

        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'

        if self.state == "right" and self.isImageFlipped:
            # Unflip the image if it's flipped but the state is "right"
            self.isImageFlipped = False
            self.image = pygame.transform.flip(self.image, True, False)

        elif self.state != "right" and not self.isImageFlipped:
            # Flip the image if it's not flipped but the state is not "right"
            self.isImageFlipped = True
            self.image = pygame.transform.flip(self.image, True, False)

    def collision(self, direction, dt):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: 
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: 
                        self.hitbox_rect.left = sprite.rect.right
                    # Stop movement in the horizontal direction
                    self.direction.x = 0  # Prevent further movement
                else:
                    if self.direction.y < 0: 
                        self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: 
                        self.hitbox_rect.bottom = sprite.rect.top
                    # Stop movement in the vertical direction
                    self.direction.y = 0  # Prevent further movement

    def update(self, dt):

        # Update water splash animation if on water
        if self.standingOn == "water":
            self.frame_timer += self.animation_speed
            if self.frame_timer >= 1:
                self.current_frame = (self.current_frame + 1) % len(self.water_splash_frames)
                self.frame_timer = 0

        self.input()
        self.move(dt)

        self.playerData["state"] = self.state

    def updatePlayerFrame(self):

        # return

        # Prevent any non animated tiles from having their tile updated
        # if not self.isPlayer:
        #     return

        if self.updatePlayerFrame and self.isMoving:


            self.frameIndex = self.frameIndex + 1

            if self.frameIndex > self.amountOfFrames - 1:
                self.frameIndex = 0

            self.image = self.frames[self.frameIndex]

            # If the player is currently looking to the right, turn it to the left
            if self.state == "left" and self.isImageFlipped:
                self.image = pygame.transform.flip(self.image, True, False)

            # # If the player is currently looking to the right, turn it to the left
            # if self.state == "right":
            #     self.image = pygame.transform.flip(self.image, False, False)

            # Scale the image
            self.image = pygame.transform.scale_by(self.image, TILE_SIZE / 16)

            self.updateFrame = False
        else:
            self.updateFrame = True

            if self.isMoving == False:
                self.image = self.frames[0]

                if self.state == "left" and self.isImageFlipped:
                    self.image = pygame.transform.flip(self.image, True, False)

                self.image = pygame.transform.scale_by(self.image, TILE_SIZE / 16)


        # "- - - - - - - updated player frame Index"
    
    def drawWater(self, screen):
        # Draw the water splash animation if on water
        if self.standingOn == "water":
            splash_image = self.water_splash_frames[self.current_frame]
            # Get the screen center
            screen_center = screen.get_rect().center
            # Adjust the y coordinate by +32
            adjusted_center = (screen_center[0], screen_center[1] + 28)
            splash_rect = splash_image.get_frect(center=adjusted_center)
            screen.blit(splash_image, splash_rect)

    def drawAccessory(self,screen):

        # FOR NOW, DONT DO ANYTHING HERE
        return 
        if self.current_accessory == "none":
            return
        
        pathToAccessory = ""
        hardcodedPath = join('assets', 'images', 'player', 'accessories')

        if self.current_accessory == "caca":
            pathToAccessory = join(hardcodedPath, 'caca.png')

        if self.current_accessory == "balloon":
            pathToAccessory = join(hardcodedPath, 'balloon.png')
        
        accessory_image = pygame.image.load(pathToAccessory).convert_alpha()
        accessory_image = pygame.transform.scale_by(accessory_image, 4.0)

        # Get the screen center
        screen_center = screen.get_rect().center
        # Adjust the y coordinate by +32
        adjusted_center = (screen_center[0], screen_center[1] - 11)
        accessory_rect = accessory_image.get_frect(center=adjusted_center)
        screen.blit(accessory_image, accessory_rect)
            
    # If the entity is damaged
    def updateEntity_Damaged(self, damage_sprites):
        player_hp = self.playerData["health"]
        self.can_be_damaged = False

        # If it has collided with a damage sprite, get the damage of the 
        # damage_sprite and subtract from player health
        for damage_sprite in damage_sprites:
            if self.rect.colliderect(damage_sprite.rect):
                if self.can_be_damaged:
                    # player_hp -= damage_sprite.damage
                    player_hp -= 10
                    self.can_be_damaged = False
                    # Start the timer
                    self.timerData_CanTakeDamage["last_time"] = self.timerData_CanTakeDamage["current_time"]

        # Update the timer
        self.timerData_CanTakeDamage["current_time"] = pygame.time.get_ticks()
        if (self.timerData_CanTakeDamage["current_time"] - self.timerData_CanTakeDamage["last_time"] >= self.timerData_CanTakeDamage["delay"]):
            self.can_be_damaged = True

        # Update the player's remaining health
        self.playerData["health"] = player_hp















