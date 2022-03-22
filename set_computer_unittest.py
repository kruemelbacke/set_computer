"""
This module is to test "set_computer.py"
"""
import unittest
import set_engine as se

class TestStringMethods(unittest.TestCase):
    """
    Test Class
    """
    def test_init(self):
        """
        Test init method
        """
        self.assertIsInstance(
            se.Card([0,0], 1, "oval", "solid", "red"), se.Card)

        with self.assertRaises(ValueError):
            se.Card([-1,0], 1, "oval", "solid", "red")
            
        with self.assertRaises(ValueError):
            se.Card([0,-1], 1, "oval", "solid", "red")
            
        with self.assertRaises(ValueError):
            se.Card([3,0], 1, "oval", "solid", "red")
            
        with self.assertRaises(ValueError):
            se.Card([0,4], 1, "oval", "solid", "red")
            
        with self.assertRaises(ValueError):
            se.Card([0,0], 0, "oval", "solid", "red")
            
        with self.assertRaises(ValueError):
            se.Card([0,0], 4, "oval", "solid", "red")
            
        with self.assertRaises(ValueError):
            se.Card([0,0], 1, "triangle", "solid", "red")
            
        with self.assertRaises(ValueError):
            se.Card([0,0], 1, "oval", "lol", "red")
                
        with self.assertRaises(ValueError):
            se.Card([0,0], 1, "oval", "solid", "pink")
                
        with self.assertRaises(ValueError):
            se.Card(0, 1, 2, 3, 4)


    def test_get_methods(self):
        """
        Test return of get methods
        """
        card = se.Card([0,0], 1, "oval", "solid", "red")
        self.assertEqual(card.get_position(),[0,0])
        self.assertEqual(card.get_number(), 1)
        self.assertEqual(card.get_symbol(), "oval")
        self.assertEqual(card.get_shading(), "solid")
        self.assertEqual(card.get_color(), "red")
        self.assertIsInstance(card.get_attributes(), dict)

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()