from __future__ import annotations
from data_structures.referential_array  import ArrayR
from layer_store import *

class Grid:
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 2
    MAX_BRUSH = 5
    MIN_BRUSH = 0

    def __init__(self, draw_style, x: int, y: int) -> None:
        """
        Initialise the grid object by the dimension givenin the argument.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Intialise the brush size to the DEFAULT provided as a class variable.
        
        Args:
        - draw_style: one option from the DRAW_STYLE_OPTIONS.
        - x: the dimension of the grid in the x-coordinate.
        - y: the dimension of the grid in the y-coordinate.

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(n**2), where n is dimension of the grid.
        - Best case: O(n**2), same as worst case since we need to iterate over the dimension of the grid to create the grid regardless.
        """
        if draw_style in self.DRAW_STYLE_OPTIONS :
            self.draw_style = draw_style
        self.brush_size = self.DEFAULT_BRUSH_SIZE


        self.grid = ArrayR(y)

        for i in range(y):
            inner = ArrayR(x)

            for j in range(x):
                if self.draw_style == self.DRAW_STYLE_SET:
                    inner[j] = SetLayerStore()
                elif self.draw_style == self.DRAW_STYLE_ADD:
                    inner[j] = AdditiveLayerStore()
                else:
                    inner[j] = SequenceLayerStore()

            self.grid[i] = inner


    def increase_brush_size(self):
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method.
        - Best case: O(1), since the worst case id O(1), the best case will also be O(1).     
        """
        if self.brush_size < self.MAX_BRUSH:
            self.brush_size += 1

    def decrease_brush_size(self):
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method.
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1).
        """
        if self.brush_size > self.MIN_BRUSH:
            self.brush_size -= 1

    def special(self):
        """
        Activate the special affect depends on the type of LayerStore on all grid squares.

        Args: None

        Raises: None

        Returns: None

        Complexity:        
        - Worst case: O((n**2) * special), where n is the dimension fo the grid, and special is the complexity of special function, it depends on what layerstore is used.
        - Best case: O((n**2) * special), same as worst case, because no other property in the algorithm will affect the nested loop.
        """
        for i in range(len(self.grid)): #O(n), where n is the dimension fo the grid.
            for j in range(len(self.grid[i])): #O(n), where n is the dimension fo the grid.
                self.grid[i][j].special() #O(special), different depends on what layerstore is used.


    def __getitem__(self, key: int):
        return self.grid[key]
