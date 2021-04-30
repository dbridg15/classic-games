"""
flappy bird game using object-oriented approach
signigicant inspiration from https://github.com/attreyabhatt/Flappy-Bird-Pygame
"""
import random

import pygame

from shapely.geometry import Polygon

from base import GameOver, BaseConfig, BaseGame


class FlappyConfig(BaseConfig):
    """configurations for flappy-bird game"""

    NAME: str = 'Flappy Bird'
    SPEED: int = 80

    FONT_COLOUR =  (255, 255, 255)
    BLOCKS_COLOUR: tuple = (30, 220, 30)
    BACKGROUND_COLOUR: tuple = (60, 60, 255)

    GAME_WIDTH: int= 800
    GAME_HEIGHT: int = 500

    BLOCK_WIDTH: int = 50
    BLOCK_BASE_SPEED: int = 5
    BLOCK_MAX_SPEED: int = 17
    BLOCK_SPEED_INCREMENT: int = 2  # increment speed every time score increase

    BIRD_V_SPEED: int = 5  # speed bird move vertically

    GAP_MAX_MULTIPLIER: float = 6.0
    GAP_MIN_MULTIPLIER: float = 2.5 # min size of gap (times bird height)
    GAP_DEINCREMENT_MULTIPLIER: float = 0.1

    BIRD_IMG: str = 'assets/flap.png'



class Bird:
    """flappy bird"""

    def __init__(self, config: FlappyConfig) -> None:
        """instantiate a bird object with image and size from filepath"""

        self.config = config

        self.img = pygame.image.load(self.config.BIRD_IMG)
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]

        self.x = int(0.2 * self.config.GAME_WIDTH)  # x location never changes
        self.y = int(0.4 * self.config.GAME_HEIGHT)

    @property
    def location(self) -> tuple[float, float]:
        """bird location, bottom left corner"""
        return self.x, self.y

    @property
    def polygon(self) -> Polygon:
        """Polygon object outling birds location"""
        return Polygon([(self.x, self.y),
                        (self.x, self.y + self.height),
                        (self.x + self.width, self.y + self.height),
                        (self.x + self.width, self.y)])

    def move_down(self) -> None:
        """move bird down"""
        self.y += self.config.BIRD_V_SPEED

    def move_up(self) -> None:
        """move bird up"""
        self.y -= self.config.BIRD_V_SPEED

    def draw(self, surface: pygame.Surface) -> None:
        """draw bird onto pygame surface"""
        surface.blit(self.img, self.location)

class Blocks:
    """blocks!"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, bird_height: float, config: FlappyConfig) -> None:
        """instantiate bird object"""
        self.config = config

        self._bird_height = bird_height

        self.x = self.config.GAME_WIDTH
        # y0 is the bottom of the bottom block so always zero
        # y1 is the top of the bottom block, start so gap is at center
        # y2 is the top of the top block (i.e. the top of the screen)
        self.y0 = 0
        self.y1 = int((self.config.GAME_HEIGHT/2) - (self.bird_height/2))
        self.y2 = self.config.GAME_HEIGHT

        self.set_speed_and_size(0)

    @property
    def bird_height(self) -> int:
        """height of bird in pixels"""
        return self._bird_height

    @property
    def width(self) -> int:
        """width of blocs in pixels"""
        return self.config.BLOCK_WIDTH

    @property
    def colour(self) -> tuple[int, int, int]:
        """colour of blocks RGB"""
        return self.config.BLOCKS_COLOUR

    @property
    def speed(self) -> float:
        """speed of blocks"""
        return self._speed

    @property
    def gap_size(self) -> int:
        """size of gap between blocks"""
        return self._gap_size

    @property
    def base_speed(self) -> int:
        """the base speed of the blocks"""
        return self.config.BLOCK_BASE_SPEED

    @property
    def max_speed(self):
        """the max speed of blocks"""
        return self.config.BLOCK_MAX_SPEED

    @property
    def speed_increment(self):
        """rate at which to increase block speed with improved score"""
        return self.config.BLOCK_SPEED_INCREMENT

    @property
    def min_gap_size(self):
        """the minimum size gap between blocks can go"""
        return self.bird_height*self.config.GAP_MIN_MULTIPLIER

    @property
    def max_gap_size(self):
        """the maximum gap size between blocks (starting position)"""
        return self.bird_height*self.config.GAP_MAX_MULTIPLIER

    @property
    def deincrement_gap_size(self):
        """the amount to reduce gap size by as score increases"""
        return int(self.bird_height*self.config.GAP_DEINCREMENT_MULTIPLIER)

    def set_speed_and_size(self, score: int) -> None:
        """
        set the speed block speed and gap_size based on score

        Parameters
        ----------
        score : int
            score, higher values result in smaller gap_size and higher speed
        """

        if score == 0:
            self._speed = self.base_speed
            self._gap_size = self.max_gap_size
        else:
            if self.speed <= self.max_speed:
                self._speed = self.base_speed + (score // self.speed_increment)

            if self.gap_size >= self.min_gap_size:
                self._gap_size = self.max_gap_size - (score*self.deincrement_gap_size)

    @property
    def location(self) -> tuple[list, list]:
        """
        return the location of the blocks

        Returns
        -------
        tuple[list, list]
            the location of the bottom_block and top_block respectively
            list contains items in this order:
                leftmost x
                bottom y
                width
                top
        """
        bottom_block = [self.x, self.y0, self.width, self.y1]
        top_block = [self.x, self.y1 + self.gap_size, self.width, self.y2]

        return bottom_block, top_block

    @property
    def polygon(self) -> tuple[Polygon, Polygon]:
        """
        returns the location of the blocks as two Polygon objects
        this allows for easy intersection calculations

        Returns
        -------
        tuple[Polygon, Polygon]
            Polygon representing the location of the bottom_block and
            top_block respectively
        """

        bottom_block = Polygon([(self.x, self.y0),
                                (self.x, self.y1),
                                (self.x + self.width, self.y1),
                                (self.x + self.width, self.y0)])

        top_block = Polygon([(self.x, self.y1 + self.gap_size),
                             (self.x, self.y2),
                             (self.x + self.width, self.y2),
                             (self.x + self.width, self.y1 + self.gap_size)])

        return bottom_block, top_block


    def update_location(self, score: int) -> None:
        """
        update the location of the blocks,
        or create new blocks if they have moved off the screen
        """

        self.set_speed_and_size(score)

        # if on screen, move along speed pixels
        if (self.x + self.width) > 0:
            self.x -= self.speed

        # if not on screen create new blocks on right
        else:
            self.x = self.config.GAME_WIDTH
            self.y1 = random.randint(self.gap_size,
                                     self.y2 - self.gap_size)

    def draw(self, surface: pygame.Surface) -> None:
        """draw blocks on pygame surface"""
        bottom_block, top_block = self.location
        pygame.draw.rect(surface, self.colour, bottom_block)
        pygame.draw.rect(surface, self.colour, top_block)


class FlappyGame(BaseGame):
    """the game"""

    def __init__(self, config: FlappyConfig = FlappyConfig()) -> None:
        """instantiate game"""
        self.config = config

        self.bird= Bird(self.config)
        self.blocks = Blocks(self.bird.height, self.config)
        super().__init__(self.config)

    @property
    def polygon(self) -> Polygon:
        """return game surface as a Polygon object"""
        return Polygon([(0, 0),
                        (0, self.config.GAME_HEIGHT),
                        (self.config.GAME_WIDTH, self.config.GAME_HEIGHT),
                        (self.config.GAME_WIDTH, 0)])


    def restart(self) -> None:
        """reset game to starting parameters"""
        super().restart()
        self.bird = Bird(self.config)
        self.blocks = Blocks(self.bird.height, self.config)

    def update(self, move_up: bool = False) -> None:
        """update the state of the game"""
        if move_up:
            self.bird.move_up()
        else:
            self.bird.move_down()

        self.blocks.update_location(self.score)
        self.update_score()
        self.detect_collision()

    def update_score(self) -> None:
        """increment score if bird passes blocks"""
        # increment score if the birds location is beyond the block
        # but within BIRD_SPEED (i.e. no passed last time)
        bird_x = self.bird.x
        block_x = self.blocks.x + self.blocks.width

        if block_x <= bird_x < block_x + self.blocks.speed:
            self.score += 1

        self.high_score = max(self.high_score, self.score)

    def _draw(self) -> None:
        self.blocks.draw(self.surface)
        self.bird.draw(self.surface)

    def detect_collision(self) -> None:
        """check if bird intersects with blocks or outside game surface"""
        bird_poly = self.bird.polygon
        b_block_poly, t_block_poly = self.blocks.polygon
        game_poly = self.polygon

        if ((not bird_poly.intersects(game_poly)) or
            (bird_poly.intersects(b_block_poly)) or
            (bird_poly.intersects(t_block_poly))):
            raise GameOver

    def play(self) -> None:
        """play the game"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                # keydown - when button is pressed keyup - when it's released
                move_up = (event.type == pygame.KEYDOWN and
                           event.key == pygame.K_UP)

            try:
                self.update(move_up)
            except GameOver:
                self.game_over = True
            self.draw()


if __name__ == '__main__':
    game = FlappyGame()
    game.play()
