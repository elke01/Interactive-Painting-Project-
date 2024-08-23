import arcade
import arcade.key as keys
import math
from grid import Grid
from layer_util import get_layers, Layer
from layers import lighten
from layer_store import *
from undo import *
from action import *
from replay import *

class MyWindow(arcade.Window):
    """ Painter Window """

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 700
    SIDEBAR_WIDTH = 100
    BUTTONS_HEIGHT = 100
    SCREEN_TITLE = "Paint"

    REPLAY_TIMER_DELTA = 0.05

    GRID_SIZE_X = 32
    GRID_SIZE_Y = 32

    BG = [255, 255, 255]

    # SCAFFOLD PART
    # Unless you're adding new features, you shouldn't need to touch this.

    def __init__(self) -> None:
        """Initialise visual and logic variables."""
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.SCREEN_TITLE)
        arcade.set_background_color(self.BG)
        self.grid: Grid = None
        self.draw_style = Grid.DRAW_STYLE_SET
        self.z_pressed = False
        self.y_pressed = False
        self.z_timer = 0
        self.y_timer = 0
        self.enable_ui = True
        self.replay_timer = 0
        self.on_init()

    def reset(self) -> None:
        """Reset the screen."""
        self.grid = Grid(self.draw_style, self.GRID_SIZE_X, self.GRID_SIZE_Y)
        self.timestamp = 0

        self.selected_layer_index = -1
        self.dragging = None
        self.prev_drawn = None
        self.prev_pos = None
        self.draw_size = 2

        # Visual calculations
        self.DRAW_PANEL = self.SCREEN_WIDTH - self.SIDEBAR_WIDTH
        self.GRID_SQ_WIDTH = self.DRAW_PANEL / self.GRID_SIZE_X
        self.GRID_SQ_HEIGHT = self.SCREEN_HEIGHT / self.GRID_SIZE_Y
        self.LAYER_BUTTON_SIZE = self.SIDEBAR_WIDTH / 2
        # Action button sprites
        self.action_buttons = arcade.SpriteList()
        self.draw_mode_button = arcade.Sprite(
            "img/on_off.png" if self.draw_style == Grid.DRAW_STYLE_SET else (
                "img/additive.png" if self.draw_style == Grid.DRAW_STYLE_ADD else "img/sequence.png"
            ),
            scale=50/48,
        )
        self.draw_mode_button.center_x = self.DRAW_PANEL + self.LAYER_BUTTON_SIZE / 2
        self.draw_mode_button.center_y = self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.draw_mode_button)
        self.replay_button = arcade.Sprite(
            "img/replay.png",
            scale=50/48,
        )
        self.replay_button.center_x = self.DRAW_PANEL + 3 * self.LAYER_BUTTON_SIZE / 2
        self.replay_button.center_y = self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.replay_button)
        self.brush_big_button = arcade.Sprite(
            "img/brush_up.png",
            scale=50/48,
        )
        self.brush_big_button.center_x = self.DRAW_PANEL + self.LAYER_BUTTON_SIZE / 2
        self.brush_big_button.center_y = 3 * self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.brush_big_button)
        self.brush_small_button = arcade.Sprite(
            "img/brush_down.png",
            scale=50/48,
        )
        self.brush_small_button.center_x = self.DRAW_PANEL + 3 * self.LAYER_BUTTON_SIZE / 2
        self.brush_small_button.center_y = 3 * self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.brush_small_button)
        self.special_button = arcade.Sprite(
            "img/special.png",
            scale=50/48,
        )
        self.special_button.center_x = self.DRAW_PANEL + self.LAYER_BUTTON_SIZE / 2
        self.special_button.center_y = 5 * self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.special_button)

        self.on_reset()

    def setup(self) -> None:
        """Set up the game and initialize the variables."""
        self.reset()

    def on_draw(self) -> None:
        """Draw everything"""
        self.clear()
        # UI - Layers
        for i, layer in enumerate(get_layers()):
            if layer is None: break
            xstart = (i % 2) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            xend = ((i % 2)+1) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = self.SCREEN_HEIGHT - (i//2) * self.LAYER_BUTTON_SIZE
            yend = self.SCREEN_HEIGHT - (i//2+1) * self.LAYER_BUTTON_SIZE
            bg = lighten.apply(layer.bg or self.BG[:], 0, 0, 0) if self.selected_layer_index == i else (layer.bg or self.BG[:])
            if not self.enable_ui:
                bg = lighten.apply(bg, 0, 0, 0)
            arcade.draw_lrtb_rectangle_filled(xstart, xend, ystart, yend, bg)
            arcade.draw_lrtb_rectangle_outline(
                xstart, xend, ystart, yend, (0, 0, 0), border_width=1,
            )
            arcade.draw_text(str(i), xstart, (ystart+yend)/2, (0, 0, 0), 18, width=xend-xstart, align="center", bold=True, anchor_y="center")
        # UI - Draw Modes / Action buttons
        self.action_buttons.draw()
        # Grid
        for x in range(self.GRID_SIZE_X):
            for y in range(self.GRID_SIZE_Y):
                arcade.draw_lrtb_rectangle_filled(
                    self.GRID_SQ_WIDTH * x,
                    self.GRID_SQ_WIDTH * (x+1),
                    self.GRID_SQ_HEIGHT * (y+1),
                    self.GRID_SQ_HEIGHT * y,
                    self.grid[x][y].get_color(self.BG[:], self.timestamp, x, y),
                )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Called when the mouse buttons are pressed."""
        if x > self.DRAW_PANEL:
            if not self.enable_ui:
                return
            # Buttons
            for i, layer in enumerate(get_layers()):
                if layer is None: break
                xstart = (i % 2) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
                xend = ((i % 2)+1) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
                ystart = self.SCREEN_HEIGHT - (i//2) * self.LAYER_BUTTON_SIZE
                yend = self.SCREEN_HEIGHT - (i//2+1) * self.LAYER_BUTTON_SIZE
                if xstart <= x < xend and yend <= y < ystart:
                    self.selected_layer_index = i
                    break
            # Actions
            xstart = self.DRAW_PANEL
            xend = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = self.LAYER_BUTTON_SIZE
            yend = 0
            if xstart <= x < xend and yend <= y < ystart:
                self.change_draw_mode()
            xstart = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            xend = 2 * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = self.LAYER_BUTTON_SIZE
            yend = 0
            if xstart <= x < xend and yend <= y < ystart:
                self.start_replay()
            xstart = self.DRAW_PANEL
            xend = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = 2 * self.LAYER_BUTTON_SIZE
            yend = self.LAYER_BUTTON_SIZE
            if xstart <= x < xend and yend <= y < ystart:
                self.on_increase_brush_size()
            xstart = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            xend = 2 * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = 2 * self.LAYER_BUTTON_SIZE
            yend = self.LAYER_BUTTON_SIZE
            if xstart <= x < xend and yend <= y < ystart:
                self.on_decrease_brush_size()
            xstart = self.DRAW_PANEL
            xend = 1 * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = 3 * self.LAYER_BUTTON_SIZE
            yend = 2 * self.LAYER_BUTTON_SIZE
            if xstart <= x < xend and yend <= y < ystart:
                self.on_special()
        else:
            self.dragging = True
            self.try_draw(x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """Called when the mouse buttons are released."""
        self.dragging = False
        self.prev_drawn = None
        self.prev_pos = None

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        """Called when the mouse moves."""
        if not self.dragging:
            return
        if not(0 <= self.selected_layer_index < len(get_layers())):
            return
        if x > self.DRAW_PANEL:
            return
        self.try_draw(x, y)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when a keyboard key is pressed."""
        if not self.enable_ui:
            return
        self.z_pressed = keys.Z == symbol and (modifiers & keys.MOD_CTRL)
        self.y_pressed = keys.Y == symbol and (modifiers & keys.MOD_CTRL)
        if self.z_pressed:
            self.on_undo()
            self.z_timer = 0.5
        if self.y_pressed:
            self.on_redo()
            self.y_timer = 0.5

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when a keyboard key is released."""
        self.z_pressed = False
        self.y_pressed = False

    def try_draw(self, x, y) -> None:
        """Attempt to draw at a position, but safely fail if an invalid square."""
        if self.selected_layer_index == -1:
            return
        layer = get_layers()[self.selected_layer_index]
        if self.prev_pos is not None:
            # Try draw in increments of 0.5 to avoid skipping squares.
            mhat_dist = abs(x - self.prev_pos[0]) + abs(y - self.prev_pos[1])
            increment = 0.5
            points_to_draw = []
            for d in range(1, math.ceil(mhat_dist/increment)+1):
                distance = min(d * increment / mhat_dist, 1)
                nx = distance * (x - self.prev_pos[0]) + self.prev_pos[0]
                ny = distance * (y - self.prev_pos[1]) + self.prev_pos[1]
                nx_pos = int(nx // self.GRID_SQ_WIDTH)
                ny_pos = int(ny // self.GRID_SQ_HEIGHT)
                points_to_draw.append((nx_pos, ny_pos))
        else:
            x_pos = int(x // self.GRID_SQ_WIDTH)
            y_pos = int(y // self.GRID_SQ_HEIGHT)
            points_to_draw = [
                (x_pos, y_pos)
            ]
        for px, py in points_to_draw:
            if self.prev_drawn is None or (px, py) != self.prev_drawn:
                if 0 <= px < self.GRID_SIZE_X and 0 <= py < self.GRID_SIZE_Y:
                    self.on_paint(layer, px, py)
                    self.prev_drawn = (px, py)
        self.prev_pos = (x, y)

    def start_replay(self) -> None:
        """Begin the replay mode."""
        self.enable_ui = False
        self.grid = Grid(self.draw_style, self.GRID_SIZE_X, self.GRID_SIZE_Y)
        self.replay_timer = self.REPLAY_TIMER_DELTA
        self.on_replay_start()

    def on_update(self, delta_time) -> None:
        """Movement and game logic."""
        self.timestamp += delta_time
        if self.z_pressed:
            self.z_timer -= delta_time
            if self.z_timer <= 0:
                self.on_undo()
                self.z_timer += 0.05
        if self.y_pressed:
            self.y_timer -= delta_time
            if self.y_timer <= 0:
                self.on_redo()
                self.y_timer += 0.05
        if not self.enable_ui:
            self.replay_timer -= delta_time
            if self.replay_timer <= 0:
                self.replay_timer += self.REPLAY_TIMER_DELTA
                finished = self.on_replay_next_step()
                if finished:
                    self.enable_ui = True

    def change_draw_mode(self) -> None:
        """Changes the draw mode of the application, and resets the window."""
        if self.draw_style == Grid.DRAW_STYLE_SET:
            self.draw_style = Grid.DRAW_STYLE_ADD
        elif self.draw_style == Grid.DRAW_STYLE_ADD:
            self.draw_style = Grid.DRAW_STYLE_SEQUENCE
        elif self.draw_style == Grid.DRAW_STYLE_SEQUENCE:
            self.draw_style = Grid.DRAW_STYLE_SET
        self.reset()

    # STUDENT PART

    def on_init(self):
        """
        Called when MyWindow object is created.
        Initialise the instance variable undo_tracker which is an UndoTracker object to store PaintAction objects.
        Initialise the instance variable ReplayTracker which is an ReplayTracker object to store PaintAction objects.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(max_capacity), where max_capacity is the maximum capacity of the CircularQueue & ArrayStack in the UndoTracker and ReplayTracker.
        - Best case: O(max_capacity), because we have to create both UndoTracker and ReplayTracker objects regardless.  
        """
        self.undo_tracker = UndoTracker()
        self.replay_tracker = ReplayTracker()

    def on_reset(self):
        """Called when a window reset is requested.
        This method will be called when reset is being done, it will reset the UndoTracker and ReplayTracker object everytime the user change 
        layerstore.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(max_capacity), where max_capacity is the maximum capacity of the CircularQueue & ArrayStack in the UndoTracker and ReplayTracker.
        - Best case: O(max_capacity), because we have to create both UndoTracker and ReplayTracker objects regardless. 
        """
        self.undo_tracker = UndoTracker()
        self.replay_tracker = ReplayTracker()

    def on_paint(self, layer: Layer, px, py):
        """
        Called when a grid square is clicked on, which should trigger painting in the vicinity.
        Vicinity squares outside of the range [0, GRID_SIZE_X) or [0, GRID_SIZE_Y) can be safely ignored.
        This will determine which square grid is going to be painted based on the brush size and manhattan distance.

        layer: The layer being applied.
        px: x position of the brush.
        py: y position of the brush.

        Args: 
        - layer = A layer object to be apply to each grid square based on the brush size.

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(PaintAction + (v**2)), where v is the length from the (px|py-brush size) to (px|py+brush size)
        - Best case: O(PaintAction + (v**2)), because we have to create both PaintAction and no property of the algorithm will stop the for mested loop. 
        """
        action = PaintAction() #O(PaintAction)

        grid = len(self.grid.grid) - 1  #O(1)
        brush = self.grid.brush_size

        for i in range(px-brush, px+brush+1): #O(v) where v is the length from the px-brush size to px+brush size
            if i <=  px:
                sub = abs(px - (i+brush)) #O(1)
            else:
                sub = abs(px - (i-brush)) #O(1)
            max_y = py + sub
            min_y = py - sub
            for j in range(py-brush, py+brush+1): #O(v) where v is the length from the py-brush size to py+brush size (same as px).
                if (j <= max_y and j >= min_y) and (j >= 0 and j <= grid):
                    if (i >= 0 and i <= grid):
                        is_added = self.grid[i][j].add(layer) #O(1)
                        if is_added:
                            action.add_step(PaintStep((i, j), layer)) #O(1)????

        self.undo_tracker.add_action(action) #O(1)
        self.replay_tracker.add_action(action) #O(1)


    def on_undo(self):
        """Called when an undo is requested.
        Call the method undo to undo the action taht has been done on the grid.

        Args: None

        Raises: None

        Returns: None 

        Complexity:
        - Worst case: O(undo_apply), since we are calling undo function, and the undo function have a complexity of O(undo_apply).
        - Best case: O(undo_apply), since we are still calling undo function regardless.  
        """
        action = self.undo_tracker.undo(self.grid) #O(undo_apply)
        if action != None:
            self.replay_tracker.add_action(action, True) #O(1)

    def on_redo(self):
        """Called when a redo is requested.
        Call the method redo to redo the action taht has been done on the grid.

        Args: None

        Raises: None

        Returns: None 

        Complexity:
        - Worst case: O(redo_apply), since we are calling redo function, and the redo function have a complexity of O(redo_apply).
        - Best case: O(redo_apply), since we are still calling redo function regardless. 
        """
        action = self.undo_tracker.redo(self.grid) #O(redo_apply)
        if action != None:
            self.replay_tracker.add_action(action) #O(1)

    def on_special(self):
        """Called when the special action is requested.
        Does the special method to the grid, the special method called depends on what layerstore is being used.
        
        Args: None

        Raises: None

        Returns: None 

        Complexity:
        - Worst case: O(n**2), since we are calling special function, and the special function have a complexity of O(n**2).
        - Best case: O(n**2), since we are still calling special function regardless.  
        """
        self.grid.special() #O(n**2)
        self.undo_tracker.add_action(PaintAction(is_special=True)) #O(1)
        self.replay_tracker.add_action(PaintAction(is_special=True)) #O(1)

    def on_replay_start(self):
        """Called when the replay starting is requested.
        Calls the method on_replay_next_step to start replaying.
        
        Args: None

        Raises: None

        Returns: None 

        Complexity:
        - Worst case: O(undo_apply|redo_apply), since we are calling on_replay_next_step function, and the on_replay_next_step function have a complexity of O(undo_apply|redo_apply).
        - Best case: O(undo_apply|redo_apply), since we are still calling on_replay_next_step function regardless. 
        """
        self.on_replay_next_step() #O(undo_apply|redo_apply)

    def on_replay_next_step(self) -> bool:
        """
        Called when the next step of the replay is requested.
        Returns whether the replay is finished.
        Calls the method play.next.action to continue the replay.
        
        Args: None

        Raises: None

        Returns: None 

        Complexity:
        - Worst case: O(undo_apply|redo_apply), since we are calling play_next_action function, and the play_next_action function have a complexity of O(undo_apply|redo_apply).
        - Best case: O(undo_apply|redo_apply), since we are still calling play_next_action function regardless. 
        """
        return self.replay_tracker.play_next_action(self.grid) #O(undo_apply|redo_apply)

    def on_increase_brush_size(self):
        """Called when an increase to the brush size is requested.
        Calls the method increase_brish_size to increase the brush size.
        
        Args: None

        Raises: None

        Returns: None 

        Complexity:
        - Worst case: O(1), since the function increase_brush_size is O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        self.grid.increase_brush_size() #O(1)

    def on_decrease_brush_size(self):
        """Called when a decrease to the brush size is requested.
        Calls the method decrease_brish_size to decrease the brush size.
        
        Args: None

        Raises: None

        Returns: None 

        Complexity:
        - Worst case: O(1), since the function decrease_brush_size is O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        self.grid.decrease_brush_size() #O(1)

def main():
    """ Main function """
    window = MyWindow()
    window.setup()
    arcade.run()

def run_with_func(func, pause=False):
    from threading import Thread
    window = MyWindow()
    window.setup()
    if pause:
        _ = input("Press enter to begin test.")
    t = Thread(target=func, args=(window,))
    t.start()
    arcade.run()


if __name__ == "__main__":
    # grid1 = Grid("SET", 2,4)
    # print(grid1[[0][0]])
    main()
