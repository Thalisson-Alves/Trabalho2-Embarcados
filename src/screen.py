import curses
import io
import os
import logging
from curses.textpad import rectangle
from typing import Tuple
from oven_status import OvenState, HeatingStatus
from enum import Enum


class Box:
    def __init__(self, win: 'curses._CursesWindow', size: Tuple[int, int], pos: Tuple[int, int], title: str = '') -> None:
        self.win = win
        self.h, self.w = size
        self.y, self.x = pos
        self.title = title and title.center(len(title) + 4)
        self.title_attr = []

    def render(self):
        rectangle(self.win, self.y, self.x, self.y + self.h, self.x + self.w)
        if not self.title:
            return

        for at in self.title_attr:
            self.win.attron(at)

        self.win.addstr(self.y, self.x + centered_x(self.title, self.w), self.title)

        for at in self.title_attr:
            self.win.attroff(at)

    def write(self, y: int, x: int, s: str, *, center: bool = False) -> None:
        if center:
            x = centered_x(s, self.w)
        self.win.addstr(self.y + y, self.x + x, s)


class _ScreenState(Enum):
    PID = 0
    CONTROL_MODE = 1
    TEMPERATURE = 2
    MENU = 3


class Screen:
    def __init__(self) -> None:
        self.option_selected = 0
        self.state = _ScreenState.MENU
        os.environ.setdefault('ESCDELAY', '10')

    def run(self, stdscr: 'curses._CursesWindow'):
        self.initialize(stdscr)
        while True:
            self.update()
            self.render()

            curses.napms(10)

    def initialize(self, stdscr: 'curses._CursesWindow'):
        self.stdscr = stdscr
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        curses.curs_set(0)

        self.initialize_boxes()

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def initialize_boxes(self):
        h, w = self.size

        self.system_state_box = Box(self.stdscr, (4, w // 3 - 2),
                                    (3, 1), 'Estado do Sistema')
        self.working_state_box = Box(self.stdscr, (4, w // 3 - 2),
                                     (3, 1 + w // 3), 'Estado de Funcionamento')
        self.control_mode_box = Box(self.stdscr, (4, w // 3 - 2),
                                    (3, 1 + 2 * w // 3), 'Modo de Controle')

        self.options = [
            'Alterar Constantes do PID',
            'Alterar Modo de Controle',
            'Alterar a Temperatura de Referência',
            'Sair',
        ]
        self.menu_box = Box(self.stdscr, (len(self.options) + 1, w - 2), (8, 1), 'Menu')

        self.pid_box = Box(self.stdscr, (6, w // 2 - 2), (14, 1), 'Constantes PID')
        self.temperature_box = Box(self.stdscr, (6, w // 2 - 2), (14, w // 2 + 1), 'Temperaturas')

        self.boxes = [
            self.system_state_box,
            self.working_state_box,
            self.control_mode_box,
            self.menu_box,
            self.pid_box,
            self.temperature_box,
        ]

    def update(self):
        user_input = self.stdscr.getch()
        if user_input == curses.KEY_RESIZE:
            self.initialize_boxes()
        elif user_input == 27:  # ESC
            self.option_selected = 0
            self.state = _ScreenState.MENU

        self.navigate(user_input)

    def navigate(self, user_input):
        if user_input in (curses.KEY_DOWN, ord('j'), curses.KEY_RIGHT, ord('l'), ord('\t')):
            self.option_selected = (self.option_selected + 1) % self.navigate_size()
        elif user_input in (curses.KEY_UP, ord('k'), curses.KEY_LEFT, ord('h'), curses.KEY_BTAB):
            self.option_selected = (self.option_selected - 1) % self.navigate_size()
        elif user_input == 10:  # Enter
            self.apply_action()

    def navigate_size(self):
        if self.state == _ScreenState.MENU:
            return len(self.options)
        if self.state == _ScreenState.CONTROL_MODE:
            return 3
        if self.state == _ScreenState.PID:
            return 3
        if self.state == _ScreenState.TEMPERATURE:
            return 1

    def apply_action(self):
        if self.state == _ScreenState.MENU:
            self.apply_menu_action()
        elif self.state == _ScreenState.CONTROL_MODE:
            self.apply_control_mode_action()

    def apply_menu_action(self):
        if self.option_selected == 3:
            exit(0)

        self.state = _ScreenState(self.option_selected)
        self.option_selected = 0

    def apply_control_mode_action(self):
        # TODO: update OvenState. Update UART
        ...

    def render(self):
        self.stdscr.erase()

        for func_name in filter(lambda x: x.startswith('render_'), dir(self)):
            getattr(self, func_name)()

        for box in self.boxes:
            box.render()

        self.stdscr.refresh()

    def render_title(self):
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.attron(curses.A_BOLD)

        title = 'Controlador do Forno'
        cx = centered_x(title, self.size[1])
        self.stdscr.addstr(1, cx, title)

        self.stdscr.attroff(curses.color_pair(1))
        self.stdscr.attroff(curses.A_BOLD)

    def render_state(self):
        self.system_state_box.write(2, 0, format_value(OvenState.on), center=True)
        self.working_state_box.write(2, 0, format_value(OvenState.heating), center=True)

    def render_control_mode(self):
        if self.state != _ScreenState.CONTROL_MODE:
            self.control_mode_box.write(2, 0, format_value(OvenState.heating_status.name), center=True)
            return

        offset = (self.control_mode_box.w // 3)
        for i, mode in enumerate(HeatingStatus, 1):
            if i - 1 == self.option_selected:
                self.stdscr.attron(curses.color_pair(3))

            self.control_mode_box.write(2, offset * (i - 1), mode.name.center(offset))

            if i - 1 == self.option_selected:
                self.stdscr.attroff(curses.color_pair(3))

    def render_temperature(self):
        temperatures = (('Temperatura de Referência', OvenState.reference_temp),
                        ('Temperatura Interna', OvenState.internal_temp),
                        ('Temperatura Ambiente', OvenState.internal_temp))
        for i, (name, value) in enumerate(temperatures, 2):
            v = format_value(value)
            self.temperature_box.write(i, 4, name.ljust(self.temperature_box.w - len(v) - 5, '_') + v)

    def render_pid(self):
        for i, name in enumerate('PID', 2):
            v = format_value(getattr(OvenState, name.lower(), None))
            self.pid_box.write(i, 4, f'Constante {name}'.ljust(self.temperature_box.w - len(v) - 5, '_') + v)

    def render_menu(self):
        for i, option in enumerate(self.options, 1):
            if self.state == _ScreenState.MENU and i - 1 == self.option_selected:
                self.menu_box.write(i, 2, '>')
                self.stdscr.attron(curses.color_pair(3))

            option = f'{i}. {option}'
            self.menu_box.write(i, 4, option.ljust(self.menu_box.w - 5))

            if self.state == _ScreenState.MENU and i - 1 == self.option_selected:
                self.stdscr.attroff(curses.color_pair(3))

    @property
    def size(self) -> Tuple[int, int]:
        return self.stdscr.getmaxyx()


def centered_x(s: str, w: int) -> int:
    return w // 2 - len(s) // 2


def format_value(value) -> str:
    if value is None:
        return '???'
    if isinstance(value, bool):
        return ('OFF', 'ON')[value]
    if isinstance(value, float):
        return f'{value:.2f}'
    return str(value)