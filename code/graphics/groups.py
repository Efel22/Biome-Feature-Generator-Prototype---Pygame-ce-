from settings import *
import pygame

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self,target_pos, updateFrame, updateEntities, bgImg):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH /2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT /2)

        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'isGroundTile')]
        # object_sprites = [sprite for sprite in self if not hasattr(sprite, 'isGroundTile')]
        object_sprites = [sprite for sprite in self if hasattr(sprite, 'isObjectTile')]
        animated_sprites = [sprite for sprite in self if hasattr(sprite, 'isAnimated')]
        player_sprites = [sprite for sprite in self if hasattr(sprite, 'isPlayer')]
        entity_sprites = [sprite for sprite in self if hasattr(sprite, 'isEntity')]
        damage_sprites = [sprite for sprite in self if hasattr(sprite, 'isDamageSprite')]

        if updateFrame:
            for sprite in animated_sprites:
                sprite.updateFrame()

        if updateEntities:
            for sprite in player_sprites:
                sprite.updatePlayerFrame()

        # Render the background first 
        self.display_surface.blit(bgImg, (0, 0))

        for layer in [ground_sprites, object_sprites, player_sprites, entity_sprites]:
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        # for layer in [player_sprites, entity_sprites]:
        #     for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
        #         self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        # for layer in [damage_sprites]:
        #     for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
        #         # sprite.checkForRemoval()
        #         self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
                