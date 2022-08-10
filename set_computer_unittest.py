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
            se.CCard(1, "oval", "solid", "red"), se.CCard)

        with self.assertRaises(ValueError):
            se.CCard(0, "oval", "solid", "red")

        with self.assertRaises(ValueError):
            se.CCard(4, "oval", "solid", "red")

        with self.assertRaises(ValueError):
            se.CCard(1, "triangle", "solid", "red")

        with self.assertRaises(ValueError):
            se.CCard(1, "oval", "lol", "red")

        with self.assertRaises(ValueError):
            se.CCard(1, "oval", "solid", "pink")

        with self.assertRaises(ValueError):
            se.CCard(1, 2, 3, 4)

    def test_eq_method(self):
        """"
        Test == equal method
        """
        card1 = se.CCard(1, "oval", "solid", "red")
        card2 = se.CCard(1, "oval", "solid", "red")

        self.assertTrue(card1 == card2)

        card1 = se.CCard(1, "oval", "hatched", "red")

        self.assertFalse(card1 == card2)

        with self.assertRaises(NotImplementedError):
            self.assertTrue(card1 == "ohgotteinFEHLER")

    def test_get_methods(self):
        """
        Test return of get methods
        """
        card = se.CCard(1, "oval", "solid", "red")
        self.assertEqual(card.get_number(), 1)
        self.assertEqual(card.get_symbol(), "oval")
        self.assertEqual(card.get_shading(), "solid")
        self.assertEqual(card.get_color(), "red")
        self.assertIsInstance(card.get_attributes(), dict)

    def test_check_set(self):
        """
        Test SET-checking method
        """
        card1 = se.CCard(1, "oval", "solid", "red")
        card2 = se.CCard(2, "oval", "empty", "red")
        card3 = se.CCard(3, "oval", "hatched", "red")

        self.assertTrue(se.is_a_set(card1, card2, card3))

        card1 = se.CCard(1, "diamond", "solid", "red")

        self.assertFalse(se.is_a_set(card1, card2, card3))

        with self.assertRaises(NotImplementedError):
            se.is_a_set(card1, card2, "hello marvin")


if __name__ == '__main__':
    unittest.main()
