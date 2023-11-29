from __future__ import annotations
from string import ascii_letters, digits
from screen.screen import BaseScreen
from ui.button import Button

from typing import TYPE_CHECKING

from ui.text_input import TextInput
if TYPE_CHECKING:
    from application import Application

class Login(BaseScreen):
    def __init__(self, application: Application):
        super().__init__(application)
        self.user_input_error = None

    def login(self) -> None:
        self.user_input_error = self.application.user.validate(
            self.username_field.get_value(), 
            self.password_field.get_value()
        )
        if not self.user_input_error:
            self.application.set_screen('options')
        else:
            self.render_static_elements()

    def create_account(self) -> None:
        self.user_input_error = self.application.user.create(
            self.username_field.get_value(), 
            self.password_field.get_value()
        )
        if not self.user_input_error:
            self.application.set_screen('options')
        else:
            self.render_static_elements()

    def add_buttons(self) -> None:
        self.application.screen_buttons = []
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Log In', 
                position=(640, 450), 
                dimensions=(160, 75),
                on_click=self.login
            )
        )
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Create Account', 
                position=(640, 540), 
                dimensions=(320, 75),
                on_click=self.create_account,
                text_size=35
            )
        )
        self.application.screen_buttons.append(
            Button(
                self.application, 
                text='Back', 
                position=(128, 648), 
                dimensions=(160, 75),
                on_click=lambda: self.application.set_screen('options')
            )
        )

    def add_text_inputs(self) -> None:
        self.application.text_inputs = []

        self.username_field = TextInput(
            self.application, 
            dimensions=(575, 55), 
            position=(340, 175), 
            character_limit=16, 
            allowed_characters=ascii_letters + digits + '_'
        )
        self.password_field = TextInput(
            self.application, 
            dimensions=(575, 50), 
            position=(340, 285), 
            character_limit=30, 
            allowed_characters=ascii_letters + digits + ' ', 
            input_hidden=True
        )

        self.application.text_inputs.append(self.username_field)
        self.application.text_inputs.append(self.password_field)

    def render_static_elements(self) -> None:
        # Background color and image
        background_image = self.application.images['menu_background_c']
        image_position = (round(640 - (background_image.get_size()[0] * .5)), round(360 - (background_image.get_size()[1] * .5)))
        self.application.screen.blit(background_image, image_position)
        self.application.screen.blit(self.application.overlay, (0, 0))

        # Title text
        title = self.application.get_font(50).render('Log In', True, (0, 0, 0))
        self.application.screen.blit(title, (565, 36))

        username_text = self.application.get_font(40).render('Username', True, (0, 0, 0))
        self.application.screen.blit(username_text, (340, 125))
        
        username_text = self.application.get_font(40).render('Password', True, (0, 0, 0))
        self.application.screen.blit(username_text, (340, 235))

        if self.user_input_error:
            error_text = self.application.get_font(30).render(self.user_input_error, True, (0, 0, 0))
            self.application.screen.blit(error_text, (340, 350))        

    def setup(self) -> None:
        self.application.clear_screen()
        self.render_static_elements() 
        self.add_buttons()
        self.add_text_inputs()