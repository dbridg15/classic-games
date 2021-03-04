"""
flappy bird game using object-oriented approach
signigicant inspiration from https://github.com/attreyabhatt/Flappy-Bird-Pygame
"""

import time
import random

import pygame

from shapely.geometry import Polygon


# settings
FONT_COLOUR: tuple = (255, 255, 255)
BLOCKS_COLOUR: tuple = (30, 220, 30)
BACKGROUND_COLOUR: tuple = (60, 60, 255)

GAME_WIDTH: int= 800
GAME_HEIGHT: int = 500

BLOCK_WIDTH: int = 50
BLOCK_STARTING_SPEED: int = 5
BLOCK_MAX_SPEED: int = 17
BLOCK_SPEED_INCREMENT: int = 3  # increment speed every time score increase by

BIRD_V_SPEED: int = 5  # speed bird move vertically

GAP_START_MULTIPLIER: float = 6.0
GAP_MIN_MULTIPLIER: float = 2.5 # min size of gap (times bird height)
GAP_DECREASE_DENOMINATOR: float = 10.0  # smaller means gap will close quicker


SMALL_FONT: tuple = ('freesansbold.ttf', 20)
LARGE_FONT: tuple = ('freesansbold.ttf', 130)


class Bird:
    """flappy bird"""

    def __init__(self, filepath: str = 'assets/flap.png') -> None:
        """instantiate a bird object with image and size from filepath"""

        self.img = pygame.image.load(filepath)
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]

        self.x = int(0.2 * GAME_WIDTH)  # x location never changes
        self.y = int(0.4 * GAME_HEIGHT)

    def get_location(self) -> tuple[float, float]:
        """return bird location, bottom left corner"""
        return self.x, self.y

    def get_polygon(self) -> Polygon:
        """return a Polygon object outling birds location"""
        return Polygon([(self.x, self.y),
                        (self.x, self.y + self.height),
                        (self.x + self.width, self.y + self.height),
                        (self.x + self.width, self.y)])

    def move_down(self) -> None:
        self.y += BIRD_V_SPEED

    def move_up(self) -> None:
        self.y -= BIRD_V_SPEED

    def draw(self, surface: pygame.Surface) -> None:
        """draw bird onto pygame surface"""
        surface.blit(self.img, self.get_location())

class Blocks:
    """blocks!"""

    def __init__(self, bird_height: float) -> None:
        """
        instantiate a blocks object

        Parameters
        ----------
        bird_height : float
            the height of the bird in the game, determines gap size
        """

        self._starting_speed = BLOCK_STARTING_SPEED
        self._bird_height = bird_height
        self.colour = BLOCKS_COLOUR

        self.width = BLOCK_WIDTH
        self.x = GAME_WIDTH
        # y0 is the bottom of the bottom block so always zero
        # y1 is the top of the bottom block, start so gap is at center
        # y2 is the top of the top block (i.e. the top of the screen)
        self.y0 = 0
        self.y1 = int((GAME_HEIGHT/2) - (self._bird_height/2))
        self.y2 = GAME_HEIGHT

        self._speed = 0
        self._gap_size = GAME_HEIGHT/2

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def gap_size(self) -> float:
        return self._gap_size

    def set_speed_and_size(self, score: int) -> None:
        """
        set the speed block speed and gap_size based on score

        Parameters
        ----------
        score : int
            score, higher values result in smaller gap_size and higher speed
        """
        if self._speed <= BLOCK_MAX_SPEED:
            self._speed = self._starting_speed +\
                          (score // BLOCK_SPEED_INCREMENT)

        if self._gap_size >= self._bird_height * GAP_MIN_MULTIPLIER:
            self._gap_size =  int(self._bird_height *
                                  (GAP_START_MULTIPLIER -
                                   score/GAP_DECREASE_DENOMINATOR))

    def get_location(self) -> tuple[list, list]:
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

    def get_polygon(self) -> tuple[Polygon, Polygon]:
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
            self.x = GAME_WIDTH
            self.y1 = random.randint(self.gap_size,
                                     self.y2 - self.gap_size)

    def draw(self, surface: pygame.Surface) -> None:
        """draw blocks on pygame surface"""
        bottom_block, top_block = self.get_location()
        pygame.draw.rect(surface, self.colour, bottom_block)
        pygame.draw.rect(surface, self.colour, top_block)


class Game:
    """the game"""

    def __init__(self) -> None:
        """instantiate game"""
        pygame.init()
        self.surface = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption('Flappy Bird')

        self.bird= Bird()
        self.blocks = Blocks(self.bird.height)

        self.game_over: bool = False

        self.score= 0
        self.high_score = 0
        self.clock = pygame.time.Clock()

        self.draw()

    @staticmethod
    def get_center() -> tuple[float, float]:
        return GAME_WIDTH/2, GAME_HEIGHT/2

    def get_polygon(self) -> Polygon:
        """return game surface as a Polygon object"""
        return Polygon([(0, 0),
                        (0, GAME_HEIGHT),
                        (GAME_WIDTH, GAME_HEIGHT),
                        (GAME_WIDTH, 0)])


    def restart(self) -> None:
        """reset game to starting parameters"""
        self.bird = Bird()
        self.blocks = Blocks(bird_height=self.bird.height)
        self.score = 0
        self.game_over = False


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

    def draw(self) -> None:
        self.surface.fill(BACKGROUND_COLOUR)
        self.blocks.draw(self.surface)
        self.bird.draw(self.surface)
        self.display_score()
        if self.game_over:
            self.display_game_over()
            pygame.display.update()
            time.sleep(1)
            self.replay()
            self.restart()
            self.draw()

        pygame.display.update()
        self.clock.tick(80)

    @staticmethod
    def quit() -> None:
        pygame.quit()

    def detect_collision(self) -> None:
        """check if bird intersects with blocks or outside game surface"""
        bird_poly = self.bird.get_polygon()
        b_block_poly, t_block_poly = self.blocks.get_polygon()
        game_poly = self.get_polygon()

        if ((not bird_poly.intersects(game_poly)) or
            (bird_poly.intersects(b_block_poly)) or
            (bird_poly.intersects(t_block_poly))):
            self.game_over = True

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
        displat text on the pygame surface

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
        self._display_text( f'Score: {self.score}', SMALL_FONT, (45, 15))


    def display_game_over(self) -> None:
        x, y = self.get_center()
        self._display_text('Game Over!', LARGE_FONT, (x, y-50))
        self._display_text(f'Score: {self.score} Highscore: {self.high_score}',
                           SMALL_FONT, (x, y+35))
        self._display_text('Press any key to continue.', SMALL_FONT, (x, y+75))

    def play(self) -> None:
        """play the game"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                # keydown - when button is pressed keyup - when it's released
                move_up = (event.type == pygame.KEYDOWN and
                           event.key == pygame.K_UP)

            self.update(move_up)
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.play()
