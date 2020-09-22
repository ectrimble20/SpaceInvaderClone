from library import GameScene, Particle, Entity
import assets
import eventbus
from pygame import Rect, KEYUP, KEYDOWN, K_a, K_d, K_SPACE, K_q, K_p, Vector2
# debug
from pygame.draw import rect as draw_rect


class PlayScene(GameScene):

    # TODO, we need to unify all game entities under a single entity class, we need this to prevent having to have so
    # TODO: many different kinds of entity containers and also to allow us to quickly remove many entities with a single
    # TODO: walk of the list rather than the 3 it currently has to do.
    def __init__(self, game_ref):
        super().__init__(game_ref)
        self._score = 0  # players current score
        self._level = 1  # current level
        self._lives = 3  # number of lives the player has
        self._win_level = 10  # end of the game
        self._level_speed_mult = 0.2  # they move N faster each level
        # all of these 'player_' elements should be contained in a entity
        self._player_rect = assets.images['player'].get_rect().copy()
        self._player_rect.centerx = self.game.display.get_rect().centerx
        self._player_rect.y = self.game.display.get_rect().bottom - self._player_rect.height - 20
        self._player_abs_x = float(self._player_rect.x)
        self._player_movement = 0
        self._player_speed = 250
        # player shots
        self._player_laser_speed = 500
        self._player_lasers = []
        self._particles = []
        self._fire_rate = 0.25
        self._last_fire = 0.0
        # spawn some basic enemies
        self._enemies = []
        rows = 3
        st_enemy_y = 20
        y_row_offset = assets.images['enemy'].get_rect().height + 10
        for _ in range(rows):
            st_enemy_x = self.game.display.get_rect().width - assets.images['enemy'].get_rect().width - 20
            for e_x_off in range(7):
                enemy = assets.images['enemy'].get_rect().copy()
                enemy.topleft = st_enemy_x, st_enemy_y
                self._enemies.append(enemy)
                st_enemy_x -= assets.images['enemy'].get_rect().width + 5
            st_enemy_y += y_row_offset
        # let's get a large area of movement, thought I could just pass the list to unionall but no, fuck you, doesn't
        # work.  Not sure if this is a bug or not but w/e, we'll just work around it
        # get the lead element and copy it's rect
        self._enemy_parent = self._enemies[0].copy()
        # iterate the other elements
        for e_i in range(1, len(self._enemies)):
            # then union them up gradually growing the rect
            self._enemy_parent.union_ip(self._enemies[e_i])
        # movement variables
        self._enemy_speed = 500
        self._enemy_x_step_modifier = -1
        self._enemy_move_x = self._enemy_speed * (self._level_speed_mult * self._level) * self._enemy_x_step_modifier
        self._enemy_move_y = 0
        self._enemy_pos = Vector2(self._enemy_parent.x, self._enemy_parent.y)
        self._enemy_stop_y = self._enemy_parent.y + assets.images['enemy'].get_rect().height
        self._enemy_parent_last = self._enemy_parent.copy()
        # setup info text and pad it off the top-left, then pad off each element, we can probably handle this with a
        # loop to make it more read-able.
        self._text_rect_score = assets.images['text_score_lead'].get_rect()
        self._text_rect_score.x += 20
        self._text_rect_score.y += 20
        self._text_rect_lives = assets.images['text_player_lives'].get_rect()
        self._text_rect_lives.x += 20
        self._text_rect_lives.y = self._text_rect_score.bottom + 10  # pad off the score
        self._text_rect_level = assets.images['text_player_level'].get_rect()
        self._text_rect_level.x += 20
        self._text_rect_level.y = self._text_rect_lives.bottom + 10  # pad off the score

    def handle_render(self):
        # make a copy of the laser rect so we can draw our lasers
        plr = assets.images['laser_player'].get_rect().copy()
        # for each laser, adjust the rects center to it's position and draw it there
        for p_l in self._player_lasers:
            plr.center = int(p_l.x), int(p_l.y)
            self.game.display.blit(assets.images['laser_player'], plr)
        # Draw particles
        for ptc in self._particles:
            ptc_r = assets.images[ptc.image_key].get_rect().copy()
            ptc_r.center = ptc.pos
            self.game.display.blit(assets.images[ptc.image_key], ptc_r)
        # handle player 'animation' based on movement direction
        if self._player_movement > 0:
            pik = 'player_right'
        elif self._player_movement < 0:
            pik = 'player_left'
        else:
            pik = 'player'
        # draw the enemies
        for enemy in self._enemies:
            self.game.display.blit(assets.images['enemy'], enemy)
        # draw the player with the appropriate key
        self.game.display.blit(assets.images[pik], self._player_rect)
        # draw_rect(self.game.display, (255, 255, 255), self._enemy_parent, 1)  # for debug
        # lastly, draw the info text stuff
        self.game.display.blit(assets.images['text_player_lives'], self._text_rect_lives)
        self.game.display.blit(assets.images['text_player_level'], self._text_rect_level)
        self.game.display.blit(assets.images['text_score_lead'], self._text_rect_score)
        # handle dynamic text
        p_lives = assets.fonts['small'].render(str(self._lives), True, (255, 255, 255))
        p_li_r = p_lives.get_rect()
        p_li_r.topleft = self._text_rect_lives.topright
        p_level = assets.fonts['small'].render(str(self._level), True, (255, 255, 255))
        p_lv_r = p_level.get_rect()
        p_lv_r.topleft = self._text_rect_level.topright
        p_score = assets.fonts['small'].render(str(self._score), True, (255, 255, 255))
        p_sc_r = p_score.get_rect()
        p_sc_r.topleft = self._text_rect_score.topright
        self.game.display.blit(p_lives, p_li_r)
        self.game.display.blit(p_level, p_lv_r)
        self.game.display.blit(p_score, p_sc_r)

    def handle_logic(self):
        # increment last_fire timer if needed
        if self._last_fire < self._fire_rate:
            self._last_fire += self.game.time_delta
        # move the player based on movement
        self._player_abs_x += self._player_movement * self.game.time_delta
        # keep player within the game bounds
        if self._player_abs_x < 20:
            self._player_abs_x = 20.0
        elif self._player_abs_x > self.game.display.get_rect().right - self._player_rect.width - 20:
            self._player_abs_x = self.game.display.get_rect().right - self._player_rect.width - 20
        # adjust rect to absolute position
        self._player_rect.x = int(self._player_abs_x)
        remove_pl = []
        # move player lasers, append to the remove list if they've gone off screen
        laser_move_offset = Vector2(0, -1 * self._player_laser_speed * self.game.time_delta)
        for p_l in self._player_lasers:
            p_l.move(laser_move_offset)
            # p_l.y -= self._player_laser_speed * self.game.time_delta
            if p_l.y < -33:
                remove_pl.append(p_l)
        # check for any hits
        dead_enemies = []
        for p_l in self._player_lasers:
            laser_spent = False
            for enemy in self._enemies:
                if not laser_spent:
                    if enemy.colliderect(p_l.rect):
                        if enemy not in dead_enemies:
                            dead_enemies.append(enemy)
                            for _ in range(10):
                                self._particles.append(Particle(p_l.rect.centerx, p_l.rect.top))
                        if p_l not in remove_pl:
                            remove_pl.append(p_l)
                        laser_spent = True
        # remove any lasers that have gone out of bounds or hit an enemy
        for p_l in remove_pl:
            self._player_lasers.remove(p_l)
        for d_e in dead_enemies:
            self._enemies.remove(d_e)
            self._score += 25
        # handle particle movements
        dead_particles = []
        for particle in self._particles:
            particle.update(self.game.time_delta)
            if not particle.alive:
                dead_particles.append(particle)
        for particle in dead_particles:
            self._particles.remove(particle)
        # move enemies
        self._enemy_parent_last = self._enemy_parent.copy()
        if self._enemy_move_x != 0:
            self._enemy_pos.x += self._enemy_move_x * self.game.time_delta
        if self._enemy_move_y != 0:
            self._enemy_pos.y += self._enemy_move_y * self.game.time_delta
        # need to adjust the parent rect, then make sure it stays in bounds and handles direction changes
        # then we need to move each individual enemy to follow the parent
        self._enemy_parent.x = int(self._enemy_pos.x)
        self._enemy_parent.y = int(self._enemy_pos.y)
        if self._enemy_move_x > 0:  # moving right
            # if we went over the bounds, stop X movement
            if self._enemy_parent.right > self.game.display.get_rect().right:
                self._enemy_parent.right = self.game.display.get_rect().right
                self._enemy_pos.x = float(self._enemy_parent.x)
                self._enemy_move_x = 0
                self._enemy_move_y = self._enemy_speed * (self._level_speed_mult * self._level)
        if self._enemy_move_x < 0:  # moving left
            if self._enemy_parent.x < 0:
                self._enemy_parent.x = 0
                self._enemy_pos.x = float(self._enemy_parent.x)
                self._enemy_move_x = 0
                self._enemy_move_y = self._enemy_speed * (self._level_speed_mult * self._level)
        if self._enemy_move_y > 0:  # moving down
            if self._enemy_parent.y >= self._enemy_stop_y:
                self._enemy_move_y = 0
                self._enemy_move_x = (self._enemy_speed * (self._level_speed_mult * self._level)) * self._enemy_x_step_modifier
                self._enemy_stop_y = self._enemy_parent.y + assets.images['enemy'].get_rect().height
                self._enemy_x_step_modifier *= -1
        # move each individual enemy now
        e_x, e_y = self._enemy_parent.x - self._enemy_parent_last.x, self._enemy_parent.y - self._enemy_parent_last.y
        for enemy in self._enemies:
            enemy.x += e_x
            enemy.y += e_y
        # TODO need to figure out a way to pass parameters between scenes, cuz like here we'd want to know where the
        # player was so we could move the ship from there in the transition scene rather than magically moving to the
        # center like we do now.
        if len(self._enemies) == 0:
            self.game.change_scene('level_end')

    def on_enter(self):
        eventbus.bind_listener(self.key_pressed, KEYDOWN)
        eventbus.bind_listener(self.key_released, KEYUP)

    def on_exit(self):
        eventbus.unbind_listener(self.key_pressed, KEYDOWN)
        eventbus.unbind_listener(self.key_released, KEYUP)

    def key_pressed(self, e):
        if e.key == K_q:
            self.game.change_scene('menu')
        if e.key == K_a:
            self._player_movement -= self._player_speed
        if e.key == K_d:
            self._player_movement += self._player_speed
        if e.key == K_SPACE:
            if self._last_fire >= self._fire_rate:
                self.spawn_player_laser()

    def key_released(self, e):
        if e.key == K_a:
            self._player_movement += self._player_speed
        if e.key == K_d:
            self._player_movement -= self._player_speed

    def spawn_player_laser(self):
        # self._player_lasers.append(Vector2(self._player_rect.midtop))
        l_img_r = assets.images['laser_player'].get_rect()
        l_img_r.center = self._player_rect.center
        self._player_lasers.append(Entity(l_img_r.x, l_img_r.y, l_img_r.w, l_img_r.h))

