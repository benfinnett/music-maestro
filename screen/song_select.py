from __future__ import annotations
import pygame

from screen.screen import BaseScreen
from ui.button import Button
from ui.scrollbar import ScrollBar
from ui.song_tab import SongTab

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class SongSelect(BaseScreen):
    def __init__(self, application: Application) -> None:
        super().__init__(application)

    def add_buttons(self) -> None:
        '''
        Clears existing buttons and adds the main menu buttons to the screen_buttons list.
        '''
        self.application.screen_buttons = []
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Back', 
                position=(128, 648), 
                dimensions=(160, 75),
                on_click=lambda: self.application.set_screen('main_menu'))
        )

    def create_song_tabs(self) -> None:
        '''
        Create song tabs for each song in the list.
        '''
        self.application.song_tabs = []
        songs = self.application.load_files(extensions=['.txt'])
        user_data = self.application.user.get_data()

        for i, song in enumerate(songs):
            song_name, song_difficulty = song[1].split(' - ')
            song_location = song[0]
            highscore = int(user_data.get(song_name, -1))
            start_pos = round((i + 1) * (250 + 25)) - 135

            song_tab = SongTab(
                self.application, 
                start_pos=start_pos, 
                song=(song_name, song_difficulty, song_location),
                highscore=highscore
            )
            self.application.screen_buttons.append(song_tab.button)
            self.application.song_tabs.append(song_tab)
    
    def add_scrollbar(self) -> None:
        if not self.application.song_tabs:
            self.create_song_tabs()

        self.application.scroll_bar = ScrollBar(
            self.application, 
            dimensions=(1000, 20), 
            position=(640, 504), 
            scroll_length=round(275 * len(self.application.song_tabs)) - 1025, 
            color=(153, 217, 234), 
            alt_color=(0, 162, 232), 
            clicked_color=(0, 131, 187)
        )

    def render_static_elements(self) -> None:
        # Background
        background_image = self.application.images['menu_background_e']
        image_position = (round(640 - (background_image.get_size()[0] * .5)), round(360 - (background_image.get_size()[1] * .5)))
        self.application.screen.blit(background_image, image_position)
        self.application.screen.blit(self.application.overlay, (0, 0))

        # Title
        title = self.application.get_font(50).render('Song Select', True, (0, 0, 0))
        self.application.screen.blit(title, (490, 36))
    
    def render_dynamic_elements(self, **kwargs: tuple[int, int]) -> None:
        mouse_position = kwargs.get('mouse_position', None)
        if not mouse_position:
            raise ValueError('The "mouse_position" keyword argument is required but missing.')

        pygame.draw.rect(self.application.screen, self.application.BACKGROUND_COLOR, (0, 92, 1280, 400))

        for tab in self.application.song_tabs:
            if not self.application.scroll_bar:
                break
            tab.set_x(self.application.scroll_bar.get_notch_position())
            if -275 < tab.get_x() < 1280:
                tab.render()
                tab.button.is_hovered(mouse_position)

        pygame.draw.rect(self.application.screen, self.application.BACKGROUND_COLOR + (255,), (0, 115, 140, 365))
        pygame.draw.rect(self.application.screen, self.application.BACKGROUND_COLOR + (255,), (1140, 115, 1280, 365))

    def setup(self) -> None:
        self.application.clear_screen()
        self.render_static_elements() 
        self.add_buttons()
        self.create_song_tabs()
        self.add_scrollbar() 