from __future__ import annotations
from screen.screen import BaseScreen
from ui.button import Button

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class MainMenu(BaseScreen):
    def __init__(self, application: Application):
        super().__init__(application)   

    def add_buttons(self) -> None:
        '''
        Clears existing buttons and adds the main menu buttons to the screen_buttons list.
        '''
        self.application.screen_buttons = []
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Song Select', 
                position=(768, 288), 
                dimensions=(300, 75),
                on_click=lambda: self.application.set_screen('song_select')
            )
        )
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Options', 
                position=(768, 378), 
                dimensions=(300, 75),
                on_click=lambda: self.application.set_screen('options')
            )
        )

        username = self.application.user.get_username()
        if not username:
            self.application.screen_buttons.append(
                Button(
                    self.application, 
                    text='Log In', 
                    position=(698, 468), 
                    dimensions=(160, 75),
                    on_click=lambda: self.application.set_screen('login')
                )
            )            
        
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Quit', 
                position=(768, 468) if username else (856, 468), 
                dimensions=(300, 75) if username else (125, 75),
                on_click=self.application.quit
            )
        )

    def render_static_elements(self) -> None:
        # Background
        self.application.screen.blit(self.application.images['menu_background'], (0, 40))

        # Title
        title = self.application.get_font(70).render('Music Maestro', True, (0, 0, 0))
        self.application.screen.blit(title, (190, 135))

        # Logged in message
        username = self.application.user.get_username()
        if username:
            text = self.application.get_font(30).render(f'Logged in as: {username}', True, (0, 0, 0))
            self.application.screen.blit(text, (15, 675))

    def setup(self) -> None:
        self.application.clear_screen()
        self.render_static_elements() 
        self.add_buttons()