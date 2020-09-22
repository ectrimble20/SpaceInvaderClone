import pygame
from game import GameController


pygame.init()
space_invaders = GameController()
space_invaders.run()
pygame.quit()
