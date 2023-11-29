from __future__ import annotations
import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class TextInput:
    def __init__(
        self, 
        application: Application, 
        dimensions: tuple[int, int], 
        position: tuple[int, int], 
        character_limit: int, 
        allowed_characters: str, 
        color: tuple[int, int, int] = (153, 217, 234), 
        active_color: tuple[int, int, int] = (113, 203, 225), 
        input_hidden: bool = False
    ) -> None:
        '''
        Initialize a TextInput instance.

        Args:
            application (Application): Context for rendering the text input.
            dimensions (tuple): Width and height of the text input.
            position (tuple): X and Y position of the text input.
            character_limit (int): Maximum number of characters allowed.
            allowed_characters (list) List of allowed characters.
            color (tuple): Color when inactive.
            active_color (tuple): Color when active.
            input_hidden (bool): Whether the input should be hidden. Defaults to False.
        '''
        self.application = application
        self.dimensions = dimensions
        self.position = position
        self.character_limit = character_limit
        self.allowed_characters = allowed_characters
        self.colors = {'inactive': color, 'active': active_color}
        self.rect = pygame.Rect(position, dimensions)
        self.input_hidden = input_hidden
        self.is_active = False
        self.cursor = None
        self.value = []
        self.cursor_position = 0

    def render(self) -> None:
        '''
        Render the text input on the screen.
        '''
        color = self.colors['active'] if self.is_active else self.colors['inactive']
        pygame.draw.rect(self.application.screen, color, self.rect)
        font = self.application.get_font(self.dimensions[1])
        text_content = '•' * len(self.value) if self.input_hidden else ''.join(self.value)
        text = font.render(text_content, True, (0, 0, 0))
        self.application.screen.blit(text, (self.rect.left + (.01 * self.dimensions[0]), self.rect.top - (.1 * self.dimensions[1])))

    def check(self, mouse_position: tuple[int, int], mouse_clicked: bool) -> None:
        '''
        Check and handle mouse interactions with the text input.

        Args:
            mouse_position (tuple[int, int]): Current mouse position.
            mouse_clicked (bool): Whether the mouse is clicked.
        '''
        if self.rect.collidepoint(mouse_position):
            self.cursor = pygame.cursors.compile(pygame.cursors.textmarker_strings)
            pygame.mouse.set_cursor((8, 16), (0, 0), *self.cursor)
            if mouse_clicked:
                self.is_active = True
        else:
            if self.cursor:
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
                self.cursor = None
            if mouse_clicked:
                self.is_active = False
        self.render()        

    def key_press(self, key: str) -> None:
        '''
        Handle key press events for the text input.

        Args:
            key (str | int): The key pressed.
        '''
        if not self.is_active:
            return

        self._handle_character_input(key)

    def _handle_character_input(self, key: str) -> None:
        if key == '\x08':  # Backspace
            self._delete_character()
        elif len(self.value) < self.character_limit and key in self.allowed_characters:
            self._insert_character(key)

    def _delete_character(self) -> None:
        '''
        Delete a character at the cursor position.
        '''
        try:
            del self.value[self.cursor_position - 1]
            self.cursor_position -= 1
        except IndexError:
            pass

    def _insert_character(self, key: str) -> None:
        '''
        Insert a character at the cursor position.
        '''
        self.value.insert(self.cursor_position, key)
        self.cursor_position += 1

    def get_value(self) -> str:
        '''
        Return the current value of the text input.

        Returns:
            str: The current text value.
        '''
        return ''.join(self.value)
