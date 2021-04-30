from abc import ABC, abstractmethod
import time
import pygame


class GameOver(Exception):
    """exception to raise if game is over!"""

class BaseConfig(ABC):
    """universal configurations"""
    # pylint: disable=invalid-name

    NAME: str
    SPEED: int
    BACKGROUND_COLOUR:  tuple[int, int, int]
    FONT_COLOUR: tuple[int, int, int]

    GAME_WIDTH: int
    GAME_HEIGHT: int

    FONT: str = 'freesansbold.ttf'

    @property
    def SMALL_FONT(self) -> tuple:
        """small font"""
        return self.FONT, int(self.GAME_WIDTH/40)

    @property
    def LARGE_FONT(self) -> tuple:
        """large font"""
        return self.FONT, int(self.GAME_WIDTH/6)


class BaseGame(ABC):
    """Base class for simple pygame-games"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 config: BaseConfig) -> None:
        """
        instantiate the game

        Parameters
        ----------
        name : str
            name of the game, displayed in caption
        width : int
            width of the game in pixels
        height : int
            height of the game in pixels
        """
        self.config = config

        self.score = 0
        self.high_score = 0
        self.game_over = False

        pygame.init()
        self.surface = pygame.display.set_mode((self.width,
                                                self.height))
        pygame.display.set_caption(self.config.NAME)

        self.clock = pygame.time.Clock()
        self.draw()

    @property
    def width(self) -> int:
        """return the game width"""
        return self.config.GAME_WIDTH

    @property
    def height(self) -> int:
        """return the game width"""
        return self.config.GAME_HEIGHT

    @property
    def center(self) -> tuple[float, float]:
        """return the centre of the game"""
        return self.width/2, self.height/2

    def restart(self) -> None:
        """reset game to starting parameters"""
        self.score = 0
        self.game_over = False

    @abstractmethod
    def update(self) -> None:
        """update the state of the game"""
        raise NotImplementedError

    @abstractmethod
    def _draw(self) -> None:
        """draw state of game within child"""
        raise NotImplementedError

    def draw(self) -> None:
        """draw state of game"""
        self.surface.fill(self.config.BACKGROUND_COLOUR)
        self.display_score()

        self._draw()

        if self.game_over:
            self.display_game_over()
            pygame.display.update()
            time.sleep(1)
            self.replay()
            self.restart()
            self.draw()

        pygame.display.update()
        self.clock.tick(self.config.SPEED)

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

    def display_text(self,
                     text: str,
                     font: tuple[str, int],
                     center: tuple[int, int] = None,
                     colour: tuple[int, int, int] = None) -> None:
        """
        display text on the pygame surface

        Parameters
        ----------
        text : str
            the text to display
        font : tuple[str, int]
            the font to use (font-name, size)
        center : tuple[int, int], optional
            where to centre the text, by default None
        colour : tuple[int, int, int], optional
            text colour, by default (0, 0, 255) which is blue
        """

        if colour is None:
            colour = self.config.FONT_COLOUR
        font = pygame.font.Font(*font)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = center
        self.surface.blit(text_surface, text_rect)

    def display_score(self) -> None:
        """display the game score"""
        self.display_text(f'Score: {self.score}',
                          self.config.SMALL_FONT,
                          (45, 15))

    def display_game_over(self) -> None:
        """display the game over message"""
        x, y = self.center
        self.display_text('Game Over!', self.config.LARGE_FONT, (x, y-50))
        self.display_text(f'Score: {self.score} Highscore: {self.high_score}',
                          self.config.SMALL_FONT, (x, y+35))
        self.display_text('Press any key to continue.',
                          self.config.SMALL_FONT,
                          (x, y+75))

    def play(self):
        """the game loop"""
        raise NotImplementedError
