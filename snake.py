# pylint: disable = no-member
"""snake game"""
import random

from typing import List

import pygame
import numpy as np

from base import BaseGame, GameOver, BaseConfig
from grid import Grid


class SnakeConfig(BaseConfig):
    """configurations for snake game"""

    NAME = 'Snake'
    SPEED = 15
    BACKGROUND_COLOUR = (255, 255, 255)
    FONT_COLOUR: tuple = (0, 0, 255)

    GAME_WIDTH: int = 600
    GAME_HEIGHT: int = 600

    BLOCK_SIZE: int = 30

    SNAKE_COLOUR: tuple = (0, 0, 0)
    FOOD_COLOUR: tuple = (255, 0, 0)


class Food:
    """the food"""
    def __init__(self, grid: Grid, colour: tuple[int, int, int]) -> None:
        """initialise a food object"""
        self.grid = grid
        self.colour = colour
        self.set_location([(0, 0)])

    @property
    def location(self) -> tuple:
        """the coordiates of the food"""
        return self._location

    def set_location(self, body: List[tuple]) -> None:
        """
        set a new location for the food
        ensures this falls within the game-grid and does not overlap with the
        snake
        """
        while (loc := (random.choice(range(self.grid.width)),
                       random.choice(range(self.grid.height)))) in body:
            pass

        self._location = loc

    def draw(self, surface: pygame.Surface) -> None:
        """draw the food"""
        translated = self.grid[self.location]
        radius = self.grid.block_size/2
        center = [i+radius  for i in translated]
        pygame.draw.circle(surface,
                           self.colour,
                           center,
                           radius)


class Snake:
    """the snake"""

    def __init__(self, grid: Grid, colour: tuple[int, int, int]) -> None:
        """initialise a snake object"""
        self.colour = colour
        self.grid = grid
        self.body = [(random.choice(range(self.grid.width)),
                      random.choice(range(self.grid.height)))]
        self.set_direction(pygame.K_UP)

    def draw(self, surface: pygame.Surface) -> None:
        """draw the snake"""
        for segment in self.body:
            translated = self.grid[segment]
            rect_coords = list(translated) + [self.grid.block_size]*2
            pygame.draw.rect(surface,
                             self.colour,
                             rect_coords)

    @staticmethod
    def _check_wrap(loc: int, no_blocks: int):
        """
        check if an index is outside the range of blocks and so should wrap
        to the other side

        Parameters
        ----------
        loc : int
            the location
        no_blocks : int
            the max number of blocks

        Returns
        -------
        int
            new location
        """
        if loc < 0:
            loc = no_blocks-1
        elif loc >= no_blocks:
            loc = 0
        return loc

    def update_location(self, food: Food) -> None:
        """
        update the location of the snake based on direction
        increase length if new location intersects with food
        raise GameOver if new location intersects with existing body
        """

        head = self.body[0]

        lookup = {pygame.K_DOWN: (head[0], head[1]+1),
                  pygame.K_UP: (head[0], head[1]-1),
                  pygame.K_LEFT: (head[0]-1, head[1]),
                  pygame.K_RIGHT: (head[0]+1, head[1])}

        new_head = lookup[self.direction]

        new_x, new_y = new_head
        new_x = self._check_wrap(new_x, self.grid.width)
        new_y = self._check_wrap(new_y, self.grid.height)
        new_head = (new_x, new_y)

        self.body.insert(0, new_head)

        if new_head == food.location:
            food.set_location(self.body)
        else:
            _ = self.body.pop()

        if new_head in self.body[1:]:
            raise GameOver()

    @property
    def direction(self) -> int:
        """direction snake is moving in"""
        return self._direction

    def set_direction(self, direction: int) -> None:
        """
        set the direction of the snake
        maintain current direction if attempts to go in opposite direction
        """
        check_dict = {pygame.K_DOWN: np.array([0, 1]),
                      pygame.K_UP: np.array([0, -1]),
                      pygame.K_LEFT: np.array([-1, 0]),
                      pygame.K_RIGHT: np.array([1, 0])}

        if direction not in check_dict.keys():
            return None

        if len(self.body) > 1:
            # check the second index of the snake to stop going back on itself
            head = np.array(self.body[0]) + check_dict.get(direction)
            check = np.array(self.body[1])

            if (check == head).all():
                return None

        self._direction = direction
        return None


class SnakeGame(BaseGame):
    """the game"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, config: SnakeConfig = SnakeConfig()) -> None:
        """instantiate game"""

        self.config = config
        self.grid = Grid(self.config.GAME_WIDTH,
                         self.config.GAME_HEIGHT,
                         self.config.BLOCK_SIZE)
        self.snake = Snake(self.grid, self.config.SNAKE_COLOUR)
        self.food = Food(self.grid, self.config.FOOD_COLOUR)
        super().__init__(self.config)

    def restart(self) -> None:
        """reset game to starting parameters"""
        super().restart()
        self.snake = Snake(self.grid, self.config.SNAKE_COLOUR)
        self.food = Food(self.grid, self.config.FOOD_COLOUR)

    def update(self) -> None:
        """update the state of th game"""
        self.snake.update_location(self.food)
        self.score = len(self.snake.body) - 1
        self.high_score = max(self.score, self.high_score)

    def _draw(self) -> None:
        """draw state of game"""
        self.snake.draw(self.surface)
        self.food.draw(self.surface)

    def play(self):
        """the game loop"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.snake.set_direction(event.key)
            try:
                self.update()
            except GameOver:
                self.game_over = True
            self.draw()



if __name__ == '__main__':
    game = SnakeGame()
    game.play()
