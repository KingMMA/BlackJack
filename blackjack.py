import cards, games


class BJ_Card(cards.Positionable_Card):
    ACE_VALUE = 1
    
    @property
    def value(self):
        if self.is_face_up:
            v = BJ_Card.RANKS.index(self.rank) + 1
            if v > 10:
                v = 10
        else:
            v = None
        return v
    
class BJ_Deck(cards.Deck):
    def populate(self):
        for suit in BJ_Card.SUITS:
            for rank in BJ_Card.RANKS:
                self.cards.append(BJ_Card(rank, suit))
                

class BJ_Hand(cards.Hand):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        
    def __str__(self) -> str:
        rep = self.name  + ":\t" + super().__str__()
        if self.total:
            rep += "(" + str(self.total) + ")"
        return rep
    
    @property
    def total(self):
        for card in self.cards:
            if not card.value:
                return None
        t = 0
        contains_ace = False
        for card in self.cards:
            t += card.value
            if card.value == BJ_Card.ACE_VALUE:
                contains_ace = True
        
        if contains_ace and  t <= 11:
            t += 10
        
        return t
    
    def is_busted(self) -> bool:
        return self.total > 21 
    

class BJ_Player(BJ_Hand):
    
    def __init__(self, name) -> None:
        super().__init__(name)
        self.all_money = 0
    
    def is_lose_all_money(self):
        if abs(self.all_money) != self.all_money or not bool(self.all_money):
            return True
        else:
            return False
    
    def is_hitting(self):
        response = games.ask_yes_no("\n" + self.name + ", братиме ще карти ")
        return response == "y"
    
    def bust(self, all_players: list):
        print(f"{self.name} перебрав(-ла).")
        if self.lose():
            all_players.remove(self)
    
        
    def lose(self):
        print(f"Гравець '{self.name}' програв {self.money_for_rate} гривню")
        self.all_money = self.all_money - self.money_for_rate
        if self.is_lose_all_money():
            print(f"Гравець '{self.name}' витратив всі гроші")
            print("Він покидає стол")
            return True
        else:
            print(f"Баланс гравця '{self.name}': {self.all_money}")
      
    @property
    def set_money(self):
        return self.all_money
    
    @set_money.setter
    def set_money(self, money):
        if self.all_money != 0:
            pass
        if money > 0:
            self.all_money = money
        else:
            print("Не допустима кількість грошей")
            self.set_money = int(input(f"Скільки грошей у вас, {self.name}?: "))
                    
    @property
    def set_bet(self):
        return self.money_for_rate
    
    @set_bet.setter
    def set_bet(self, bet):
        if bet > 0 and bet <= self.all_money:
            self.money_for_rate = bet
        else:
            print("Не допустима ставка")
            self.set_bet = int(input(f"Ваша ставка, {self.name}?: "))
            
           
    def win(self):
        print(f"Гравець '{self.name}' виграв {self.money_for_rate} гривень")
        self.all_money = self.all_money + self.money_for_rate
        print(f"Баланс гравця '{self.name}': {self.all_money}")
        
    def push(self):
        print(f"{self.name} зіграв(-ла) з дилером в нічию.")
        print(f"Баланс гравця '{self.name}': {self.all_money}")
        
    def want_continue(self):
        res = games.ask_yes_no(f"Бажаєте грати, {self.name}? ")
        if res == "y":
            return True
        else:
            self.all_money = self.all_money - (self.money_for_rate * 0.5)
            print(f"Гравець '{self.name}' програв 50% ставки")
            print(f"Баланс гравця '{self.name}': {self.all_money}")
            return False
        

class BJ_Dealer(BJ_Hand):
    
    def is_hitting(self):
        return self.total < 17 
    
    def bust(self):
        print(f"{self.name} перебрав.")
        
    def flip_first_card(self):
        first_card = self.cards[0]
        first_card.flip()
        
        
class BJ_Game:
    
    def __init__(self, names) -> None:
        self.players: list[BJ_Player] = []
        self.del_players = []
        for name in names:
            self.players.append(BJ_Player(name))  
        self.dealer = BJ_Dealer("Дилер")
        self.deck = BJ_Deck()
        self.deck.populate()
        self.deck.shuffle()
        
    @property
    def still_playing(self):
        sp: list[BJ_Player] = []
        for player in self.players:
            if not player.is_busted():
                sp.append(player)
        return sp
    
    def __additional_cards(self, player: BJ_Player):
        while not player.is_busted() and player.is_hitting():
            self.deck.deal([player])
            print(player)
            print(self.dealer)
            if player.is_busted():
                player.bust(self.players)
        
                
    def play(self):
        if not bool(self.players):
            raise Exception
        for player in self.players:
            player.set_money = int(input(f"Скільки грошей у вас, {player.name}?: "))
            player.set_bet = int(input(f"Ваша ставка, {player.name}?: "))
        if len(self.deck.cards) < ((len(self.players) + 1) * 2) :
            self.add_new_deck()
        self.deck.deal(self.players + [self.dealer], per_hand=2)
        self.dealer.flip_first_card()
        for player in self.players:
            print(player)
            if player.want_continue():
                print(player)
                print(self.dealer)
            else:
                self.players.remove(player)
        for player in self.players:
            self.__additional_cards(player)
        self.dealer.flip_first_card()
        if not self.still_playing:
            print(self.dealer)
        else:
            print(self.dealer)
            self.__additional_cards(self.dealer)
            if self.dealer.is_busted():
                for player in self.still_playing:
                    player.win()
            else:
                for player in self.still_playing:
                    if player.total > self.dealer.total:
                        player.win()
                    elif player.total < self.dealer.total:
                        if player.lose():
                            self.players.remove(player)
                    else:
                        player.push()
        
        for player in self.players:
            player.clear()
        self.dealer.clear()
        
def main():
    print("\t\tЛаскава просимо до гри Блек-Джек\n")
    
    names = []
    number = games.ask_number("Скільки всього гравців (1-7): ", low=1, high=7)
    
    for i in range(number):
        name = input(f"Введіть ім'я гравця №{i+1}: ")
        names.append(name)
    
    print()
    
    game = BJ_Game(names)
    game.play()
    again = None
    try:
        while again != "n":
            game.play()
            again = games.ask_yes_no("\nБажаєте зіграти ще раз")
    except Exception:
        print("Гра завершена.")
    
main()
