from __future__ import annotations
import pygame
from ui.button import Button

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class SongTab:
    def __init__(self, 
                 application: Application, 
                 start_pos: int, 
                 song: tuple[str, str, str] = ('name', 'difficulty', 'location'), 
                 highscore: int = -1) -> None:
        '''
        Initialize a SongTab instance.

        Args:
            application (Application): The application context.
            start_pos (int): Starting X-position of the tab.
            song (tuple): A list containing the song's name, difficulty, and location. Defaults to placeholders.
            highscore (int): Highscore for the song. Defaults to -1 (not set).
        '''
        self.application = application
        self.start_pos = start_pos
        self.position = start_pos
        self.song = song
        self.button = Button(
            self.application, 
            text='play', 
            text_size=22, 
            position=(self.position + 125, 400), 
            dimensions=(160, 75), 
            on_click=self.start_song,
            color=(213, 240, 247), 
            alt_color=(0, 162, 232), 
            hover_color=(58, 186, 218), 
            text_color=(0, 0, 0)
        )
        self.highscore = highscore

    def start_song(self) -> None:
        self.application.set_song(self.song)
        self.application.set_screen('performance')

    def render(self) -> None:
        pygame.draw.rect(self.application.screen, (0, 162, 232), (self.position, 115, 250, 350))
        pygame.draw.rect(self.application.screen, (153, 217, 234), (self.position + 5, 120, 240, 340)) # 5 pixels smaller to create a border

        font_40 = self.application.get_font(40)
        font_20 = self.application.get_font(20)
        name_text = font_40.render(self.song[0], True, (0, 0, 0))
        difficulty_text = font_20.render(self.song[1], True, (0, 0, 0))
        self.application.screen.blit(name_text, (self.position + 10, 120))
        self.application.screen.blit(difficulty_text, (self.position + 10, 170))

        if self.highscore >= 0:
            highscore = font_20.render(f'Highscore: {self.highscore}%', True, (0, 0, 0))
            self.application.screen.blit(highscore, (self.position + 10, 200))

    def set_x(self, x) -> None:
        self.button.set_position((self.start_pos + x + 125, 400))
        self.position = self.start_pos + x

    def get_x(self) -> int:
        return self.position