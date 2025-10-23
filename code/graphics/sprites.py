from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

# class DamageSprite(pygame.sprite.Sprite):
#     def __init__(self, pos, image, groups):
#         super().__init__(groups)
#         self.image = pygame.image.load(join('assets','images','damage','generic','3.png')).convert_alpha()
#         self.rect = self.image.get_frect(topleft = pos)
        


    




