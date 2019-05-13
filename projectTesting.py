#The Quest For The Golden Head
#Author: Pranav Krishnan
#Course: ICS3U
#Date: 2016/01/19

import unittest #Include the pyUnit unittest framework
import project
from pygame import *

# The following is the class in which all functions will be ran by unittest
class projectTest(unittest.TestCase):
    ''' Main class for add testing; Can be added to a suite'''

    # Functions beginning with "test" will be ran as a unit test.
    def test_importImage(self):
        # Provide your test cases
        self.assertEqual(project.importImage("images/coss.png"), None)
        self.assertEqual(project.importImage("images/coin.png").get_size(), (34, 34))
        self.assertEqual(project.importImage("images/player/Level2.png").get_size(), (30, 60))
        self.assertEqual(project.importImage("images/player/Level2Walk1.png").get_size(), (28, 60))
        self.assertEqual(project.importImage("images/player/Level2Walk2.png").get_size(), (15, 60))
        self.assertEqual(project.importImage("images/enemy.png").get_size(), (30, 60))
        self.assertEqual(project.importImage("images/grassGround.png").get_size(), (10720, 1416))
        self.assertEqual(project.importImage("images/grassPlat.png").get_size(), (2904, 1416))
        

#Main
if __name__=='__main__':
    unittest.main()
