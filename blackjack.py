import pandas as pd
import random

class Blackjack:
    def __init__(self, n_decks=1, money=0, count_dict={2:1,3:1,4:1,5:1,6:1,7:0,8:0,9:0,10:-1,'A':-1}):
        self.n_decks = n_decks
        self.deck = [2,3,4,5,6,7,8,9,10,10,10,10,'A'] * 4 * n_decks
        random.shuffle(self.deck)
        self.money = money
        self.count_dict = count_dict
        self.player_hand = []
        self.dealer_hand = []
        self.excess_hands = []
        self.dealt_cards = 0
        self.count = 0

    def reset_deck(self):
        self.deck = [2,3,4,5,6,7,8,9,10,10,10,10,'A'] * 4 * self.n_decks
        random.shuffle(self.deck)
        self.dealt_cards = 0
        self.count = 0

    def load_rules(self, path):
        self.rules_df = pd.read_csv(path)
        self.handindex = {}
        for i in range(len(self.rules_df)):
            self.handindex[self.rules_df['PlayerHand'].iloc[i]] = i

    def deal_card(self, player=True):
        card = self.deck.pop()
        self.dealt_cards += 1
        self.count += self.count_dict[card]
        if player:
            self.player_hand.append(card)
        else:
            self.dealer_hand.append(card)

    def deal(self):
        self.deal_card()
        self.deal_card(player=False)
        self.deal_card()
        self.deal_card(player=False)

    def clear_cards(self):
        self.player_hand = []
        self.excess_hands = []
        self.dealer_hand = []

    def total(self, hand):
        tot = 0
        n_aces = 0
        for x in hand:
            if x != 'A':
                tot += x
            else:
                n_aces += 1
        n_elevens = n_aces
        n_ones = 0
        while tot + 11 * n_elevens + n_ones > 21 and n_elevens > 0:
            n_elevens -= 1
            n_ones += 1
        return tot + 11 * n_elevens + n_ones

    def action(self, hand, dealercard):
        if self.total(hand) > 21:
            return 'S'
        if 'A' in hand:
            tot = self.total(hand)
            if tot == 12:
                handstr = 'A.A'
            else:
                handstr = 'A.{}'.format(str(tot - 11))
            # print('handstr', handstr)
            return self.rules_df[str(dealercard)].iloc[self.handindex[handstr]]
        elif len(hand) == 2 and hand[0] == hand[1]:
            splithand = '{}.{}'.format(str(hand[0]), str(hand[0]))
            return self.rules_df[str(dealercard)].iloc[self.handindex[splithand]]
        else:
            tot = self.total(hand)
            return self.rules_df[str(dealercard)].iloc[self.handindex[str(tot)]]

    def play_hand(self, bet):
        action = self.action(self.player_hand, self.dealer_hand[0])
        if action == 'SP':
            self.player_hand = [self.player_hand[0]]
            self.deal_card()
            excess_hand = [self.player_hand[0]]
            card = self.deck.pop()
            self.dealt_cards += 1
            self.count += self.count_dict[card]
            excess_hand.append(card)
            self.excess_hands.append(excess_hand)
            res = self.play_hand(bet)
            return res
        elif action == 'D':
            self.deal_card()
            if len(self.player_hand) > 3:
                return 1
            else:
                return 2
            # if self.total(self.player_hand) > 21:
            #     self.money -= 2 * bet
            #     return 0
            # while self.total(self.dealer_hand) < 17:
            #     self.deal_card(player=False)
            # if self.total(self.player_hand) > self.total(self.dealer_hand):
            #     self.money += 2 * bet
            #     return 1
            # elif self.total(self.player_hand) < self.total(self.dealer_hand):
            #     self.money -= 2 * bet
            #     return 0
            # else:
            #     return -1
        elif action == 'DS':
            if len(self.player_hand) == 2:
                self.deal_card()
                return 2
            else:
                return 1
        elif action == 'H':
            self.deal_card()
            # if self.total(self.player_hand) > 21:
            #     self.money -= bet
            #     return 0
            res = self.play_hand(bet)
            return res
        elif action == 'S':
            return 1
            # if self.total(self.player_hand) > self.total(self.dealer_hand):
            #     self.money += bet
            #     return 1
            # elif self.total(self.player_hand) < self.total(self.dealer_hand):
            #     self.money -= bet
            #     return 0
            # else:
            #     return -1

    def play_round(self, bet):
        self.clear_cards()
        self.deal()

        if self.player_hand in [['A',10], [10,'A']]:
            self.money += 1.5 * bet
            return
        elif self.dealer_hand in [['A',10], [10,'A']]:
            self.money -= bet
            return
        outcomes = []
        single = self.play_hand(bet)
        outcomes.append((self.total(self.player_hand), single))
        while len(self.excess_hands) > 0:
            self.player_hand = self.excess_hands.pop()
            single = self.play_hand(bet)
            outcomes.append((self.total(self.player_hand), single))
        while self.total(self.dealer_hand) < 17:
            self.deal_card(player=False)
        for x in outcomes:
            tot = x[0]
            single = x[1]
            dealer_tot = self.total(self.dealer_hand)
            if tot > 21:
                self.money -= single * bet
            elif dealer_tot > 21:
                self.money += single * bet
            else:
                if tot > dealer_tot:
                    self.money += single * bet
                elif tot < dealer_tot:
                    self.money -= single * bet

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np
    bjack = Blackjack(n_decks = 6)
    ncards = len(bjack.deck)
    bjack.load_rules('rules.csv')
    portfolios = []
    end_vals = []
    for i in range(200):
        bjack = Blackjack(n_decks = 6)
        ncards = len(bjack.deck)
        bjack.load_rules('rules.csv')
        money = []
        for i in range(4000):
            true_count = bjack.count / (bjack.n_decks * (ncards - bjack.dealt_cards) / ncards)
            if true_count < 0:
                bjack.play_round(bet=3)
            elif true_count < 1:
                bjack.play_round(bet=6)
            elif true_count < 2:
                bjack.play_round(bet=9)
            else:
                bjack.play_round(bet=100)
            # print(bjack.player_hand, bjack.excess_hands, bjack.dealer_hand, bjack.money)
            # print()
            money.append(bjack.money)
            if len(bjack.deck) < ncards / 3:
                bjack.reset_deck()
        portfolios.append(money)
        end_vals.append(money[-1])
    for x in portfolios:
        plt.plot(x)
    plt.show()
    plt.hist(end_vals, bins=20)
    plt.show()
    print(np.mean(np.array(end_vals)))
    print(np.std(np.array(end_vals)))
