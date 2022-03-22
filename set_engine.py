""""
This module represents the game itself with card and rules
"""

class Card():
    """
    A class to represent a card.

    ...

    Attributes
    ----------
    position : list of int
        x,y coordinates on the game board
    number : int
        count of symbols on card (1, 2 or 3)
    symbol : str
        kind of symbol ("oval", "diamond" or "wave")
    shading : str
        kind of shading ("empty, "hatched" or "solid")
    color : str
        color of the symbols ("red", "green" or "purple")

    Methods
    -------
    get_...:
        returns attribute value
    """
    def __init__(self, position, number, symbol, shading, color):
        if not (
            isinstance(position, list)
            and len(position) == 2
            and isinstance(position[0], int)
            and position[0] >= 0
            and position[0] <= 2
            and isinstance(position[1], int)
            and position[1] >= 0
            and position[1] <= 6
            and number in [1,2,3]
            and symbol in ["oval", "diamond", "wave"]
            and shading in ["empty", "hatched", "solid"]
            and color in ["red", "green", "purple"]
        ):
            raise ValueError


        self.__position = position # [x, y]
        self.__attributes = {
            "number" : number,
            "symbol" : symbol,
            "shading": shading,
            "color"  : color
        }

    def get_attributes(self):
        """
        Get all attributes as a dict
        """
        return self.__attributes

    def get_position(self):
        """
        Get position of the card
        """
        return self.__position

    def get_number(self):
        """
        Get number of symbols of the card
        """
        return self.__attributes["number"]

    def get_symbol(self):
        """
        Get symbol of the card
        """
        return self.__attributes["symbol"]

    def get_shading(self):
        """
        Get shading of the symbol
        """
        return self.__attributes["shading"]

    def get_color(self):
        """
        Get color of the symbol
        """
        return self.__attributes["color"]


def is_a_set(card1, card2, card3):
    """
    A function to check if the given cards are a SET.
    """
    if not (
        isinstance(card1, Card)
        and isinstance(card2, Card)
        and isinstance(card3, Card)
    ):
        # don't attempt to compare against unrelated types
        return NotImplemented

    for key in card1.get_attributes():
        could_be_a_set = check_val(
            card1.get_attributes()[key],
            card2.get_attributes()[key],
            card3.get_attributes()[key]
        )

        if could_be_a_set is False:
            return False

    return True


def check_val(val1, val2, val3):
    """
    Check if values are all equal or all different

    Returns True if could be a SET candidate -> all equal, all different
    Returns False if only 2 values are equal or different respectivly
    """
    if val1 == val2 == val3:
        return True
    if val1 != val2 != val3:
        return True

    return False
