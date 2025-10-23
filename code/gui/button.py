from settings import *
import json
import shutil  # For deleting directories

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color, imageScale):
		self.imageScale = imageScale

		self.ogimage = image
		self.image = image
		self.hovering_image = image

		self.x_pos = pos[0]
		self.y_pos = pos[1]

		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		
		self.image = pygame.transform.scale_by(self.image, imageScale)
		# Assign the hovering image be the same image for now
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def setHoverImg(self, hoverImg):
		self.hovering_image = hoverImg

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
			self.image = pygame.transform.scale_by(self.ogimage, self.imageScale)

		else:
			self.text = self.font.render(self.text_input, True, self.base_color)
			self.image = pygame.transform.scale_by(self.hovering_image, self.imageScale)

# Returns the Generic Game Font in the requested size 
def get_font(size): 
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..'))
    return pygame.font.Font(join('assets','font','gen.ttf'), size)

class WorldButton:
    def __init__(self, x, y, width, height, index, border_color="#bc4a9b", body_color="#793a80", text_color="white"):
        self.index = index # This is the index of the world that it is interacting with
        self.rect = pygame.Rect(x, y, width, height)  # Button position and size
        self.world_name = self.find_level_name()  # Name of the world
        self.last_played = self.find_level_last_played()  # Time last played

        if not self.level_exists():
             self.world_name = "Click Here"
             self.last_played = "to create a new level"
             body_color = "#403353"
             border_color = "#242234"
        else:
            self.world_name = self.find_level_name()  # Name of the world
            self.last_played = "Last Played:" + str(self.find_level_last_played())  # Time last played

        self.font = get_font(28)  # Font for the text
        self.lpfont = get_font(18)  # Font for the last played text
        self.border_color = pygame.Color(border_color)  # Border color
        self.body_color = pygame.Color(body_color)  # Main body color
        self.text_color = pygame.Color(text_color)  # Text color
        self.hovered = False  # Hover state

    def draw(self, screen):
        """
        Draw the button on the given screen.
        Args:
            screen (pygame.Surface): The surface to draw the button on.
        """

        if not self.level_exists():
            if self.hovered:
                self.border_color = "#FFFFFF"
                self.text_color = "#ffd541"
            else: 
                self.border_color = "#242234"
                self.text_color = "white"
        else:
            if self.hovered:
                self.border_color = "#FFFFFF"
                self.text_color = "#ffd541"
            else: 
                self.border_color = "#bc4a9b"
                self.text_color = "white"

        # Draw the border
        pygame.draw.rect(screen, self.border_color, self.rect, 15)  # 5px border

        # Draw the main body
        body_rect = self.rect.inflate(-25, -25)  # Shrink the body to fit inside the border
        pygame.draw.rect(screen, self.body_color, body_rect)

        text_surface1 = self.font.render(self.world_name, True, self.text_color)
        text_surface2 = self.lpfont.render(self.last_played, True, self.text_color)

        # Position the text in the center of the button
        text_rect1 = text_surface1.get_rect(center=(self.rect.centerx, self.rect.centery - 35))
        text_rect2 = text_surface2.get_rect(center=(self.rect.centerx, self.rect.centery + 35))

        # Draw the text
        screen.blit(text_surface1, text_rect1)
        screen.blit(text_surface2, text_rect2)

    def level_exists(self):
        levels_dir = "levels"
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)  # Load JSON data
                    
                    # Check if 'index' key exists and matches target_index
                    if isinstance(data, dict) and "index" in data:
                        if data["index"] == self.index:
                            return True  # Level exists

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return False  # Level not found

    def find_level_last_played(self):
        levels_dir = "levels"
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)  # Load JSON data
                    
                    # Check if 'index' key exists and matches target_index
                    if isinstance(data, dict) and "index" in data and "last_time_played" in data:
                        if data["index"] == self.index:
                            return data["last_time_played"]  # Return last time played as a string

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return None  # Return None if no matching level is found

    def find_level_name(self):
        levels_dir = "levels"
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)  # Load JSON data
                    
                    # Check if 'index' key exists and matches target_index
                    if isinstance(data, dict) and "index" in data and "name" in data:
                        if data["index"] == self.index:
                            return data["name"]  # Return level name as a string

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return None  # Return None if no matching level is found

    def update_level_last_played(self):
        levels_dir = "levels"

        currentTime = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)  # Load JSON data
                    
                    # Check if 'index' key exists and matches target_index
                    if isinstance(data, dict) and "index" in data and "last_time_played" in data:
                        if data["index"] == self.index:
                            data["last_time_played"] = currentTime  # Set the target string as the last played time

                            # Write the updated data back to the file
                            with open(file_path, "w", encoding="utf-8") as file:
                                json.dump(data, file, ensure_ascii=False, indent=4)
                            
                            return True  # Return True if the update was successful

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {file_path}")
                except Exception as e:
                    print(f"Error reading or writing {file_path}: {e}")

        return False  # Return False if no matching level is found

    def check_hover(self, mouse_pos):
        """
        Check if the mouse is hovering over the button.
        Args:
            mouse_pos (tuple): The (x, y) position of the mouse.
        """
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        """
        Check if the button is clicked.
        Args:
            mouse_pos (tuple): The (x, y) position of the mouse.
            mouse_pressed (tuple): The state of the mouse buttons.
        Returns:
            bool: True if the button is clicked, False otherwise.
        """
        return self.hovered and mouse_pressed[0]  # Left mouse button
    
class DeleteWorldButton:
    def __init__(self, x, y, width, height, index, border_color="#3b1725", body_color="#73172d", text_color="white"):
        self.index = index # This is the index of the world that it is interacting with
        self.rect = pygame.Rect(x, y, width, height)  # Button position and size
        self.text = "Delete level"

        if not self.level_exists():
            body_color = "#73172d"

        self.font = get_font(28)  # Font for the text
        self.border_color = pygame.Color(border_color)  # Border color
        self.body_color = pygame.Color(body_color)  # Main body color
        self.text_color = pygame.Color(text_color)  # Text color
        self.hovered = False  # Hover state

    def draw(self, screen):
        """
        Draw the button on the given screen.
        Args:
            screen (pygame.Surface): The surface to draw the button on.
        """

        if not self.level_exists():
            if self.hovered:
                self.border_color = "#3b1725"
                self.text_color = "#ffd541"
            else: 
                self.border_color = "#3b1725"
                self.text_color = "white"
                
        else:
            self.body_color = "#73172d"

            if self.hovered:
                self.border_color = "#FFFFFF"
                self.text_color = "#ffd541"
            else: 
                self.border_color = "#3b1725"
                self.text_color = "white"

        # Draw the border
        pygame.draw.rect(screen, self.border_color, self.rect, 15)  # 5px border

        # Draw the main body
        body_rect = self.rect.inflate(-25, -25)  # Shrink the body to fit inside the border
        pygame.draw.rect(screen, self.body_color, body_rect)

        text_surface1 = self.font.render(self.text, True, self.text_color)

        # Position the text in the center of the button
        text_rect1 = text_surface1.get_rect(center=(self.rect.centerx, self.rect.centery - 0))

        # Draw the text
        screen.blit(text_surface1, text_rect1)

    def delete_level(self):
        levels_dir = "levels"
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)  # Load JSON data
                    
                    # Check if 'index' key exists and matches target_index
                    if isinstance(data, dict) and "index" in data:
                        if data["index"] == self.index:
                            # Delete the entire directory containing the level
                            print(root)
                            shutil.rmtree(root)
                            print(f"Level with index {self.index} deleted successfully.")
                            return True  # Level found and deleted

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        print(f"Level with index {self.index} not found.")
        return False  # Level not found

    def level_exists(self):
        levels_dir = "levels"
        
        for root, _, files in os.walk(levels_dir):
            if "leveldata.txt" in files:
                file_path = os.path.join(root, "leveldata.txt")

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)  # Load JSON data
                    
                    # Check if 'index' key exists and matches target_index
                    if isinstance(data, dict) and "index" in data:
                        if data["index"] == self.index:
                            return True  # Level exists

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return False  # Level not found

    def check_hover(self, mouse_pos):
        """
        Check if the mouse is hovering over the button.
        Args:
            mouse_pos (tuple): The (x, y) position of the mouse.
        """
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        """
        Check if the button is clicked.
        Args:
            mouse_pos (tuple): The (x, y) position of the mouse.
            mouse_pressed (tuple): The state of the mouse buttons.
        Returns:
            bool: True if the button is clicked, False otherwise.
        """
        return self.hovered and mouse_pressed[0]  # Left mouse button