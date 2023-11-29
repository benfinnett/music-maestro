from __future__ import annotations
from screen.screen import BaseScreen
from ui.button import Button
from user.user import User

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class Options(BaseScreen):
    def __init__(self, application: Application):
        super().__init__(application)

    def sign_out(self) -> None:
        self.application.user = User()
        self.setup()

    def delete_account(self) -> None:
        self.application.user.remove()
        self.sign_out()

    def add_buttons(self) -> None:
        '''
        Clears existing buttons and adds the options menu buttons to the screen_buttons list.
        '''
        self.application.screen_buttons = []
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Back', 
                position=(128, 648), 
                dimensions=(160, 75),
                on_click=lambda: self.application.set_screen('main_menu')
            )
        )
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Calibrate', 
                position=(300, 200), 
                dimensions=(200, 60),
                on_click=lambda: self.application.set_screen('calibrate')
            )
        )

        if self.application.user.logged_in:
            self.application.screen_buttons.append(
                Button(
                    self.application, 
                    text='Sign Out', 
                    position=(875, 200), 
                    dimensions=(180, 60),
                    on_click=self.sign_out,
                    text_size=20
                )
            )
            self.application.screen_buttons.append(
                Button(
                    self.application, 
                    text='Delete Account', 
                    position=(875, 275), 
                    dimensions=(250, 60),
                    on_click=self.delete_account,
                    text_size=26,
                    color=(250, 50, 50),
                    alt_color=(140, 25, 25),
                    hover_color=(190, 60, 60)
                )
            )
        else:
            self.application.screen_buttons.append(
                Button(
                    self.application, 
                    text='Log In', 
                    position=(875, 200), 
                    dimensions=(160, 75),
                    on_click=lambda: self.application.set_screen('login')
                )
            )

    def render_static_elements(self) -> None:
        # Background color and image
        background_image = self.application.images['menu_background_a']
        image_position = (round(640 - (background_image.get_size()[0] * .5)), round(360 - (background_image.get_size()[1] * .5)))
        self.application.screen.blit(background_image, image_position)
        self.application.screen.blit(self.application.overlay, (0, 0))

        # Title text
        options_text = self.application.get_font(50).render('Options', True, (0, 0, 0))
        self.application.screen.blit(options_text, (490, 36))

        calibrate_text = self.application.get_font(40).render('Calibrate Microphone', True, (0, 0, 0))
        self.application.screen.blit(calibrate_text, (100, 100))

        account_text = self.application.get_font(40).render('User Account', True, (0, 0, 0))
        self.application.screen.blit(account_text, (750, 100))

        # Logged in message
        username = self.application.user.get_username()
        if username:
            text = self.application.get_font(30).render(f'Logged in as: {username}', True, (0, 0, 0))
            self.application.screen.blit(text, (15, 675))

    def setup(self) -> None:
        self.application.clear_screen()
        self.render_static_elements() 
        self.add_buttons()