from library import GameScene, Entity, Particle
from pygame.math import Vector2
import assets
import eventbus
from pygame import K_SPACE, KEYUP
import random


class LevelEndScene(GameScene):

    def __init__(self, game_ref):
        super().__init__(game_ref)
        self._player_speed = 250
        self._player = Entity(1, 1, 1, 1)
        self._warp_ramp_up = 0
        self._warp_ramp_speed = 0.1  # how fast we increase the star field speed
        self._animation_finished = False
        self._particle_step = 0.03
        self._particle_timer = 0.0
        self._particles = []
        self._msg_loc_x = self.game.display.get_rect().centerx
        self._msg_loc_y = self.game.display.get_rect().bottom - 100
        self._msg_box = assets.images['text_space_to_continue'].get_rect()
        self._msg_box.midbottom = self._msg_loc_x, self._msg_loc_y

    def handle_render(self):
        for ptc in self._particles:
            ptc_r = assets.images[ptc.image_key].get_rect().copy()
            ptc_r.center = ptc.pos
            self.game.display.blit(assets.images[ptc.image_key], ptc_r)
        if self._animation_finished:
            self.game.display.blit(assets.images['text_space_to_continue'], self._msg_box)
        else:
            self.game.display.blit(assets.images['player'], self._player.rect)

    def handle_logic(self):
        # clean up particles
        dead_particles = []
        if self._particles:
            for particle in self._particles:
                if not particle.alive:
                    dead_particles.append(particle)
        if dead_particles:
            for particle in dead_particles:
                self._particles.remove(particle)
        for particle in self._particles:
            particle.update(self.game.time_delta)
        if not self._animation_finished:
            self._particle_timer += self.game.time_delta
            y_off = -1 * self._player_speed * self.game.time_delta
            self._player.move(Vector2(0, y_off))
            if self._particle_timer > self._particle_step:
                self._particle_timer -= self._particle_step
                psx, psy = self._player.rect.centerx, self._player.rect.bottom
                for _ in range(random.randint(2, 5)):
                    rv = random.randint(0, 30) - 15
                    self._particles.append(Particle(psx, psy, vel=Vector2(rv, 250)))
            # stop the scene once we move up
            if self._player.rect.bottom < -500:
                self._animation_finished = True

    def handle_key_next_level(self, e):
        # prevent hitting space until we've finished the transition
        if self._animation_finished:
            if e.key == K_SPACE:
                self.game.change_scene('menu')  # TODO this should link back to the Play scene once we get that working

    def on_enter(self):
        eventbus.bind_listener(self.handle_key_next_level, KEYUP)
        pr = assets.images['player'].get_rect().copy()
        pr.centerx = self.game.display.get_rect().centerx
        pr.y = self.game.display.get_rect().bottom - pr.height - 20
        self._player = Entity(pr.x, pr.y, pr.w, pr.h)
        self._particles.clear()

    def on_exit(self):
        eventbus.unbind_listener(self.handle_key_next_level, KEYUP)
        self._particles.clear()
        self._animation_finished = False
