"""
Game interface.
Client which receives data about its robot, cards and state of the game from
server. It sends messages with its state to server.
"""
import asyncio
import aiohttp
import pyglet
from time import monotonic

from interface_frontend import draw_interface, create_window, handle_text, handle_click
from interface import InterfaceState
from backend import State
from util_network import set_argument_value, tick_asyncio


class Interface:
    def __init__(self, server_ip):
        # Game attributes
        self.window = create_window(self.window_draw, self.on_text, self.on_mouse_press)
        # When something has changed in interface state, the function 'send_state_to_server' is called.
        self.interface_state = InterfaceState(change_callback=self.send_state_to_server)
        self.game_state = None
        self.winner_time = None
        # Connection attribute
        self.ws = None
        self.server_ip = server_ip

    def window_draw(self):
        """
        Draw the window containing game interface with its current state.
        """
        self.window.clear()
        draw_interface(self.interface_state, self.game_state, self.winner_time, self.window)

    def on_text(self, text):
        """
        Key listener.
        Wait for user input on keyboard and react for it.
        """
        handle_text(self.interface_state, text)

    def on_mouse_press(self, x, y, button, mod):
        """
        Interface is handled by mouse press.
        """
        handle_click(self.interface_state, x, y, self.window)

    def send_state_to_server(self):
        """
        Send message with interface_state to server.
        """
        if self.ws:
            message = self.interface_state.as_dict()
            message["interface_data"]["game_round"] = self.game_state.game_round
            asyncio.ensure_future(self.ws.send_json(message))

    async def get_messages(self):
        """
        Connect to server and receive messages.
        Process information from server: game state, robot and cards.
        """
        # create Session
        async with aiohttp.ClientSession() as session:
            # create Websocket
            async with session.ws_connect('http://' + self.server_ip + ':8080/interface/') as self.ws:
                # Cycle "for" is finished when client disconnects from server
                async for message in self.ws:
                    message = message.json()
                    if "robot_name" in message:
                        robot_name = message["robot_name"]
                    if "game_state" in message:
                        self.set_game_state(message, robot_name)
                    if "robots" in message:
                        self.set_robots(message, robot_name)
                    if "cards" in message:
                        self.interface_state.dealt_cards = self.game_state.cards_from_dict(message["cards"])
                    if "winner" in message:
                        self.game_state.winners = message["winner"]
                        self.winner_time = monotonic()
                    if "timer_start" in message:
                        self.interface_state.timer = monotonic()
                    if "blocked_cards" in message:
                        self.set_blocked_cards(message["blocked_cards"])
                    if "current_game_round" in message:
                        self.game_state.game_round = message["current_game_round"]
                    if "round_over" in message:
                        self.interface_state = InterfaceState(change_callback=self.send_state_to_server)

        self.ws = None

    def set_game_state(self, message, robot_name):
        """
        Set game attributes using data from server message:
        - create game state, call set_robots.
        """
        self.game_state = State.whole_from_dict(message)
        self.set_robots(message["game_state"], robot_name)

    def set_robots(self, message, robot_name):
        """
        Set robots, players and self robot using data from sent message.
        """
        self.game_state.robots = self.game_state.robots_from_dict(message)
        for robot in self.game_state.robots:
            if robot.name == robot_name:
                self.interface_state.robot = robot

    def set_blocked_cards(self, cards):
        """
        Set blocked cards from the message obtained from server.
        """
        self.interface_state.blocked_cards = self.game_state.cards_from_dict(cards)
        del self.interface_state.program[:len(self.interface_state.blocked_cards)]


def main():
    server_ip = set_argument_value("localhost")
    interface = Interface(server_ip)

    pyglet.clock.schedule_interval(tick_asyncio, 1/30)
    asyncio.ensure_future(interface.get_messages())


if __name__ == "__main__":
    main()
    pyglet.app.run()
