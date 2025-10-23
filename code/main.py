from settings import *
from gui.button import Button
from graphics.start_level import *



class Game:
    def __init__(self):
        # setup
        pygame.init()

        # Set the working directory to the factioncraft folder (IMPORTANT, removing this will cause the game to crash)
        # This makes it so the "game" is executing from the 'factioncraft' folder instead of factioncraft/code, which
        # would make it so it can't find any assets, levels, etc. files! 
        # os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

        # Create the Game Screen
        self.SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT - (WINDOW_HEIGHT * 0.05)), pygame.RESIZABLE)
        pygame.display.set_caption("Pixelonia")

        pygame.display.set_icon(pygame.image.load(join('assets','images','other','icon.png')).convert_alpha())
        self.clock = pygame.time.Clock()

        # This is to prevent the player from instantly getting
        # into a level after pressing "play"
        self.timerData_AfterPlayBtn = {
            "delay": 1000,
            "last_time": 0,
            "current_time": 0
        }

        # This is the timer FOR preventing weird behavior
        # after creating a new level
        self.timerData_AfterLevelCreation = {
            "delay": 1000,
            "last_time": 0,
            "current_time": 0
        }

        self.load_images()

    # Load the images
    def load_images(self):
        self.textures = {
            "play_bg": pygame.image.load(join('assets','images','gui','choose_world_bg.png')).convert_alpha(),
            "BACK_BUTTON_IMG": pygame.image.load(join('assets', 'images', 'gui', 'back_button.png')).convert_alpha(),
            "BACK_BUTTON_HOVER_IMG": pygame.image.load(join('assets', 'images', 'gui', 'back_button_hover.png')).convert_alpha()
        }

    def quit(self):
        pygame.quit()
        sys.exit()

    def find_level_info(self, target_index):
        levels_dir = "levels"
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")
                level_info = {"index": None, "name": None}

                with open(file_path, "r") as file:
                    for line in file:
                        key_value = line.strip().split("=")
                        if len(key_value) == 2:
                            key, value = key_value
                            if key in level_info:
                                level_info[key] = value if key != "index" else int(value)

                    # If the index matches, return the details
                    if level_info["index"] == target_index:
                        return {
                            "name": level_info["name"]
                        }
        
        return None  # Return None if no matching index is found

    def find_level_name(self, target_index):
        levels_dir = "levels"
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)  # Load JSON data
                    
                    # Check if 'index' key exists and matches target_index
                    if isinstance(data, dict) and "index" in data and "name" in data:
                        if data["index"] == target_index:
                            return data["name"]  # Return level name as a string

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return None  # Return None if no matching level is found

    def worldButtons(self, currentMusic):

        # Get the mouse position and is mouse being pressed
        MOUSE_POS = pygame.mouse.get_pos()
        MOUSE_PRESSED = pygame.mouse.get_pressed()

        # Each button must show the following information
        # - Name
        # - Date of Last Plsaayed

        # Define the positions in terms of X (so they are centered horizontally)
        # Define the width, height and spacing of the buttons
        # Button dimensions and spacing
        BUTTON_WIDTH = 480
        BUTTON_HEIGHT = 300
        BUTTON_SPACING = 20  # Space between buttons

        # Calculate the total width of all buttons and spacing
        total_width = (3 * BUTTON_WIDTH) + (2 * BUTTON_SPACING)
        # Calculate the starting X position to center the buttons
        start_x = (WINDOW_WIDTH - total_width) // 2

        # Create the buttons
        worldButtons = [
            WorldButton(start_x, 250, BUTTON_WIDTH, BUTTON_HEIGHT, index=1),
            WorldButton(start_x + BUTTON_WIDTH + BUTTON_SPACING, 250, BUTTON_WIDTH, BUTTON_HEIGHT, index=2),
            WorldButton(start_x + 2 * (BUTTON_WIDTH + BUTTON_SPACING), 250, BUTTON_WIDTH, BUTTON_HEIGHT, index=3)
        ]

        # Update the buttons if they're being interacted with
        # Then draw them on the screen
        for button in worldButtons:
            button.check_hover(MOUSE_POS)

            current_time = self.timerData_AfterPlayBtn["current_time"]
            last_time = self.timerData_AfterPlayBtn["last_time"]
            delay = self.timerData_AfterPlayBtn["delay"]

            # Check if the delay has passed
            if button.is_clicked(MOUSE_POS, MOUSE_PRESSED) and (current_time - last_time >= delay):
                 
                # if the level exists, then open it, after ending the playthrough, open the main menu
                if button.level_exists():

                    changeBgToLoading(self.SCREEN)
                    # Stop the current music from playing so it doesn't overlap
                    currentMusic.stop()
                    button.update_level_last_played()
                    start_level(button.index, self.find_level_name(button.index), self.SCREEN)
                    self.main_menu()
                    
                else:

                    changeBgToLoading(self.SCREEN)
                    self.timerData_AfterPlayBtn["last_time"] = pygame.time.get_ticks()
                    print("World does not exist!: " + str(button.index)) # Debug
                    Level = LevelCreator(button.index)
                    Level.setLevelName("")
                    Level.create_files()
                    Level.loadWorldMap("generate")
                    print("World Has been Created") # Debug
                    
                        

            button.draw(self.SCREEN)

    def deleteButtons(self):

        # Get the mouse position and is mouse being pressed
        MOUSE_POS = pygame.mouse.get_pos()
        MOUSE_PRESSED = pygame.mouse.get_pressed()

        # Each button must show the following information
        # - Name
        # - Date of Last Played

        # Define the positions in terms of X (so they are centered horizontally)
        # Define the width, height and spacing of the buttons
        # Button dimensions and spacing
        BUTTON_WIDTH = 480
        BUTTON_HEIGHT = 80
        BUTTON_SPACING = 20  # Space between buttons

        # Calculate the total width of all buttons and spacing
        total_width = (3 * BUTTON_WIDTH) + (2 * BUTTON_SPACING)
        # Calculate the starting X position to center the buttons
        start_x = (WINDOW_WIDTH - total_width) // 2

        start_y = 600

        # Create the buttons
        deleteButtons = [
            DeleteWorldButton(start_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, index=1),
            DeleteWorldButton(start_x + BUTTON_WIDTH + BUTTON_SPACING, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, index=2),
            DeleteWorldButton(start_x + 2 * (BUTTON_WIDTH + BUTTON_SPACING), start_y, BUTTON_WIDTH, BUTTON_HEIGHT, index=3)
        ]

        # Update the buttons if they're being interacted with
        # Then draw them on the screen
        for button in deleteButtons:
            button.check_hover(MOUSE_POS)

            current_time = self.timerData_AfterPlayBtn["current_time"]
            last_time = self.timerData_AfterPlayBtn["last_time"]
            delay = self.timerData_AfterPlayBtn["delay"]

            # If the level even exists... do:
            if button.level_exists():

                # Check if the delay has passed
                if button.is_clicked(MOUSE_POS, MOUSE_PRESSED) and (current_time - last_time >= delay):
                    
                    button.delete_level()

                    # Stop the current music from playing so it doesn't overlap
                    # currentMusic.stop()

                    print("World has been deleted!: " + str(button.index)) # Debug
                    self.timerData_AfterPlayBtn["last_time"] = pygame.time.get_ticks()\
                
                button.draw(self.SCREEN)

    # This opens up the choose_world page
    def play(self):

        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

        # Start playing some Music
        music = pygame.mixer.Sound(join('assets','audio','music','choose_level.mp3'))
        music.set_volume(1.0)
        music.play(loops=-1)

        # Change the background to be the loading world screen 
        # background
        background = self.textures["play_bg"]
        
        # Set the WorldButton timer to start
        self.timerData_AfterPlayBtn["last_time"] = pygame.time.get_ticks()

        keepRunning = True
        while keepRunning:

            # Get the current time for the world buttons
            self.timerData_AfterPlayBtn["current_time"] = pygame.time.get_ticks()

            # Create a scaled background variable that is basically
            # a copy of the start_game_panorama but scaled, uses the WIDTH and HEIGHT to
            # scale correctly
            scaled_background = scale_background(background, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            # Render the background first 
            self.SCREEN.blit(scaled_background, (0, 0))

            # 'Choose Level' text
            # Create the Menu TITLE
            MENU_TEXT = get_font(100).render("CHOOSE LEVEL", True, "#FFFFFF")
            MENU_RECT = MENU_TEXT.get_rect(center=(WINDOW_WIDTH/2, ( 0 + (WINDOW_HEIGHT * 0.12))))
            # This is the shadow of the meny title
            MENU_SHADOW = get_font(100).render("CHOOSE LEVEL", True, "#060608")
            MENU_SHADOW_RECT = MENU_SHADOW.get_rect(center=(WINDOW_WIDTH/2 + 12, ( 0 + (WINDOW_HEIGHT * 0.1325)) ))

            # Render the Title and its shadow
            self.SCREEN.blit(MENU_SHADOW, MENU_SHADOW_RECT) 
            self.SCREEN.blit(MENU_TEXT, MENU_RECT) 

            # Get the mouse position
            MOUSE_POS = pygame.mouse.get_pos()

            # Define and create the back button
            BACK_BUTTON_IMG = self.textures["BACK_BUTTON_IMG"]
            BACK_BUTTON_HOVER_IMG = self.textures["BACK_BUTTON_HOVER_IMG"]

            BACK_BUTTON = Button(image=BACK_BUTTON_IMG, pos=(WINDOW_WIDTH - ( WINDOW_WIDTH * 0.935), WINDOW_HEIGHT - ( WINDOW_HEIGHT * 0.90)), 
                                text_input="", font=get_font(75), base_color="White", hovering_color="White", imageScale=6)

            # Set the hover image (as of 17/feb/2025,12:32am, the hovering function is "inverted" with the regular image)
            BACK_BUTTON.setHoverImg(BACK_BUTTON_HOVER_IMG)

            # Create the buttons that open the worlds
            self.worldButtons(music)

            # Create the buttons that delete the worlds
            self.deleteButtons()

            # event loop 
            for event in pygame.event.get():

                # Quit detection
                if event.type == pygame.QUIT:
                    keepRunning = False

                # Check if the player is touching the back button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(MOUSE_POS):
                        music.fadeout(100)
                        self.main_menu()
                        # Go back to Cycle 1a.
                        keepRunning = False

            # draw the back button
            BACK_BUTTON.changeColor(MOUSE_POS)
            BACK_BUTTON.update(self.SCREEN)

            pygame.display.update()

        return False

    def main_menu(self):

        # Start playing the Startup Music
        startup_music = pygame.mixer.Sound(join('assets','audio','music','menu.mp3'))
        startup_music.set_volume(0.5)
        startup_music.play(loops=-1)

        # Startup
        start_game_panorama = pygame.image.load(join('assets','images','gui','start_game_panorama.png')).convert_alpha()

        while True:

            # Create a scaled background variable that is basically
            # a copy of the start_game_panorama but scaled, uses the WIDTH and HEIGHT to
            # scale correctly
            scaled_background = scale_background(start_game_panorama, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            # Render the background first 
            self.SCREEN.blit(scaled_background, (0, 0))

            # Button Magic Stuff 
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            # Create the Menu TITLE
            MENU_TEXT = get_font(100).render("Biome Generator", True, "#FFFFFF")
            MENU_RECT = MENU_TEXT.get_rect(center=(WINDOW_WIDTH/2, 100))
            # This is the shadow of the meny title
            MENU_SHADOW = get_font(100).render("Biome Generator", True, "#060608")
            MENU_SHADOW_RECT = MENU_SHADOW.get_rect(center=(WINDOW_WIDTH/2 + 10, 110))

            # Render the Title and its shadow
            self.SCREEN.blit(MENU_SHADOW, MENU_SHADOW_RECT) 
            self.SCREEN.blit(MENU_TEXT, MENU_RECT) 

            # Play Button that is used to open up the game
            PLAY_BUTTON = Button(pygame.image.load(join('assets','images','gui','play_buttonwtext_hover.png')).convert_alpha(), pos=(WINDOW_WIDTH/2, 0 + (WINDOW_HEIGHT * 0.40)), 
                                text_input="", font=get_font(75), base_color="White", hovering_color="#e3e6ff", imageScale=7)
            PLAY_BUTTON.setHoverImg(pygame.image.load(join('assets','images','gui','play_buttonwtext.png')))

            # Stops the game and closes the window
            QUIT_BUTTON = Button(image=pygame.image.load(join('assets','images','gui','quit_game_buttonwtext_hover.png')).convert_alpha(), pos=(WINDOW_WIDTH/2, 0 + (WINDOW_HEIGHT * 0.70)), 
                                text_input="", font=get_font(75), base_color="White", hovering_color="#e3e6ff", imageScale=7)
            QUIT_BUTTON.setHoverImg(pygame.image.load(join('assets','images','gui','quit_game_buttonwtext.png')).convert_alpha())

            

            # For each button (for now, the Play & Quit)
            # check if the text has to change colors or if
            # the image it uses has to change 
            # Then, render the buttons onto the screen
            for button in [PLAY_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.SCREEN)
            
            # Button Magic ends here :(

            # Look for any user clicks.
            # If the user clicks on play, execute the 2a. Main Loop
            for event in pygame.event.get():
                # Quit if the user want to (sad, very sad )
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Checks if the mouse is clicking
                # If so, then check if it is clicking a button
                # and act accordingly
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        startup_music.fadeout(100)
                        self.play()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        startup_music.fadeout(100)
                        self.quit()
                # Check for a screen resize event
                if event.type == pygame.VIDEORESIZE:  # Handle window resizing
                    WIDTH, HEIGHT = event.size
                    self.SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    
            # Update the screen
            pygame.display.update()

    # This will hold the main cycle of the game
    def run(self):
        # 1a Main Cycle
        self.main_menu()
        pygame.quit()
        sys.exit()

# If file is main then run this
if __name__ == '__main__': 
    game = Game()
    game.run()

