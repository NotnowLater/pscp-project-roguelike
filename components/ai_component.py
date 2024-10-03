""" Basic AI Component to control the entity. """

from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
   from entity import Actor

class BaseAI(Action):
    entity: Actor

    def perform(self) -> None:
        raise NotImplementedError()
    
    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """ Compute and return a path to destination. Will Return an empty list if can't compute the path. """
        # Get the walkable array
        cost = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)
        for entity in self.entity.game_map.entities:
            # Check the enitiy that blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add the cost of the blocked position
                # A lower number will make the enemies crowd together
                # A higher number will make the enemies try to surround the play
                cost[entity.x, entity.y] += 10
            # Create a graph from the cost array and pass that graph to a new pathfinder.
            graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
            pathfinder = tcod.path.Pathfinder(graph)
            # Add start position
            pathfinder.add_root((self.entity.x, self.entity.y))
            # Compute the path and remove the starting position.
            path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()
            return [(index[0], index[1]) for index in path]
        
class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))
        # If close enough to player, Attack the player.
        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(target.x, target.y)
        # If Isn't close enough to player, move to player.
        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()
        # Wait if can't find a path to player
        return WaitAction(self.entity).perform()