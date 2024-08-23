from __future__ import annotations
from action import PaintAction
from grid import Grid
from data_structures.stack_adt import ArrayStack

class UndoTracker:

    def __init__(self) -> None:
        """
        Initialise the instance variable actions which is an ArrayStack object to store PaintAction objects.
        Initialise the instance variable undone which is an ArrayStack object to store undone PaintAction objects.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(max_capacity), where max_capacity is the argumnet we place in the creation of ArrayStack object.
        - Best case: O(max_capacity), since the ArrayStack object will be created regardless.    
        """ 
        self.actions = ArrayStack(10000)
        self.undone = ArrayStack(10000)

    def add_action(self, action: PaintAction) -> None:
        """
        Adds an action to the undo tracker(self.actions).
        If self.actions is already full, we don't add the action.

        Args: 
        - action = A PainAction object to be added to 'actions' instance variable(ArrayStack).

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method, is_full, push and clear are O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        if not self.actions.is_full(): #O(1)
            self.actions.push(action) #O(1)
            self.undone.clear() #O(1)

    def undo(self, grid: Grid) -> PaintAction|None:
        """
        Undo an operation, and apply the relevant action to the grid.
        If there are no actions to undo, do nothing.

        Args: 
        - grid = The Grid object where the undo is gonna be applied to.

        Raises: None

        Returns: 
        - action = A PaintAction that has been undone.
        - None = returned when there is nothing to undo.

        Complexity:
        - Worst case: O(undo_apply), where undo_apply is the complexity of undo_apply function.
        - Best case: O(undo_apply), where undo_apply is the complexity of undo_apply function.
        """
        if not self.actions.is_empty(): #O(1)
            action = self.actions.pop() #O(1)
            action.undo_apply(grid) #O(undo_apply)
            self.undone.push(action) #O(1)
            return action
        return None

    def redo(self, grid: Grid) -> PaintAction|None:
        """
        Redo an operation that was previously undone.
        If there are no actions to redo, do nothing.

        Args: 
        - grid = The Grid object where the redo is gonna be applied to.

        Raises: None

        Returns: 
        - to_redo = A PaintAction that has been redo.
        - None = resturned when there is nothing to redo.

        Complexity:
        - Worst case: O(redo_apply), where redo_apply is the complexity of redo_apply function.
        - Best case: O(redo_apply), where redo_apply is the complexity of redo_apply function.
        """
        if not self.undone.is_empty(): #O(1)
            to_redo = self.undone.pop() #O(1)
            to_redo.redo_apply(grid) #O(redo_apply)
            self.actions.push(to_redo) #O(1)
            return to_redo
        return None
