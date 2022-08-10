""""
This module represents the game itself with card and rules
"""

possible_attributes = {
    "number": [None, 1, 2, 3],
    "symbol": [None, "oval", "diamond", "wave"],
    "shading": [None, "empty", "hatched", "solid"],
    "color": [None, "red", "green", "purple"]
}


class Card():
    """
    A class to represent a card.

    ...

    Attributes
    ----------

    Methods
    -------
    get_...:
        returns attribute value
    """
    def __init__(self, number=None, symbol=None, shading=None, color=None):
        if not (
            number in possible_attributes["number"]
            and symbol in possible_attributes["symbol"]
            and shading in possible_attributes["shading"]
            and color in possible_attributes["color"]
        ):
            raise ValueError

        self.attributes = {
            "number": number,
            "symbol": symbol,
            "shading": shading,
            "color": color
        }

    def __eq__(self, other):
        """
        Replace default == method
        """
        if not isinstance(other, Card):
            raise NotImplementedError

        return self.get_attributes() == other.get_attributes()

    def get_attributes(self):
        """
        Get all attributes as a dict
        """
        return self.attributes

    def get_number(self):
        """
        Get number of symbols of the card
        """
        return self.attributes["number"]

    def get_symbol(self):
        """
        Get symbol of the card
        """
        return self.attributes["symbol"]

    def get_shading(self):
        """
        Get shading of the symbol
        """
        return self.attributes["shading"]

    def get_color(self):
        """
        Get color of the symbol
        """
        return self.attributes["color"]


def check_val(val1, val2, val3):
    """
    Check if values are all equal or all different

    Returns True if could be a SET candidate -> all equal, all different
    Returns False if only 2 values are equal or different respectivly
    """
    if val1 == val2 and val1 == val3:
        return True
    if val1 != val2 and val1 != val3 and val2 != val3:
        return True

    return False


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
        raise NotImplementedError

    for key in card1.get_attributes():
        could_be_a_set = check_val(
            card1.get_attributes()[key],
            card2.get_attributes()[key],
            card3.get_attributes()[key]
        )

        if could_be_a_set is False:
            return False

    return True


def find_set_primitive_loop(cards):
    """
    Returns a list of 3 cards representing a SET
    or an empty list if no SET was found
    """
    counter = 0
    if len(cards) >= 3:
        for card1 in cards:
            for card2 in cards:
                for card3 in cards:
                    counter += 1
                    if card1 == card2 or card1 == card3 or card2 == card3:
                        continue
                    if is_a_set(card1, card2, card3):
                        return [card1, card2, card3]
    return []


def show_cards(cards):
    """
    Print attributes of given cards
    """
    for card in cards:
        print(card.get_attributes())
    print("\n")
