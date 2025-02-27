from rich.console import Console
try:
    from msvcrt import getch
except ImportError:
    from getch import getch


class DeferredException(Exception):
    pass


class PlayException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class Scoundrel:
    def __init__(self, starting_health=10):
        __EXCLUDE = [*(4*i + 2 for i in range(11, 15)),
                     *(4*i + 3 for i in range(11, 15))]
        self.__deck = [i for i in range(8, 60) if i not in __EXCLUDE]
        self.__deferred = False
        self.__max_health = starting_health
        self.__health = starting_health
        self.__weapon = [0, 0]
        self.__use_weapon = False
        self.__prompt = 'Press ? for help'

    def start(self):
        from random import shuffle
        shuffle(self.__deck)
        self.__room = self.__deck[0:4]
        self.__console = Console()

        running = True
        while running:
            self.__display()
            if self.__health <= 0:
                self.__console.print('YOU LOSE', style='bold red')
                running = False
            elif len(self.__deck) <= 0:
                self.__console.print('YOU WIN', style='bold green')
                running = False
            else:
                char = getch()
                if char.lower() == 'r':
                    try:
                        self.__run()
                    except DeferredException:
                        self.__prompt = "[yellow]\
You must clear this room before running![/yellow]"
                elif char.lower() == 'w':
                    if not self.__weapon[0]:
                        self.__prompt = '[yellow]\
You don\'t have any weapon to equip[/yellow]'
                    self.__use_weapon = not self.__use_weapon
                elif char >= '1' and char <= '4':
                    self.__play(ord(char) - ord('1'))
                elif char == '?':
                    self.__prompt = '''
\[1-4] Play a card
\[r] Run (you can neither run twice in a row or run while fighting in a room)
\[w] Toggle using your weapon
\[?] Show this help
'''
                else:
                    self.__prompt = 'Press ? for help'
        self.__console.print('Press any key to exit...')
        getch()

    def __run(self):
        if self.__deferred:
            raise DeferredException
        for _ in range(4):
            self.__deck.append(self.__deck.pop(0))
        self.__room = self.__deck[0:4]
        self.__deferred = True

    def __display(self):
        self.__console.clear()
        self.__console.print(
            f"[bold red]:red_heart: {self.__health}/{self.__max_health}"
            "[/bold red]\t"
            f"[bold white]:joker: {len(self.__deck) - len(self.__room)}/44"
            "[/bold white]\t"
            f"{':rabbit2:' if not self.__deferred else ''}\n"
            f"[bold gray{74 if self.__use_weapon else 3}]:dagger: "
            f"{self.__weapon[0]} ({self.__weapon[1]})"
            f"[/bold gray{74 if self.__use_weapon else 3}]\n",
            style='gray3' if self.__deferred else '')
        room = self._get_room()
        for card in room:
            self.__console.print(card, end=' ')
        self.__console.print()
        self.__console.print()
        if self.__prompt:
            self.__console.print(self.__prompt)
            self.__prompt = ''

    def _get_room(self):
        room = []
        suits = [
            "[gray100]{}:spade_suit:[/gray100]",
            "[cyan1]{}:club_suit:[/cyan1]",
            "[orange1]{}:diamond_suit:[/orange1]",
            "[red]{}:heart_suit:[/red]",
        ]
        for card in self.__room:
            if not card:
                room.append('[gray3]--[/gray3]')
                continue
            value = card // 4
            if (value == 11): value = 'J'
            elif (value == 12): value = 'Q'
            elif (value == 13): value = 'K'
            elif (value == 14): value = 'A'
            suit = card % 4
            room.append(suits[suit].format(value))
        return room

    def __draw(self):
        self.__room = self.__deck[0:min(len(self.__deck), 4)]
        self.__deferred = False

    def __play(self, id):
        if self.__room[id] == 0:
            return

        card = self.__room[id]
        value = card // 4
        suit = card % 4

        if (suit == 2):  # Diamond - Weapon
            self.__weapon = [value, 15]
            self.__use_weapon = True
            self.__prompt = f'You equipped a {value} block weapon'
        elif (suit == 3):  # Heart - Heal
            self.__health = min(self.__max_health, self.__health + value)
            self.__prompt = f'You healed for {value}'
        else:  # Black suits - Enemies
            if self.__use_weapon:
                if value > self.__weapon[1]:
                    self.__prompt = '[orange]\
Your weapon is worn, it can\'t block that attack![orange]'
                    return
                else:
                    damage = max(value - self.__weapon[0], 0)
                    self.__weapon[1] = value
                    self.__health -= damage
                    self.__prompt = f'You took {damage} dmg \
(blocked by your sword)'
            else:
                self.__health -= value
                self.__prompt = f'You took {value} dmg'
        self.__deferred = True
        self.__deck.remove(card)
        self.__room[id] = 0
        if self.__room.count(0) >= 3:
            self.__draw()
