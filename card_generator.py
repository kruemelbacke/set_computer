"""
This is a script to generate 3x4 card matrix
"""
import random
import set_engine as se

class GameField():
    """
    A class to represent the playing field filled with cards
    """
    def __init__(self):
        """
        xx
        """
        self.__field_cards = []
        self.__card_stack = self.generate_card_stack()

    def generate_card_stack(self):
        """
        xx
        """
        card_stack = []
        for number in se.possible_attributes["number"]:
            for symbol in se.possible_attributes["symbol"]:
                for shading in se.possible_attributes["shading"]:
                    for color in se.possible_attributes["color"]:
                        card_stack.append(se.Card(
                            [0,0], number, symbol, shading, color))
        return card_stack

    def pick_random_cards(self, quantity):
        """
        xx
        """
        for i in range(quantity):
            random_card = random.choice(self.__card_stack)
            self.__field_cards.append(random_card)
            self.__card_stack.remove(random_card)

    def show(self):
        """
        xx
        """
        print("Field Cards ("+str(len(self.__field_cards))+"):")
        print("Card Stack ("+str(len(self.__card_stack))+")")
        for card in self.__field_cards:
            print(card.get_attributes())
        print("\n")

if __name__ == '__main__':
    myfield = GameField()
    myfield.show()
    myfield.pick_random_cards(12)
    myfield.show()
