import pygame
from local import *

images = {}
fonts = {}
star_keys = []


def initialize_assets():
    # Create font objects to make images for the UI
    fonts['large'] = pygame.font.SysFont('Arial', 48)
    fonts['small'] = pygame.font.SysFont('Arial', 16)

    # load image assets into image dict
    images['enemy'] = pygame.image.load(os.path.join(IMAGE_DIR, 'enemyShip.png')).convert_alpha()
    # images['enemy_boss'] = pygame.image.load(os.path.join(IMAGE_DIR, 'enemyShip.png')).convert_alpha()
    images['player'] = pygame.image.load(os.path.join(IMAGE_DIR, 'player.png')).convert_alpha()
    images['player_left'] = pygame.image.load(os.path.join(IMAGE_DIR, 'playerLeft.png')).convert_alpha()
    images['player_right'] = pygame.image.load(os.path.join(IMAGE_DIR, 'playerRight.png')).convert_alpha()
    images['laser_player'] = pygame.image.load(os.path.join(IMAGE_DIR, 'laserRed.png')).convert_alpha()
    images['laser_enemy'] = pygame.image.load(os.path.join(IMAGE_DIR, 'laserGreen.png')).convert_alpha()
    images['text_new_game'] = fonts['large'].render('New Game', True, (255, 255, 255))
    images['text_new_game_h'] = fonts['large'].render('New Game', True, (255, 255, 0))
    images['text_quit_game'] = fonts['large'].render('Quit Game', True, (255, 255, 255))
    images['text_quit_game_h'] = fonts['large'].render('Quit Game', True, (255, 255, 0))
    images['text_score_lead'] = fonts['small'].render('Score: ', True, (255, 255, 255))
    images['text_player_lives'] = fonts['small'].render('Lives: ', True, (255, 255, 255))
    images['text_player_level'] = fonts['small'].render('Level: ', True, (255, 255, 255))
    images['text_space_to_continue'] = fonts['small'].render('[ Press Space To Continue ]', True, (225, 225, 225))

    # make some "stars"
    for i in range(1, 4):
        s = pygame.Surface((i*2, i*2), pygame.SRCALPHA)
        s.fill((225, 225, 255))
        k = 'star_' + str(i)
        star_keys.append(k)
        images[k] = s

    # particle colors to use
    particle_colors = {
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'grey': (125, 125, 125),
        'yellow': (255, 255, 0)
    }

    for i in range(1, 5):
        p = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
        p.fill((255, 0, 0))
        k = f'particle_{str(i)}'
        images[k] = p

    # red particles
    for i in range(1, 5):
        for k, c in particle_colors.items():
            p = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
            p.fill(c)
            k = 'particle_' + str(k) + '_' + str(i)
            images[k] = p
