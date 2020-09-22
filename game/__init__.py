import pygame
import eventbus
import assets
from library import StarField
from game.scenes.menu import MenuScene
from game.scenes.play import PlayScene
from game.scenes.levelend import LevelEndScene
from game.scenes.intro import IntroScene


class GameController(object):

    def __init__(self):
        self.display = pygame.display.set_mode((1200, 800))
        assets.initialize_assets()
        self._clock = pygame.time.Clock()
        self._time_delta = 0.016
        self._running = True
        self._paused = False
        self._star_field = StarField(1200, 800, 30, 50)
        self._cur_scene = ''
        self._scenes = {}
        eventbus.bind_listener(self.pause_game, pygame.KEYUP)
        eventbus.bind_listener(self.quit_game, pygame.QUIT)
        self.build_scenes()
        self._scenes[self._cur_scene].on_enter()
        self._change_scene_to = None

    def run(self):
        while self._running:
            eventbus.process_queue()
            self.display.fill((0, 0, 0))
            self._star_field.handle_logic(self.time_delta)
            self._scenes[self._cur_scene].handle_logic()
            self._star_field.handle_render(self.display)
            self._scenes[self._cur_scene].handle_render()
            pygame.display.flip()
            self._time_delta = self._clock.tick(60) / 1000
            pygame.display.set_caption(f"Space Invaders Clone [{int(self._clock.get_fps())}]")
            if self._change_scene_to is not None:
                self._scenes[self._cur_scene].on_exit()
                self._cur_scene = self._change_scene_to
                self._change_scene_to = None
                self._scenes[self._cur_scene].on_enter()

    @property
    def time_delta(self):
        return self._time_delta

    def set_star_field_speed(self, value):
        self._star_field.set_speed_multiplier(value)

    def pause_game(self, e):
        if e.key == pygame.K_p:
            self._paused = not self._paused

    def quit_game(self, *args):
        self._running = False

    def build_scenes(self):
        self._cur_scene = 'menu'
        self._scenes['menu'] = MenuScene(self)
        self._scenes['play'] = PlayScene(self)
        self._scenes['level_end'] = LevelEndScene(self)
        self._scenes['intro'] = IntroScene(self)

    def change_scene(self, to_scene):
        # quick hack to fix scene loop being stuck with the game ended
        if to_scene == 'play':
            self._scenes['play'] = None
            self._scenes['play'] = PlayScene(self)
        self._change_scene_to = to_scene
