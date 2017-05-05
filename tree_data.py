"""Assignment 2: Trees for Treemap

=== CSC148 Fall 2016 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
import os
from random import randint
import math


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you adding and implementing
    new public *methods* for this interface.

    === Public Attributes ===
    @type data_size: int
        The total size of all leaves of this tree.
    @type colour: (int, int, int)
        The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    @type _root: obj | None
        The root value of this tree, or None if this tree is empty.
    @type _subtrees: list[AbstractTree]
        The subtrees of this tree.
    @type _parent_tree: AbstractTree | None
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    def __init__(self, root, subtrees, data_size=0):
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and
        this tree's\
        data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.

        @type self: AbstractTree
        @type root: object
        @type subtrees: list[AbstractTree]
        @type data_size: int
        @rtype: None
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None

        # 1. Initialize self.colour and self.data_size, according to the
        # docstring.
        self.colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        # At this point, if it is a file, data_size will be specified. If it is
        # a folder, the data_size will be zero.
        self.data_size = data_size
        for subtree in self._subtrees:
            # Set the proper data_size for the folder. If it is a leaf, then it
            # will not proceed to this loop.
            self.data_size += subtree.data_size
            # 2. Properly set all _parent_tree attributes in self._subtrees.
            # Since empty trees' _parent_tree attribute should be None.
            if not subtree.is_empty():
                subtree._parent_tree = self

    def is_empty(self):
        """Return True if this tree is empty.

        @type self: AbstractTree
        @rtype: bool
        """
        return self._root is None

    def generate_treemap(self, rect):
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]

        >>> empty_file = AbstractTree('f0', [], 0)
        >>> empty_file.generate_treemap((0, 0, 800, 1000))
        []
        >>> f1 = AbstractTree('f1', [], 15)
        >>> f2 = AbstractTree('f2', [], 5)
        >>> f3 = AbstractTree('f3', [], 10)
        >>> A = AbstractTree('A', [f1, f2, f3])
        >>> results = A.generate_treemap((0, 0, 800, 1000))
        >>> for result in results:
        ...     print(result[0])
        (0, 0, 800, 500)
        (0, 500, 800, 166)
        (0, 666, 800, 334)
        """
        treemap = list()
        x, y, width, height = rect
        total_data_size = self.data_size

        # If it is an empty tree, an empty folder or a file with zero
        # data_size, then return an empty list i.e. not displayed through
        # treemap visualiser.
        # When a file is deleted, should also return an empty list.
        if not self.data_size:
            return []

        # Since empty leaves are filtered above. So, AbstractTree with empty
        # subtree list can only be displayable laef here. A tuple of pygame
        # rectangle covering the whole displaying area and corresponding random
        # RGB should be returned.
        elif not self._subtrees:
            return [(rect, self.colour)]

        # (Trying hard to come up with some kind of helper method but failed
        # because I tried to mutate global variables (e.g.coordinates and
        # total_data_size) through the local ones inside the helper method,
        # but if I return those variables through the helper method and change
        # them under the global frame, this helper method will not make it
        # any simpler.
        # So, I ended up writing two trivial helper functions (_slice_helper
        # and _update_helper). Although, _update_helper is not concise at all
        # and takes many parameters, I still use it in order to make it more
        # modular and avoid duplicates in code:)
        elif width > height:
            # If width is larger than height, slice vertically.
            # Slice the first (n - 1)th rectangles for a tree with n elements
            # in its subtree list.
            for subtree in self._subtrees[:-1]:
                # Avoid division by zero encountered when remaining subtrees
                # are all empty folders or empty leaves caused by user's
                # deletion, those empty folders or leaves will be ignored since
                # they will not be displayed.
                if total_data_size:
                    new_width = _slice_helper(subtree.data_size,
                                              total_data_size, width)
                    treemap.extend(subtree.generate_treemap
                                   ((x, y, new_width, height)))
                    # Update the rectangle available to draw on and the total
                    # data_size.
                    x, width, total_data_size = \
                        _update_helper(new_width, x, width, subtree.data_size,
                                       total_data_size)
            # Adjust the rectangle for the last element in the subtree list.
            treemap.extend(self._subtrees[-1].generate_treemap
                           ((x, y, width, height)))
            return treemap

        # If width is smaller or equal to height, slice horizontally. Procedures
        # are similar.
        elif width <= height:
            for subtree in self._subtrees[:-1]:
                if total_data_size:
                    new_height = _slice_helper(subtree.data_size,
                                               total_data_size, height)
                    treemap.extend(subtree.generate_treemap
                                   ((x, y, width, new_height)))
                    y, height, total_data_size = \
                        _update_helper(new_height, y, height,
                                       subtree.data_size, total_data_size)
            # Adjust the rectangle for the last element in the subtree list.
            treemap.extend(self._subtrees[-1].generate_treemap
                           ((x, y, width, height,)))
            return treemap

    def rect_dict(self, rect):
        """Used by the treemap visualiser in order to get the AbstractTree
        according to the coordinate, so the keys of the returned dictionary
        are pygame rectangles and the values are AbstractTrees.

        The empty folders and empty files are ignored since they will not be
        displayed through visualiser i.e. have no pygame rectangles and not
        included in the dictionary returned.

        Return an empty dictionary if it is an empty tree, a tree containing
        only empty folders or it contains only empty file(s).

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: dict[tuple, AbstractTree]
        """
        pos_dict = dict()
        x, y, width, height = rect
        total_data_size = self.data_size
        # If it is an empty tree, an empty folder or a file with zero
        # data_size, then return an empty dict i.e. has no chance of being
        # selected by the user through treemap visualiser.
        if not self.data_size:
            return {}

        # Similar to generate_treemap method, empty leaves are filtered above.
        if not self._subtrees:
            temp = dict()
            temp[rect] = self
            return temp

        # Slice the same as generate_treemap.
        elif width > height:
            for subtree in self._subtrees[:-1]:
                # Avoid division by zero encountered when
                # remaining subtrees are all empty folders, those
                # empty folders are ignored since they will not be
                # displayed through visualiser.
                if total_data_size:
                    new_width = _slice_helper(subtree.data_size,
                                              total_data_size, width)
                    pos_dict.update(subtree.rect_dict
                                    ((x, y, new_width, height)))
                    # Update the rectangle available to draw on and the total
                    # data_size.
                    x, width, total_data_size = \
                        _update_helper(new_width, x, width, subtree.data_size,
                                       total_data_size)
            # Adjust the rectangle for the last element in the subtree list.
            pos_dict.update(self._subtrees[-1].rect_dict
                            ((x, y, width, height)))
            return pos_dict

        elif width <= height:
            for subtree in self._subtrees[:-1]:
                if total_data_size:
                    new_height = _slice_helper(subtree.data_size,
                                               total_data_size, height)
                    pos_dict.update(subtree.rect_dict
                                    ((x, y, width, new_height)))
                    # Update the rectangle and total_data_size.
                    y, height, total_data_size = \
                        _update_helper(new_height, y, height,
                                       subtree.data_size, total_data_size)
            # Adjust the rectangle for the last element in the subtree list.
            pos_dict.update(self._subtrees[-1].rect_dict
                            ((x, y, width, height,)))
            return pos_dict

    def del_leaf(self, data_size=0):
        """Delete the selected leaf and update the data size of the deleted
        leaf's ancestors. This method mutates the original tree.

        Used by the treemap visualiser to delete a selected file.

        The first selected leaf should always be an non-empty leaf since
        the user can only choose and delete files that are displayed
        through the visualiser.

        @type self: AbstractTree
        @type data_size: int
            The file's size for its ancestors to subtract. If self is a file,
            then the data_size should not be specified, if self is a folder,
            then the data_size should be the size of the deleted leaf.
        @rtype: None

        >>> f1 = AbstractTree('f1', [], 15)
        >>> f2 = AbstractTree('f2', [], 5)
        >>> f3 = AbstractTree('f3', [], 10)
        >>> A = AbstractTree('A', [f1, f2, f3])
        >>> A.data_size
        30
        >>> f1.del_leaf()
        >>> f1.data_size
        0
        >>> A.data_size
        15
        """
        # If it is a leaf, delete it by making it an empty tree. (Since only
        # non-empty leaf can be chosen through visualiser)
        # Then update its ancestors'data size.
        if not self._subtrees:
            temp = self.data_size
            self.data_size = 0
            self._root = None
            if self._parent_tree:
                self._parent_tree.del_leaf(temp)
                self._parent_tree = None
        # If it is a folder, update its data_size and its ancestors.
        else:
            self.data_size -= data_size
            if self._parent_tree:
                self._parent_tree.del_leaf(data_size)

    def alt_size(self, data_size=0, positive=True):
        """Change the data_size of a file by one percent according to user's
        action, and modify its ancestors' data_size accordingly.
        This method mutates the original tree.

        Used by treemap visualiser to modify the data_size of a selected file.

        Self is Not an empty tree, because only selected leaf's size can be
        modified.
        Similarly, data_size of the file selected is always greater than zero.
        A leaf's data_size cannot decrease below 1. There is no
        upper limit on the value of data_size.
        Its parent tree's data_size is always greater than or equal to its own
        data_size.

        @type self: AbstractTree
        @type data_size: int
            This parameter is not specified when self is a file. If self is a
            folder, it should be the size changed of the leaf, this corresponds
            to the user's action.
        @type positive: bool
            True when the data_size need to be increased, false when data_size
            need to be decreased.
        @rtype: None

        >>> f1 = AbstractTree('f1', [], 15)
        >>> f2 = AbstractTree('f2', [], 2)
        >>> f3 = AbstractTree('f3', [], 10)
        >>> A = AbstractTree('A', [f1, f2, f3])
        >>> f2.alt_size(positive=False)
        >>> f2.data_size
        1
        >>> A.data_size
        26
        >>> f2.alt_size(positive=False)
        >>> f2.data_size
        1
        >>> A.data_size
        26
        """
        # If it is a leaf, change its data_size by one percent, then update
        # its ancestors' if it has any.
        if not self._subtrees:
            # Round up the changed data_size.
            alt_size = math.ceil(self.data_size / 100)
            # Here, multiple 'if' statements are used in order to avoid too many
            # nested blocks and make the code as concise as possible.
            if positive:
                self.data_size += alt_size
            # Update its parent tree if it has one.
            if positive and self._parent_tree:
                self._parent_tree.alt_size(alt_size)
            # Update its parent tree if it has one. Here, the order of following
            # 'if' condition matters because we should not subtract alt_size
            # twice when determing whether data size is greater than 1.
            if not positive and self._parent_tree:
                if self.data_size - alt_size >= 1:
                    self._parent_tree.alt_size(alt_size, positive=False)
            if not positive:
                if self.data_size - alt_size >= 1:
                    self.data_size -= alt_size

        # If it is a folder, update its data_size and its ancestors'.
        else:
            if positive:
                self.data_size += data_size
                if self._parent_tree:
                    self._parent_tree.alt_size(data_size)
            else:
                self.data_size -= data_size
                if self._parent_tree:
                    self._parent_tree.alt_size(data_size, positive=False)

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.

        @type self: AbstractTree
        @rtype: str
        """
        raise NotImplementedError


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/David/csc148/assignments'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """
    def __init__(self, path):
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.

        @type self: FileSystemTree
        @type path: str
        @rtype: None
        """
        if os.path.isfile(path):
            # If it is a file, construct an AbstractTree with its size passed
            # in as a parameter.
            AbstractTree.__init__(self, os.path.basename(path),
                                  [], os.path.getsize(path))
            # A file with positive size will contain an empty list as its
            # subtree. (Leaf type 1)
        else:
            file_list = os.listdir(path)
            subtrees_list = list()
            for file in file_list:
                file_tree = FileSystemTree(os.path.join(path, file))
                subtrees_list.append(file_tree)
            AbstractTree.\
                __init__(self, os.path.basename(path), subtrees_list)
            # Since it is a file, the data_size will not be passed
            # in as a parameter.
            # Here, if it is an empty folder or a file with zero size, then it
            # will be a leaf with empty subtrees_list and the data size will be
            # zero. These leaves will not be displayed throguh visualiser.
            # (Leaf type 2)

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        self._root always has a value i.e. not an empty tree.

        @type self: FileSystemTree
        @rtype: str
        """
        if self._parent_tree:
            return self._parent_tree.get_separator() + '\\' + self._root
        else:
            # Base case: self is at top of the tree.
            return self._root


def _slice_helper(sub_size, total_size, length):
    """Helper function for generate_treemap and rect_dict. Help slice the
    rectangle hrizontally or vertically.

    Total_size is Never zero.

    @type sub_size: int
        The data_size of a file or folder.
    @type total_size: int
        The total data_size of the folder.
    @ type length: int
        The width or heigh need to be sliced.
    @rtype: int
        The sliced portion of width or height.
    """
    portion = sub_size / total_size
    # Round the length down.
    new_length = math.floor(length * portion)
    return new_length


def _update_helper(new_length, coordinate, length, sub_size, total_size):
    """Helper function for generate_treemap and rect_dict. Used to updata the
    coordinate, length and the total_size.

    Length is greater or equal to new_length, and total_size is greater or
    equal to sub_size.

    @type new_length: int
        The sliced portion of original length.
    @type coordinate: int
        The x-coordinate or y-coordinate need to be updated.
    @type length: int
        The width or height need to be updated.
    @type sub_size: int
        The size for total_size to subtract.
    @type total_size:
        The total size of a folder need to be updated.
    @rtype: (int, int, int)
        Return the new coordinate, length and total_size
    """
    coordinate += new_length
    length -= new_length
    total_size -= sub_size
    return coordinate, length, total_size

if __name__ == '__main__':
    import python_ta
    import doctest

    doctest.testmod()
    python_ta.check_errors(config='pylintrc.txt')
    python_ta.check_all(config='pylintrc.txt')
