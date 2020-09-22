from library import GameScene, Entity, Particle
from pygame.math import Vector2
import assets
import eventbus
from pygame import K_SPACE, KEYUP
from pygame.transform import flip
import random


class IntroScene(GameScene):

    def __init__(self, game_ref):
        super().__init__(game_ref)
        self._player_speed = 250
        self._animation_finished = False
        self._stage_one = True  # start in stage one
        self._stage_two = False
        # stage one, 3 enemies will fly up running from the player
        # set the enemy starting Y positions, they need to be under the screen and offset
        e1_y = self.game.display.get_rect().bottom + 200
        e1_x = self.game.display.get_rect().centerx - 200
        e2_y = self.game.display.get_rect().bottom + 450
        e2_x = self.game.display.get_rect().centerx + 200
        e3_y = self.game.display.get_rect().bottom + 325
        e3_x = self.game.display.get_rect().centerx
        e4_y = self.game.display.get_rect().bottom + 800
        e4_x = self.game.display.get_rect().centerx
        e_rect = assets.images['enemy'].get_rect()
        p_rect = assets.images['player'].get_rect()
        self._stage_one_enemies = [
            Entity(e1_x, e1_y, e_rect.w, e_rect.h),
            Entity(e2_x, e2_y, e_rect.w, e_rect.h),
            Entity(e3_x, e3_y, e_rect.w, e_rect.h),
        ]
        self._stage_one_player = Entity(e4_x, e4_y, p_rect.w, p_rect.y)
        self._transition_timer = 2.5  # once we despawn all of stage one, we'll spawn stage two
        # stage two, several green (enemy) lasers shoot past, then the player flys by heading down chased by enemies
        # so we don't care what entities are what here
        self._stage_two_enemies = []
        self._stage_two_lasers = []
        # laser positions
        s2_lp = [
            (self.game.display.get_rect().centerx - 300, self.game.display.get_rect().top - 200),
            (self.game.display.get_rect().centerx - 100, self.game.display.get_rect().top - 300),
            (self.game.display.get_rect().centerx + 200, self.game.display.get_rect().top - 100)
        ]
        # enemy positions
        s2_ep = [
            (self.game.display.get_rect().centerx - 350, self.game.display.get_rect().top - 1000),
            (self.game.display.get_rect().centerx + 250, self.game.display.get_rect().top - 1000),
            (self.game.display.get_rect().centerx - 100, self.game.display.get_rect().top - 1000),
            (self.game.display.get_rect().centerx - 400, self.game.display.get_rect().top - 700),
            (self.game.display.get_rect().centerx - 100, self.game.display.get_rect().top - 700),
            (self.game.display.get_rect().centerx + 250, self.game.display.get_rect().top - 700),
            (self.game.display.get_rect().centerx - 400, self.game.display.get_rect().top - 500),
            (self.game.display.get_rect().centerx - 200, self.game.display.get_rect().top - 500),
            (self.game.display.get_rect().centerx + 50, self.game.display.get_rect().top - 500),
            (self.game.display.get_rect().centerx + 250, self.game.display.get_rect().top - 500)
        ]
        # load up the lasers
        laser_rect = assets.images['laser_enemy'].get_rect()
        for l_x, l_y in s2_lp:
            self._stage_two_lasers.append(Entity(l_x, l_y, laser_rect.w, laser_rect.h))
        # load up enemies
        for e_x, e_y in s2_ep:
            self._stage_two_enemies.append(Entity(e_x, e_y, e_rect.w, e_rect.h))
        # first, we have 5 lasers go flying by

    def handle_render(self):
        if self._stage_one:
            r_i = flip(assets.images['enemy'], False, True)
            for enemy in self._stage_one_enemies:
                self.game.display.blit(r_i, enemy.rect)
            self.game.display.blit(assets.images['player'], self._stage_one_player.rect)
        if self._stage_two:
            r_i = flip(assets.images['player'], False, True)
            for laser in self._stage_two_lasers:
                self.game.display.blit(assets.images['laser_enemy'], laser.rect)
            for enemy in self._stage_two_enemies:
                self.game.display.blit(assets.images['enemy'], enemy.rect)
            self.game.display.blit(r_i, self._stage_one_player.rect)

    def handle_logic(self):
        # change to main menu when we finish
        if self._animation_finished:
            self.game.change_scene('menu')
        # running stage one
        if self._stage_one:
            e_move = Vector2(0, -300 * self.game.time_delta)
            for enemy in self._stage_one_enemies:
                enemy.move(e_move)
            p_move = Vector2(0, -1 * self._player_speed * self.game.time_delta)
            self._stage_one_player.move(p_move)
            # once the player leaves the screen, scene one ends
            if self._stage_one_player.rect.top < -100:
                self._stage_one = False
                self._stage_two = True
        # running state two
        if self._stage_two:
            if self._transition_timer > 0.0:
                self._transition_timer -= self.game.time_delta
            else:
                l_move = Vector2(0, 500 * self.game.time_delta)
                for laser in self._stage_two_lasers:
                    laser.move(l_move)
                e_move = Vector2(0, 250 * self.game.time_delta)
                for enemy in self._stage_two_enemies:
                    enemy.move(e_move)
                p_move = Vector2(0, self._player_speed * self.game.time_delta)
                self._stage_one_player.move(p_move)

    def handle_key_up(self, e):
        # so we can get back while testing
        if e.key == K_SPACE:
            self.game.change_scene('menu')

    def on_enter(self):
        eventbus.bind_listener(self.handle_key_up, KEYUP)

    def on_exit(self):
        eventbus.unbind_listener(self.handle_key_up, KEYUP)
