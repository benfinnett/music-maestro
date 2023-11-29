from __future__ import annotations

if __name__ == '__main__':
    print('[Music Maestro] Please run "main.pyw" to start the program.')
    raise SystemExit()

import os
import pygame
from audio.audio_manager import AudioManager
from screen.login import Login
from screen.main_menu import MainMenu
from screen.options import Options
from screen.song_select import SongSelect
from screen.calibrate import Calibrate
from screen.performance import Performance
from screen.analysis import Analysis
from user.user import User

# Handle type checking without incurring a circular import error as TYPE_CHECKING is always False at runtime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.button import Button
    from ui.scrollbar import ScrollBar
    from ui.text_input import TextInput
    from ui.song_tab import SongTab

class Application:
    def __init__(self):
        self.BACKGROUND_COLOR = (255, 255, 255)
        self.WINDOW_SIZE = (1280, 720)
        self.font_sizes = {}
        self.images = {}

        # Load all images
        self.images = {
            name: pygame.image.load(path) for path, name in self.load_files()
        }
        self.backgrounds = [
            image for name, image in self.images.items() if 'background' in name
        ]

        # Initialise screen
        pygame.init()
        self.overlay = pygame.Surface(self.WINDOW_SIZE)
        self.overlay.set_alpha(50)
        self.overlay.fill(self.BACKGROUND_COLOR)
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption('Music Maestro')
        pygame.display.set_icon(self.images['icon'])
        
        self.screen_buttons: list[Button] = []
        self.scroll_bar: ScrollBar | None = None
        self.text_inputs: list[TextInput] = []
        self.song_tabs: list[SongTab] = []
        self.song: tuple[str, str, str] | None = None
        
        self.screens = {
            'main_menu': MainMenu(self),
            'song_select': SongSelect(self),
            'options': Options(self),
            'login': Login(self),
            'calibrate': Calibrate(self),
            'performance': Performance(self),
            'analysis': Analysis(self)
        }

        self.clock = pygame.time.Clock()
        self.audio = AudioManager()

        self.performance_results = {}

        # Default note values
        self.default_notes = {
            'A': [440],
            'A#/Bb': [466],
            'B': [493],
            'C': [523],
            'C#/Db': [554],
            'D': [587],
            'D#/Eb': [622],
            'E': [659],
            'F': [698],
            'F#/Gb': [739],
            'G': [783],
            'G#/Ab': [830]
        }
        self.reset_notes()

        self.user = User()

    def _handle_event(self, event: pygame.event.Event) -> None:
        mouse_position = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if event.type == pygame.QUIT:
            self.quit()
        
        if self.scroll_bar:
            self.scroll_bar.check(mouse_position, mouse_clicked)

        if event.type == pygame.KEYDOWN:
            if event.unicode:
                for text_input in self.text_inputs:
                    text_input.key_press(event.unicode)
                
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        for button in self.screen_buttons:
            if button.is_hovered(mouse_position):
                button.call()
                return
            
    def reset_notes(self) -> None:
        self.notes = self.default_notes.copy()
            
    def clear_screen(self) -> None:
        self.screen.fill(self.BACKGROUND_COLOR)
        self.screen_buttons = []
        self.scroll_bar = None
        self.text_inputs = []
        self.song_tabs = []

    def run_event_loop(self) -> None:
        self.current_screen.setup()
        while True:
            mouse_position = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]

            for event in pygame.event.get():
                self._handle_event(event)

            for button in self.screen_buttons:
                button.is_hovered(mouse_position)

            for text_input in self.text_inputs:
                text_input.check(mouse_position, mouse_clicked)

            self.current_screen.render_dynamic_elements(mouse_position=mouse_position)
            pygame.display.flip()
            
    def load_files(self, extensions: list[str] = ['.png', '.jpg']) -> list[list[str]]:
        '''
        Load files from the directory the program is run from and all child directories.
        
        Args:
            extensions (list): List of all file extensions to whitelist during the directory walk
                               default: ['.png', '.jpg']
        Returns:
            location (list): Contains all file names and addresses of files that have the desired extensions
        '''
        # Traverse all child directories and get contenets
        directories = [
            [file_names, dir_path] for dir_path, _, file_names in os.walk('.')
        ]
        location = []
        # Each child directory
        for i, directory in enumerate(directories):
            file_names, dir_path = directory
            # Each file in child directory
            for j, file_name in enumerate(file_names):
                name, extension = os.path.splitext(file_name)
                if extension in extensions:
                    path = dir_path + '\\' + directories[i][0][j]
                    location.append([path, name])
        return location

    def get_font(self, size: int) -> pygame.font.Font:
        if size not in self.font_sizes:
            self.font_sizes[size] = self.load_font(size)
        return self.font_sizes[size]
    
    def quit(self) -> None:
        '''
        End all PyGame processes and close the PyGame window.
        '''
        pygame.font.quit()
        pygame.quit()
        raise SystemExit
    
    def set_screen(self, screen_name: str):
        if screen_name not in self.screens:
            raise KeyError(f'Screen {screen_name} does not exist.')
        
        self.current_screen = self.screens[screen_name]

        if screen_name not in ('calibrate', 'performance'):
            self.run_event_loop()
        else:
            self.current_screen.setup()

    def set_song(self, song: tuple[str, str, str]) -> None:
        self.song = song
    
    @staticmethod
    def load_font(size: int) -> pygame.font.Font:
        return pygame.font.Font('.\\assets\\font.ttf', size)