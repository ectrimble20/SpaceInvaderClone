import random
from pygame import Rect
from pygame.math import Vector2


# Some default values, might move this into a config or something but for now, just some const definitions here
PLAYER_RECT = Rect(0, 0, 49, 37)
BADDIE_RECT = Rect(0, 0, 49, 25)


class Entity(object):

    """
    Okay, this isn't going to be a "generic" entity, this is going to be an entity specific to our uses for this game.

    It needs to handle movement, movement is defined as a direction of X and Y so just a vector.  The absolute position
    is used to control the center of the Entity which all movement will be based off of.  There will be a bounds
    function but not a bounds property, so the bounds can be changed if needed but aren't stored in the entity itself.
    We also need a Entity->Entity collision check where we pass a list of entities and return the entity(s) we've
    collided with, though we should limit this to 1 collision since this will either be the Baddies against the player,
    the baddies against lasers or the player against lasers.
    """
    def __init__(self, rect: Rect, **kwargs):
        self._rect = rect.copy()
        self._pos = Vector2(self._rect.centerx, self._rect.centery)
        self._alive = True
        self._dir = kwargs.get('direction', Vector2(1, 0))  # defaults to a rightward movement vector
        self._speed = kwargs.get('speed', 250)

    def set_direction(self, x_axis: int, y_axis: int):
        self._dir.x = x_axis
        self._dir.y = y_axis

    @property
    def alive(self):
        return self._alive

    def kill(self):
        self._alive = False

    @property
    def rect(self):
        return self._rect.copy()

    def move(self, dt):
        m_v = Vector2(self._speed * self._dir.x * dt, self._speed * self._dir.y * dt)
        self._pos += m_v
        self._rect.center = int(self._pos.x), int(self._pos.y)

    def move_by(self, x_off, y_off):
        self._pos.x += x_off
        self._pos.y += y_off
        self._rect.center = int(self._pos.x), int(self._pos.y)

    def center_at(self, pos: Vector2):
        """
        Centers an entity to a position
        :param pos: Vector2
        """
        self._pos = pos
        self._rect.center = int(pos.x), int(pos.y)

    def position_at(self, pos: Vector2):
        """
        Positions the entities from a top-left anchor point
        :param pos: Vector2
        """
        self._rect.topleft = int(pos.x), int(pos.y)
        self._pos = Vector2(self._rect.centerx, self._rect.centery)

    def clamp(self, bounds: Rect):
        realign = False
        if self._rect.left < bounds.left:
            self._rect.left = bounds.left
            realign = True
        if self._rect.right > bounds.right:
            self._rect.left = bounds.left
            realign = True
        if self._rect.top < bounds.top:
            self._rect.left = bounds.left
            realign = True
        if self._rect.bottom > bounds.bottom:
            self._rect.left = bounds.left
            realign = True
        if realign:
            self._pos = Vector2(self._rect.centerx, self._rect.centery)

    def collides_with(self, entities: list):
        for entity in entities:
            if self._rect.colliderect(entity.rect):
                return entity
        return None

    def update(self, **kwargs):
        pass


class Baddie(Entity):

    def __init__(self, rect: Rect, parent, **kwargs):
        super().__init__(rect, **kwargs)
        self._parent = parent  # BaddieGroup, it needs to follow it's movement

    def update(self):
        pass


class BaddieGroup(object):
    """
    #TODO okay so far, this is working how the old one worked, but is a lot cleaner.  We need to make the baddies move
    with the container though, this shouldn't be too hard, probably just calculate the movement offset finalized after
    adjusting for bounds and pass that offset to each baddie using the move method to readjust each position.
    """

    def __init__(self, pos: Vector2, group_rows: int, row_size: int, group_speed: int):
        self._pos = Vector2(pos.x, pos.y)
        self._gr = group_rows
        self._rs = row_size  # total size is gs * 3, the size indicates a single row of enemies
        self._speed = group_speed
        self._fire_rate = 2.5  # base fire speed, this is modified by level
        self._container = Rect(0, 0, self._rs*BADDIE_RECT.w, BADDIE_RECT.h*self._gr)
        self._container.midtop = int(self._pos.x), int(self._pos.y)
        # starting X/Y positions for each baddie
        self._baddies = []
        s_y = self._container.top
        for _ in range(self._gr):
            s_x = self._container.left  # always start at the left most position
            for _ in range(self._rs):
                baddie = Baddie(BADDIE_RECT.copy(), self)
                baddie.position_at(Vector2(s_x, s_y))
                self._baddies.append(baddie)
                s_x += BADDIE_RECT.w  # move right by the width
            s_y += BADDIE_RECT.h  # move down by the height
        # at this point we should have a nice little group of baddies in formation
        self._dir = Vector2(1, 0)  # always start by moving to the right
        self._cur_y_stop = self._container.bottom + BADDIE_RECT.h
        self._next_x_movement = -1

    @property
    def container(self):
        return self._container.copy()

    def walk(self):
        for baddie in self._baddies:
            yield baddie

    def update(self, dt, bounds):
        m_v = Vector2(self._dir.x * dt * self._speed, self._dir.y * dt * self._speed)
        old_pos = Vector2(self._pos)
        self._pos += m_v
        self._container.midtop = int(self._pos.x), int(self._pos.y)
        # if we're moving right
        if self._dir.x == 1:
            # if we've hit/cross the bounds
            if self._container.right > bounds.right:
                self._container.right = bounds.right
                self._dir.x = 0  # stop X movement
                self._dir.y = 1  # start downward movement
                self._pos = Vector2(self._container.centerx, self._container.top)
        # elif we're moving left
        elif self._dir.x == -1:
            # if we've hit/crossed the bounds
            if self._container.left < bounds.left:
                # reposition, stop X movement and start Y movement
                self._container.left = bounds.left
                self._dir.x = 0
                self._dir.y = 1
                self._pos = Vector2(self._container.centerx, self._container.top)
        # elif we're moving down
        elif self._dir.y == 1:
            if self._container.bottom > self._cur_y_stop:
                self._container.bottom = self._cur_y_stop
                self._cur_y_stop = self._container.bottom + BADDIE_RECT.h
                self._dir.y = 0
                self._dir.x = self._next_x_movement
                self._next_x_movement *= -1  # reverse next X axis
                self._pos = Vector2(self._container.centerx, self._container.top)
        mv_x = self._pos.x - old_pos.x
        mv_y = self._pos.y - old_pos.y
        for baddie in self._baddies:
            baddie.move_by(mv_x, mv_y)
