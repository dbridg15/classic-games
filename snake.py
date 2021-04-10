# pylint: disable = no-member
"""snake game"""
import time
import random

from typing import List

import pygame
import numpy as np

GRID_SIZE = 20
GAME_SIZE = 600

FONT_COLOUR: tuple = (0, 0, 255)
BACKGROUND_COLOUR = (255, 255, 255)
SNAKE_COLOUR = (0, 0, 0)
FOOD_COLOUR = (255, 0, 0)

SMALL_FONT: tuple = ('freesansbold.ttf', 20)
LARGE_FONT: tuple = ('freesansbold.ttf', 130)

SPEED = 15

class GameOver(Exception):
    """exception to raise if game is over!"""


class GameGrid:
    """grid"""

    def __init__(self,
                 game_size: int = GAME_SIZE,
                 grid_size: int = GRID_SIZE) -> None:
        """
        initialise GridTransformer object


        Parameters
        ----------
        game_size : int, optional
            the size of the game square, by default GAME_SIZE
        grid_size : int, optional
            the number of blocks to split the game into, by default GRID_SIZE
        """

        self._game_size = game_size
        self._grid_size = grid_size
        self._block_size = game_size / grid_size

        self._set_grid()

    def _set_grid(self)-> None:
        """set grid as 2D np array of coordinates of bottom left corners"""
        vector = np.array([self.block_size * i for i in range(self.grid_size)])
        self._grid = np.array(np.meshgrid(vector, vector)).T

    def __getitem__(self, item: tuple) -> tuple:
        """return the pixel-coordinates for the given game coordinates"""
        return self._grid[item]

    @property
    def grid_size(self) -> int:
        """return the size of the grid"""
        return self._grid_size

    @property
    def block_size(self) -> int:
        """return the size of each block"""
        return self._block_size


class Food:
    """the food"""
    def __init__(self, game_grid: GameGrid) -> None:
        """initialise a food object"""
        self.colour = FOOD_COLOUR
        self.game_grid = game_grid
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
        while (loc := (random.choice(range(GRID_SIZE)),
                       random.choice(range(GRID_SIZE)))) in body:
            pass

        self._location = loc

    def draw(self, surface: pygame.Surface) -> None:
        """draw the food"""
        translated = self.game_grid[self.location]
        radius = self.game_grid.block_size/2
        center = [i+radius  for i in translated]
        pygame.draw.circle(surface,
                           self.colour,
                           center,
                           radius)


class Snake:
    """the snake"""

    def __init__(self, game_grid: GameGrid) -> None:
        """initialise a snake object"""
        self.colour = SNAKE_COLOUR
        self.game_grid = game_grid
        self.body = [(random.choice(range(GRID_SIZE)),
                      random.choice(range(GRID_SIZE)))]
        self.set_direction(pygame.K_UP)

    def draw(self, surface: pygame.Surface) -> None:
        """draw the snake"""
        for segment in self.body:
            translated = self.game_grid[segment]
            rect_coords = list(translated) + [self.game_grid.block_size]*2
            pygame.draw.rect(surface,
                             self.colour,
                             rect_coords)

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

        # so you appear on the other side of the game
        # im sure there is a better way of doing this!
        new_head = tuple(i if i < GRID_SIZE else 0 for i in new_head)
        new_head = tuple(i if i >= 0 else GRID_SIZE-1 for i in new_head)

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


class Game:
    """the game"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        """instantiate game"""
        pygame.init()
        self.surface = pygame.display.set_mode((GAME_SIZE, GAME_SIZE))
        pygame.display.set_caption('Snake')

        self.grid = GameGrid()

        self.snake = Snake(self.grid)
        self.food = Food(self.grid)

        self.score = 0
        self.high_score = 0
        self.clock = pygame.time.Clock()

        self.game_over = False

        self.draw()

    def restart(self) -> None:
        """reset game to starting parameters"""
        self.snake = Snake(self.grid)
        self.food = Food(self.grid)
        self.score = 0
        self.game_over = False


    @staticmethod
    def get_center() -> tuple[float, float]:
        """return the centre of the game"""
        return GAME_SIZE/2, GAME_SIZE/2

    def update(self) -> None:
        """update the state of th game"""
        try:
            self.snake.update_location(self.food)
            self.score = len(self.snake.body) - 1
            self.high_score = max(self.score, self.high_score)
        except GameOver:
            self.game_over = True

    def draw(self) -> None:
        """draw state of game"""
        self.surface.fill(BACKGROUND_COLOUR)
        self.snake.draw(self.surface)
        self.food.draw(self.surface)
        self.display_score()

        if self.game_over:
            self.display_game_over()
            pygame.display.update()
            time.sleep(1)
            self.replay()
            self.restart()
            self.draw()

        pygame.display.update()
        self.clock.tick(SPEED)

    @staticmethod
    def quit() -> None:
        """quit the game"""
        pygame.quit()

    def replay(self) -> None:
        """wait for user input to replay game"""
        replay = False
        while not replay:
            for event in pygame.event.get([pygame.KEYDOWN,
                                           pygame.KEYUP,
                                           pygame.QUIT]):
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    replay = True

            self.clock.tick()

    def _display_text(self,
                      text: str,
                      font: tuple[str, int],
                      center: tuple[int, int] = None,
                      colour: tuple[int, int, int] = FONT_COLOUR) -> None:
        """
        display text on the pygame surface

        Parameters
        ----------
        text : str
            the text to displat
        font : tuple[str, int]
            the font to use (font-name, size)
        center : tuple[int, int], optional
            where to centre the text, by default None
        colour : tuple[int, int, int], optional
            text colour, by default FONT_COLOUR
        """
        font = pygame.font.Font(*font)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = center
        self.surface.blit(text_surface, text_rect)

    def display_score(self) -> None:
        """display the game score"""
        self._display_text( f'Score: {self.score}', SMALL_FONT, (45, 15))

    def display_game_over(self) -> None:
        """display the game over message"""
        x, y = self.get_center()
        self._display_text('Game Over!', LARGE_FONT, (x, y-50))
        self._display_text(f'Score: {self.score} Highscore: {self.high_score}',
                           SMALL_FONT, (x, y+35))
        self._display_text('Press any key to continue.', SMALL_FONT, (x, y+75))

    def play(self):
        """the game loop"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.snake.set_direction(event.key)
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.play()
