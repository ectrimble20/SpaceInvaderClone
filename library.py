import random
from pygame.math import Vector3, Vector2
from pygame import Rect
import assets


class GameScene(object):

    """
    GameScene framework.  A GameScene is designed as a self-contained mini-game of the main game.  Each scene should
    have it's own entities and controls for doing things.  The only required methods of the GameScene are the ones
    defined here as they are called during specific points of the game loop by the GameController
    """
    def __init__(self, game_ref):
        self.game = game_ref

    def handle_logic(self):
        """
        Logic execution.  Any logic specific actions should be handled here, this includes moving entities, handling
        interactions and other related events.
        """
        raise NotImplemented

    def handle_render(self):
        """
        Render execution.  All drawing actions should be contained here.  While the GameScene does not have a direct
        reference to the primary display, it is accessible through self.game.display and allows a scene to draw without
        needing a direct reference.
        """
        raise NotImplemented

    def on_enter(self):
        """
        Called when a scene is first entered, this occurs when a scene is set to active.  The primary purpose of this
        is to allow a scene to register any event binds it needs to in order to function.  It can also be used to
        rebuild elements in a scene when the scene is stepped back into.
        """
        pass

    def on_exit(self):
        """
        Called when a scene is being left, this occurs right before the scene is switch off.  The purpose of this is to
        allow the scene to unbind any event handlers that need to be deactivated once the scene itself is no longer
        active.
        """
        pass


class StarField(object):

    """
    Handles the StarField effect.  This spawns in and controls a number of objects that are meant to give the appearance
    of a slowly passing star field.  This is achieved by randomizing size and speed of white squares which represent a
    passing distant star.

    This could use some refactoring, though it runs efficiently enough, the rendering logic is baked in and this should
    be separated to try to maintain some semblance of SRP/SOC.
    """
    def __init__(self, screen_w, screen_h, min_stars, max_stars):
        self._w, self._h = screen_w, screen_h
        # build our initial star field
        self._star_field = []
        self._star_map = {}
        self._speed_multi = 1
        # stars are randomized
        num_stars = random.randint(min_stars, max_stars)
        for s_idx in range(num_stars):
            r_x, r_y, r_s = random.randint(0, self._w), random.randint(0, self._h), random.randint(20, 200)
            s_v = Vector3(r_x, r_y, r_s)  # we're using Z as speed cuz we're leet like that fools
            # pick a random image
            r_k = random.choice(assets.star_keys)
            self._star_map[s_idx] = r_k
            self._star_field.append(s_v)

    def set_speed_multiplier(self, value):
        self._speed_multi = value

    def handle_logic(self, dt):
        for star_vec in self._star_field:
            star_vec.y += star_vec.z * dt * self._speed_multi
            if star_vec.y > self._h:
                star_vec.y = -20
                star_vec.x = random.randint(0, self._w)

    def handle_render(self, display):
        for idx, star_vec in enumerate(self._star_field):
            display.blit(assets.images[self._star_map[idx]], (int(star_vec.x), int(star_vec.y)))


class VectorBody(object):

    """
    Represents any body that requires absolute X/Y positioning information.  This is stored in a Vector2 object, so this
    object could be considered just a wrapper for the Vector2 object, however, it does not expose the vector directly
    and keeps it in a private state to prevent unexpected changes to occur.
    """
    def __init__(self, x, y):
        self._pos = Vector2(x, y)

    @property
    def x(self):
        return self._pos.x

    @property
    def y(self):
        return self._pos.y

    def move(self, xy_off: Vector2):
        self._pos += xy_off


class Entity(VectorBody):

    def __init__(self, x, y, w, h, bounds=None):
        super().__init__(x, y)
        self._rect = Rect(x, y, w, h)
        self._bounds = bounds
        self._alive = True

    @property
    def rect(self):
        return self._rect

    def is_alive(self):
        return self._alive

    def kill(self):
        self._alive = False

    def move(self, xy_off: Vector2):
        super().move(xy_off)
        self._rect.x = int(self._pos.x)
        # revert X movement if we go out of bounds
        if self._bounds is not None:
            if 0 > self._pos.x > self._bounds.right - self._rect.w:
                self._pos.x -= xy_off.x
                self._rect.x = int(self._pos.x)
        self._rect.y = int(self._pos.y)
        if self._bounds is not None:
            # revert X movement if we go out of bounds
            if 0 > self._pos.y > self._bounds.bottom - self._rect.h:
                self._pos.y -= xy_off.y
                self._rect.y = int(self._pos.y)


class Particle(object):

    def __init__(self, x, y, **kwargs):
        self._pos = Vector2(x, y)
        self._key = "particle_" + str(random.randint(1, 4))  # build the key for use when drawing
        self._vel = kwargs.get('vel', Vector2(random.randint(-500, 500), random.randint(-500, 500)))  # randomized speed
        self._dur = kwargs.get('dur', random.randint(2, 5))  # random duration in seconds
        self._alive_time = 0.0  # counter till we're dead

    @property
    def pos(self):
        return self._pos

    @property
    def alive(self):
        return self._alive_time < self._dur

    def update(self, dt):
        if self.alive:
            self._alive_time += dt
            t_vel = Vector2(self._vel.x * dt, self._vel.y * dt)
            self._pos += t_vel

    @property
    def image_key(self):
        return self._key
