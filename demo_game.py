"""
This is a script to demonstrate one game round
"""
import random
from tqdm import tqdm
import matplotlib.pyplot as plt
import set_engine as se


class CGameField():
    """
    A class to represent the playing field filled with cards
    """
    def __init__(self):
        """
        Init field cards and a full card deck
        """
        self.__field_cards = []

        self.__card_deck = []
        self.generate_card_deck()

    def generate_card_deck(self):
        """
        Generate a full card deck with all possible cards
        """
        card_deck = []
        for number in se.possible_attributes["number"]:
            for symbol in se.possible_attributes["symbol"]:
                for shading in se.possible_attributes["shading"]:
                    for color in se.possible_attributes["color"]:
                        card_deck.append(se.Card(
                            number, symbol, shading, color))
        self.__card_deck = card_deck

    def get_field_cards(self):
        """
        Returns all field cards as list
        """
        return self.__field_cards

    def pick_random_cards(self, quantity):
        """
        Move random cards of the quantity given from the deck to the field
        """
        if len(self.__card_deck) <= 0:
            return False
        for i in range(quantity):  # pylint: disable=unused-variable
            random_card = random.choice(self.__card_deck)
            self.__field_cards.append(random_card)
            self.__card_deck.remove(random_card)
        # print("Picked "+str(quantity)+" cards\n")
        return True

    def show_field(self):
        """
        Print attributes of the field cards
        """
        for card in self.__field_cards:
            print(card.get_attributes())
        print("\n")

    def count_cards(self):
        """
        Print the amount of the cards in the deck and on the field
        """
        print("Card deck ("+str(len(self.__card_deck))+")")
        print("Field Cards ("+str(len(self.__field_cards))+"):\n")

    def remove_field_cards(self, cards):
        """
        Removes given card from field
        """
        for card in cards:
            self.__field_cards.remove(card)


def play_game(verbose_output=False):
    """
    Play one game and return number of during game found SETs
    """
    # init game
    myfield = CGameField()
    if verbose_output is False:
        myfield.count_cards()
    myfield.pick_random_cards(12)

    set_list = []
    set_counter = 0

    # game routine
    while 1:
        if verbose_output is False:
            myfield.count_cards()
        set_list = se.find_set_primitive_loop(myfield.get_field_cards())
        if len(set_list) > 0:
            # found a SET
            set_counter += 1
            if verbose_output is False:
                se.show_cards(set_list)
            myfield.remove_field_cards(set_list)
            if len(myfield.get_field_cards()) >= 12:
                pass
            else:
                if myfield.pick_random_cards(3) is False:
                    break
        else:
            # no SET found
            if myfield.pick_random_cards(3) is False:
                break

    # card deck is empty
    while 1:
        if verbose_output is False:
            myfield.count_cards()
        set_list = se.find_set_primitive_loop(myfield.get_field_cards())
        if len(set_list) > 0:
            # found a SET
            set_counter += 1
            if verbose_output is False:
                se.show_cards(set_list)
            myfield.remove_field_cards(set_list)
        else:
            # no SET found
            break

    # Game finished
    if verbose_output is False:
        print("Game finished after "+str(set_counter)+" found SETs")
    return set_counter


def play_games_and_plot_histogram(number_of_games):
    """
    Play 'number_of_games' times and plot histogram of found SETs in each game
    """
    number_of_found_sets = []
    for i in tqdm(range(number_of_games)):  # pylint: disable=unused-variable
        number_of_found_sets.append(play_game(verbose_output=True))
    plt.hist(number_of_found_sets)
    plt.title("Number of found SETs ("+str(number_of_games)+" games)")
    plt.show()


if __name__ == '__main__':
    play_games_and_plot_histogram(1000)
