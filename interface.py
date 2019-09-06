class InterfaceState:
    def __init__(self, change_callback):
        self.dealt_cards = []
        self.robot = None
        #len(self.program) is the number of cards to select (0 - 5)
        self.program = [None, None, None, None, None]
        self.blocked_cards = []
        self.power_down = False
        self.selection_confirmed = False
        self.cursor_index = 0  # 0-4 number of positon
        self.players = []
        self.game_round = None
        # List of winners
        self.winner = []
        self.timer = False
        self.flag_count = 0
        # Change_callback - callback function which is called with argument,
        # when new InterfaceState is created
        self.change_callback = change_callback

    def __repr__(self):
        return f"InterfaceState \
                Cards: {self.dealt_cards}, \
                My Cards: {self.program}, \
                Power Down: {self.power_down,}, \
                Robot: {self.robot}"

    def as_dict(self):
        """
        Return dictionary about state of client_interface."
        """
        return {
            "interface_data": {
                "program": self.program,
                "power_down": self.power_down,
                "confirmed": self.selection_confirmed,
                "game_round": self.game_round,
                }
            }

    def select_card(self, dealt_card_index):
        """
        Select a card from the dealt cards and put on
        a place where selector is (in the robot program)
        and selector cursor moves to the next free place.
        """
        if not self.selection_confirmed:
            if dealt_card_index >= len(self.dealt_cards):
                return
            if dealt_card_index not in self.program:
                self.program[self.cursor_index] = dealt_card_index
                # After select a card Move with cursor to right
                self.cursor_index_plus()

    def return_card(self):
        """
        Return one selected card from your program back to the dealt cards.
        """
        if not self.selection_confirmed:
            self.program[self.cursor_index] = None

    def return_cards(self):
        """
        Return all cards of your program back to the dealt cards.
        """
        if not self.selection_confirmed:
            for card in range(len(self.program)):
                self.program[card] = None
            self.cursor_index = 0
        self.change_callback()

    def cursor_index_plus(self):
        """
        Change selecting cursor position to the next one.
        """
        if not self.selection_confirmed:
            max_cursor_index = len(self.program) - 1
            if self.cursor_index < max_cursor_index:
                self.cursor_index += 1

    def cursor_index_minus(self):
        """
        Change selecting cursor position to the previous one.
        """
        if not self.selection_confirmed:
            if self.cursor_index > 0:
                self.cursor_index -= 1

    def switch_power_down(self):
        """
        Switch power down status between True and False.
        When it is True the Robot doesn't play this round.
        """
        if not self.selection_confirmed:
            if not self.power_down:
                self.power_down = True
            else:
                self.power_down = False
        self.change_callback()

    def confirm_selection(self):
        """
        When indicator is False the player can choose cards and switch Power Down.
        When is True the player ended the selection of cards.
        """
        if None not in self.program:
            self.selection_confirmed = True
