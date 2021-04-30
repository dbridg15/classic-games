import numpy as np


class Grid:
    """a grid object which maps grid coordinates to pixel coordinates"""

    def __init__(self,
                 width: int,
                 height: int,
                 block_size: int) -> None:
        """
        initialise Grid object


        Parameters
        ----------
        game_size : int, optional
            the size of the game square, by default GAME_SIZE
        grid_size : int, optional
            the number of blocks to split the game into, by default GRID_SIZE
        """


        if (width % block_size) + (height % block_size) != 0:
            raise ValueError('width and height must be divisible by '
                             'block_size')

        self._block_size = block_size
        self._game_width = width
        self._game_height = height
        self._grid_width = int(width/block_size)
        self._grid_height = int(height/block_size)

        self._set_grid()

    def _set_grid(self) -> None:
        """
        set grid as 2D np array of coordinates of bottom left corners

        Parameters
        ----------
        width : int
            width of the game in pixels
        height : int
            height of the game in pixels
        block_size : int
            size of blocks in the grid
        """

        width_vector = np.array(
            [self.block_size * i for i in range(self.width)])
        height_vector = np.array(
            [self.block_size * i for i in range(self.height)])

        self._grid = np.array(np.meshgrid(width_vector, height_vector)).T

    def __getitem__(self, item: tuple) -> tuple:
        """return the pixel-coordinates for the given game coordinates"""
        return self._grid[item]

    @property
    def game_width(self) -> int:
        """the width of the game in pixels"""
        return self._game_width

    @property
    def game_height(self) -> int:
        """the height of the game in pixels"""
        return self._game_height

    @property
    def width(self) -> int:
        """the width of the grid (no. blocks)"""
        return self._grid_width

    @property
    def height(self) -> int:
        """the height of the grid (no. blocks)"""
        return self._grid_height

    @property
    def block_size(self) -> int:
        """the size of each block"""
        return self._block_size
