""" Define the game entity """

from __future__ import annotations

import copy
from typing import Optional, Type, Tuple, TypeVar, TYPE_CHECKING

from render_order import RenderOrder

# Maybe use this, idk man.
if TYPE_CHECKING:
    from components.ai_component import BaseAI
    from components.fighter_component import Fighter
    from game_map import GameMap

# from game_map import GameMap
# from components.ai_component import BaseAI
# from components.fighter_component import Fighter

T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent entity in the game like player, enemy, item.
    """
    game_map : GameMap
    def __init__(
            self,
            gamemap: Optional[GameMap] = None,
            x: int = 0, 
            y: int = 0, 
            char: str = "?", 
            color: Tuple[int, int, int] = (255, 255, 255),
            name = "entity name here",
            blocks_movement = False,
            render_order: RenderOrder = RenderOrder.CORPSE,
            ):
        self.x = x
        self.y = y
        # Char that use to Represent this entity.
        self.char = char
        # Tuple use to define RGB Color to render the entity.
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if gamemap:
            self.game_map = gamemap
            self.game_map.entities.add(self)

    def spawn_copy(self: T, game_map : GameMap, x : int, y : int):
        """ Spawn a copy of this instance at the given location on the game map. """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.game_map = game_map
        game_map.entities.add(clone)
        return clone

    def place_at(self, x: int, y: int, game_map: Optional[GameMap] = None) -> None:
        """ Place this entity at the given location. """
        self.x, self.y = x, y
        if game_map:
            if hasattr(self, "game_map"):
                self.game_map.entities.remove(self)
            self.game_map = game_map
            self.game_map.entities.add(self)


    def move(self, dx: int, dy: int) -> None:
        # Move the entity by dx, dy.
        self.x += dx
        self.y += dy

class Actor(Entity):
    def __init__(
            self,
            *,
            x: int = 0,
            y: int = 0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            name = "entity name here",
            ai_class: Type[BaseAI],
            fighter: Fighter,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )
        self.ai: Optional[BaseAI] = ai_class(self)
        self.fighter = fighter
        self.fighter.entity = self

    @property
    def alive(self):
        """ Return True if entity is still alive. """
        return bool(self.ai)