from library import GameScene
import assets
import eventbus
from pygame import QUIT as PG_QUIT_EVENT
from pygame import MOUSEMOTION as PG_MOUSE_MOVE
from pygame import MOUSEBUTTONUP as PG_MB_RELEASE
from pygame import K_SPACE, KEYUP, K_i


class MenuScene(GameScene):

    def __init__(self, game_ref):
        super().__init__(game_ref)
        # position display rects for text
        self._new_game_rect = assets.images['text_new_game'].get_rect().copy()
        self._new_game_rect.center = self.game.display.get_rect().center
        self._new_game_rect.y -= 75
        self._quit_game_rect = assets.images['text_quit_game'].get_rect().copy()
        self._quit_game_rect.center = self.game.display.get_rect().center
        self._quit_game_rect.y += 75
        self._last_mouse_pos = 0, 0

    def handle_render(self):
        if self._new_game_rect.collidepoint(self._last_mouse_pos):
            self.game.display.blit(assets.images['text_new_game_h'], self._new_game_rect)
        else:
            self.game.display.blit(assets.images['text_new_game'], self._new_game_rect)
        if self._quit_game_rect.collidepoint(self._last_mouse_pos):
            self.game.display.blit(assets.images['text_quit_game_h'], self._quit_game_rect)
        else:
            self.game.display.blit(assets.images['text_quit_game'], self._quit_game_rect)

    def handle_logic(self):
        pass

    def log_mouse_move_pos(self, e):
        self._last_mouse_pos = e.pos

    def check_mouse_clicks(self, e):
        if self._new_game_rect.collidepoint(e.pos):
            self.game.change_scene('play')
        if self._quit_game_rect.collidepoint(e.pos):
            eventbus.post_event(eventbus.build_event(PG_QUIT_EVENT))

    def switch_to_test(self, e):
        if e.key == K_SPACE:
            self.game.change_scene('level_end')
        if e.key == K_i:
            self.game.change_scene('intro')

    def on_enter(self):
        eventbus.bind_listener(self.log_mouse_move_pos, PG_MOUSE_MOVE)
        eventbus.bind_listener(self.check_mouse_clicks, PG_MB_RELEASE)
        eventbus.bind_listener(self.switch_to_test, KEYUP)

    def on_exit(self):
        eventbus.unbind_listener(self.log_mouse_move_pos, PG_MOUSE_MOVE)
        eventbus.unbind_listener(self.check_mouse_clicks, PG_MB_RELEASE)
        eventbus.unbind_listener(self.switch_to_test, KEYUP)
