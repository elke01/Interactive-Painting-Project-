from __future__ import annotations
from abc import ABC, abstractmethod
from layer_util import Layer
from layers import *
from layer_util import *
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack
from data_structures.array_sorted_list import ArraySortedList
from data_structures.sorted_list_adt import ListItem
from data_structures.bset import BSet

class LayerStore(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass

class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - special: Invert the colour output.
    """

    def __init__(self) -> None:
        """
        Initialise the instance variable layer which holds a single layer Object.
        Initialise inverted which holds a boolean that indicates whether the layers are being inverted of not.

        Args: None

        Raises: None

        Returns:  None

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method.
        - Best case: O(1), since the worst case id O(1), the best case will also be O(1).     
        """        
        self.layer = None
        self.inverted = False

    def add(self, layer: Layer) -> bool:
        """
        Add/assign a layer to the store(self.layer).
        Returns true if the LayerStore was actually changed, otherwise return False.

        Args:
        - layer = Layer object to be added/applied to the square grid.

        Raises: None

        Returns:
        - True/False = indicate whether the layer is being changed or not.

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method.
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1).
        """
        if self.layer == layer:
            return False
        self.layer = layer
        return True


    def get_color(self, start: tuple[int, int, int], timestamp: int, x: int, y: int) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.

        Args:
        - start = a tuple of integers, represent the starting colour of the square grid (RGB).
        - timestamp = an integer, the time needed to decide the color .
        - x = an integer, representing the x coordinate of the square grid.
        - y = an integer, representing the y coordinate of the square grid.

        Raises: None

        Returns:
        - start/colour of the square grid = a tuple of integers, represent the colour of the square grid after a layer is applied to it.

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method.
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1).
        """
        if self.inverted:
            if self.layer != None:
                return invert.apply(self.layer.apply(start, timestamp, x, y), timestamp, x, y)
            else:
                return invert.apply(start, timestamp, x, y)
        else:
            if self.layer != None:
                return self.layer.apply(start, timestamp, x, y)
        return start


    def erase(self, layer: Layer) -> bool:
        """
        Remove/erase the layer that is currently in self.layer, making it None.
        Returns true if the LayerStore was actually changed.

        Args:
        - layer = a layer object to be removed from the square grid.

        Raises: None

        Returns:
        - True/False = indicate whether the layer is being removed or not.

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method.
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1).
        """
        if self.layer == None:
            return False
        self.layer = None
        return True


    def special(self):
        """
        Invert the whole square on the grid.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method.
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1).
        """
        self.inverted = not self.inverted
       

class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """

    def __init__(self) -> None:
        """
        Initialise the instance variable layer which is a CircularQueue object to store layer objects.
        Initialise color which is a tuple of integers that represent the current colour of the square grid.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(n), where n is the length of array returned by the get_layers() function.
        - Best case: O(n), because we have to create the CircularQueue object regardless.     
        """   
        self.layers = CircularQueue(len(get_layers()) * 100)
        self.color = None

    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store(self.layers).
        Returns true if the LayerStore was actually changed.

        Args:
        - layer = layer object to be added to the 'layer' instance variable(CircuclarQueue).

        Raises: None

        Returns: 
        - True/False: indicate whether the layer object is successfully added or not.

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method, and append is O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        initial_length = len(self.layers)
        self.layers.append(layer) #O(1)
        if len(self.layers) > initial_length:
            return True
        return False

    def get_color(self, start: tuple[int, int, int], timestamp: int, x: int, y: int) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.

        Args:
        - start = a tuple of integers, represent the starting colour of the square grid (RGB).
        - timestamp = an integer, the time needed to decide the color .
        - x = an integer, representing the x coordinate of the square grid.
        - y = an integer, representing the y coordinate of the square grid.

        Raises: None

        Returns:
        - self.color = a tuple of integers, represent the colour of the square grid.

        Complexity:
        - Worst case: O(n*apply), where n is the length of self.layers and apply is the complexity of apply function.
        - Best case: O(n*apply), same as worst case, because no other property in the algorithm will affect the loops.
        """
        self.color = start
        if len(self.layers) != 0:
            for _ in range(len(self.layers)): #O(n), n is the length of self.layers
                layer = self.layers.serve() #O(1)
                self.layers.append(layer) #O(1)
                self.color = layer.apply(self.color, timestamp, x, y) #O(apply)
            return self.color
        self.color = start
        return self.color

    def erase(self, layer: Layer) -> bool:
        """
        Erase the first/oldest layer added to the layerstore(self.layers).
        Returns true if the LayerStore was actually changed.

        Args:
        - layer: layer object to be removed from the 'layer' instance variable(CircuclarQueue).

        Raises: None

        Returns: 
        - True/False: indicate whether the layer object is successfully removed or not.

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method, and serve is O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        initial_length = len(self.layers) #O(1)
        layer_erased = self.layers.serve() #O(1)
        if len(self.layers) < initial_length:
            return True
        return False

    def special(self):
        """
        Reverse the order of the the elements in the store(self.layers).
        The oldest become the newest and vice versa.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(n), where n is the length of self.layers.
        - Best case: O(n), same as worst case, because no other property in the algorithm will affect the loops.
        """
        temp = ArrayStack(len(self.layers)) #O(n)
        
        for _ in range(len(self.layers)): #O(n)
            item: Layer = self.layers.serve() #O(1)
            temp.push(item) #O(1)

        for _ in range(len(temp)): #O(n) since len(temp) == len(self.layers)
            item: Layer = temp.pop() #O(1)
            self.layers.append(item) #O(1)
        

class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """

    def __init__(self) -> None:
        """
        Initialise the instance variable layer which is a BSet object to indicate whether certain layers are applied or not.
        Initialise color which is a tuple of integers that represent the current colour of the square grid.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(1), there are only basic operations and creation of BSet is O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1).    
        """   
        self.layers = BSet() #O(1)
        self.color = None

    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store(self.layers).
        Returns true if the LayerStore was actually changed.

        Args:
        - layer: layer object to be added/applied to the 'layer' instance variable(BSet).

        Raises: None

        Returns: 
        - True/False: indicate whether the layer object is successfully applied or not.

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method, contains and add are O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        index = layer.index
        if (index+1) not in self.layers: #contains --> O(1)
            self.layers.add(index + 1) # O(1)
            return True
        return False

    def get_color(self, start: tuple[int, int, int], timestamp: int, x: int, y: int) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        
        Args:
        - start = a tuple of integers, represent the starting colour of the square grid (RGB).
        - timestamp = an integer, the time needed to decide the color .
        - x = an integer, representing the x coordinate of the square grid.
        - y = an integer, representing the y coordinate of the square grid.

        Raises: None

        Returns:
        - self.color = a tuple of integers, represent the colour of the square grid.

        Complexity:
        - Worst case: O(n*apply), where n is the length of get_layers() and apply is the complexity of apply function.
        - Best case: O(n*apply), same as worst case, because no other property in the algorithm will affect the loops.
            still same as worst case, because if the BSet is not empty, then there must be at least 1 item 'i' that is in the BSet.
        """
        self.color = start
        if not self.layers.is_empty(): #O(1)
            for i in range(1, len(get_layers())): #O( len(get_layers()) )
                if i in self.layers: #O(1)
                    self.color = get_layers()[i-1].apply(self.color, timestamp, x, y) #O(apply)
            return self.color
        self.color = start
        return self.color


    def erase(self, layer: Layer) -> bool:
        """
        Erase/remove/unapply the layer that is the store(self.layers).
        Returns true if the LayerStore was actually changed.

        Args:
        - layer: layer object to be removed/unapplied from the 'layer' instance variable(BSet).

        Raises: None

        Returns: 
        - True/False: indicate whether the layer object is successfully removed/unapplied or not.

        Complexity:
        - Worst case: O(1), since there are only basic operations in this method, contains and remove are O(1).
        - Best case: O(1), since the worst case is O(1), the best case will also be O(1). 
        """
        index = layer.index
        if (index+1) not in self.layers: #O(1)
            return False
        self.layers.remove(index + 1) #O(1)
        return True


    def special(self):
        """
        Remove the median "applying" layer based on its name that has been lexicographically ordered.

        Args: None

        Raises: None

        Returns: None

        Complexity:
        - Worst case: O(|elems| + (mlogn)), where elems is the number of bits in the binary represenation of self.layers, 
                            m is the length of get_layers(), and n is length of applied (ArraySortedList).
        - Best case: O(|elems| + m), where m is the length of get_layers()
        """
        if not self.layers.is_empty(): #O(1)
            applied = ArraySortedList(len(self.layers)) #O(|elems|) elems is the number of bits in the binary represenation of self.layers
            for i in range(1, len(get_layers())): #O(len(get_layers()))
                if i in self.layers: #O(1)
                    applied.add(ListItem(i, get_layers()[i - 1].name)) #O(log(len(applied))) or O(1).

            length = len(applied) #O(1)
            mid = length // 2
            if length % 2 == 0:
                mid -= 1
            self.layers.remove(applied[mid].value) #O(1)




