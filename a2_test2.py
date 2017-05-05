"""Unittest of generate_treemap in assignment 2
"""

import os
import unittest

from tree_data import FileSystemTree

PATH = 'C:\\Users\\Xinze Zhao\\Downloads\\csc148\\assignments\\' \
           'Assignment1\\starter_code'
PATH2 = 'C:\\Users\\Xinze Zhao\\Downloads\\csc148\\assignments\\' \
           'Assignment1\\starter_code\\data'


def get_size(path):
    """Get the size of file(s) under the given path..

    @type path: str
    @rtype: None"""
    if os.path.isfile(path):
        print(os.path.basename(path) + ':' + str(os.path.getsize(path)))
    else:
        for file in os.listdir(path):
            get_size(os.path.join(path, file))


def get_total_size(path):
    """Get the total size of files under the path.

    @type path: str
    @rtype: int
    """
    result = 0
    if os.path.isfile(path):
        result += os.path.getsize(path)
        return result
    else:
        for file in os.listdir(path):
            result += get_total_size(os.path.join(path, file))
        return result


class TestGenerateTreemap(unittest.TestCase):
    def test_multiple_nonempty(self):
        file_tree = FileSystemTree(PATH)
        result = file_tree.generate_treemap((0, 0, 800, 1000))
        lst = [(0, 0, 800, 13),
               (0, 13, 800, 20),
               (0, 33, 800, 43),
               (0, 76, 722, 381),
               (722, 76, 16, 381),
               (738, 76, 5, 381),
               (743, 76, 43, 381),
               (786, 76, 1, 381),
               (787, 76, 12, 381),
               (799, 76, 1, 381)]
        for i in range(10):
            self.assertEqual(result[i][0], lst[i])

    def test_one_nonempty(self):
        file_tree = FileSystemTree(PATH2)
        original_len = len(file_tree._subtrees)
        for subtree in file_tree._subtrees[:-1]:
            subtree.del_leaf()
            self.assertEqual(subtree._root, None)
        self.assertEqual(len(file_tree._subtrees), original_len)
        result0 = file_tree.generate_treemap((0, 0, 800, 1000))
        result1 = file_tree.generate_treemap((0, 0, 1000, 800))
        self.assertEqual((0, 0, 800, 1000), result0[0][0])
        self.assertEqual((0, 0, 1000, 800), result1[0][0])

    def test_zero_nonempty(self):
        file_tree = FileSystemTree(PATH2)
        original_len = len(file_tree._subtrees)
        for subtree in file_tree._subtrees:
            subtree.del_leaf()
            self.assertEqual(subtree._root, None)
        self.assertEqual(len(file_tree._subtrees), original_len)
        result0 = file_tree.generate_treemap((0, 0, 800, 1000))
        result1 = file_tree.generate_treemap((0, 0, 1000, 800))
        self.assertEqual([], result0)
        self.assertEqual([], result1)

    def test_one_empty(self):
        file_tree = FileSystemTree(PATH2)
        original_len = len(file_tree._subtrees)
        file_tree._subtrees[-1].del_leaf()
        self.assertEqual(file_tree._subtrees[-1]._root, None)
        self.assertEqual(len(file_tree._subtrees), original_len)
        result = file_tree.generate_treemap((0, 0, 800, 1000))
        lst = [(0, 0, 800, 904),
               (0, 904, 800, 19),
               (0, 923, 800, 6),
               (0, 929, 800, 54),
               (0, 983, 800, 1),
               (0, 984, 800, 16)]
        for each in result:
            self.assertEqual(each[0], lst[result.index(each)])
        for each in lst:
            self.assertEqual(each, result[lst.index(each)][0])

if __name__ == '__main__':
    get_size(PATH)
    print('____________')
    print(get_total_size(PATH))
    print(get_total_size(os.path.join(PATH, 'starter_code\\data')))
    print(get_total_size(os.path.join(PATH, 'starter_code\\__pycache__')))
