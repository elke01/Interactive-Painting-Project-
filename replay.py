from __future__ import annotations
from action import PaintAction
from grid import Grid
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack

class ReplayTracker:

    def __init__(self) -> None:
        """
        Initialise the instance variable actions which is a CircularQueue object to store PaintAction objects.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(max_capacity), where max_capacity is the argumnet we place in the creation of CircularQueue object.
        - Best case: O(max_capacity), since the CircularQueue object will be created regardless.    
        """ 
        self.actions = CircularQueue(10000)

    def start_replay(self) -> None:
        """
        Called whenever we should stop taking actions, and start playing them back.

        Useful if you have any setup to do before `play_next_action` should be called.

        Args: None

        Raises: None

        Returns: None

        Complexity: None
        """
        pass

    def add_action(self, action: PaintAction, is_undo: bool=False) -> None:
        """
        Adds an action to the replay(self.actions). If the action is and undo action, then is_undo = True, otherwise False.
        `is_undo` specifies whether the action was an undo action or not.
        Special, Redo, and Draw all have this is False.

        Args:
        - action = A PainAction object to be added to 'actions' instance variable(CircularQueue).
        - is_undo = A boolean indicating is the PaintAction to be added is an undo action or not, initialise as False.

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(1), the complexity of append is O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        self.actions.append((action, is_undo)) #O(1)


    def play_next_action(self, grid: Grid) -> bool:
        """
        Plays the next replay action that is in the self.actions to the grid.
        Returns a boolean :
            - If there were no more actions to play, and so nothing happened, return True.
            - Otherwise, return False.

        Args:
        - grid = The Grid object where the next action is gonna be applied to.

        Raises: None

        Returns: 
        - True/False = If there is more action to play then return True, otherwise False.

        Complexity:
        - Worst case: O(undo_apply|redo_apply), where undo_apply|redo_apply is the complexity of undo_apply|redo_apply function.
        - Best case: O(undo_apply|redo_apply), where undo_apply|redo_apply is the complexity of undo_apply|redo_apply function.
        """
        if not self.actions.is_empty():
            attached = self.actions.serve() #O(1)
            is_undo = attached[1] #O(1)
            action = attached[0] #O(1)
            if is_undo:
                action.undo_apply(grid) #O(undo_apply)
            else:
                action.redo_apply(grid) #O(redo_apply)
            if len(self.actions) >= 0: #O(1)
                return False
        return True

if __name__ == "__main__":
    action1 = PaintAction([], is_special=True)
    action2 = PaintAction([])

    g = Grid(Grid.DRAW_STYLE_SET, 5, 5)

    r = ReplayTracker()
    # add all actions
    r.add_action(action1)
    r.add_action(action2)
    r.add_action(action2, is_undo=True)
    # Start the replay.
    r.start_replay()
    f1 = r.play_next_action(g) # action 1, special
    f2 = r.play_next_action(g) # action 2, draw
    f3 = r.play_next_action(g) # action 2, undo
    t = r.play_next_action(g)  # True, nothing to do.
    assert (f1, f2, f3, t) == (False, False, False, True)

