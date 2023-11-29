from __future__ import annotations
from typing import Callable
import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class Button:
    '''
    A user interface element that when clicked triggers some action.
    '''
    def __init__(self,
                 application: Application, 
                 text: str, 
                 position: tuple[int, int], 
                 dimensions: tuple[int, int], 
                 on_click: Callable,
                 text_size: int = 22, 
                 color: tuple[int, int, int] | None = None, 
                 alt_color: tuple[int, int, int] | None = None, 
                 hover_color: tuple[int, int, int] | None = None, 
                 text_color: tuple[int, int, int] | None = None) -> None:
        '''
        Create a Button instance.
        
        Args:
            application: Context of the Application instance required for rendering the button
            text (str): Text to be displayed on the button
            position (tuple): Two values stating coordinates of the button
            dimensions (tuple): A tuple or list of two values indicating the width and height the rectangular button should be
            on_click (Callable): Function to be called when the button is clicked.
            text_size (int): Text height in pixels. Default = 22.
            color (tuple): The color of the center of the button. Default = (153, 217, 234).
            alt_color (tuple): The color of the button border. Default = (0, 162, 232).
            hover_color (tuple): The color of the center of the button upon mouse hover. Default = (113, 203, 225).
            text_color (tuple): The color of the button text. Default = (255, 255, 255).
        '''
        self.application = application
        self.text = text
        self.text_size = text_size
        self.position = position
        self.dimensions = dimensions
        self.function = on_click
        self.colors = {
            'primary': color if color else (153, 217, 234),
            'alt': alt_color if alt_color else (0, 162, 232),
            'hover': hover_color if hover_color else (113, 203, 225),
            'text': text_color if text_color else (255, 255, 255)
        }

        # Button coords based off the center of the button using
        # (desired_x - button_width * 0.5, desired_y - button_height * 0.5)
        button_position = (round(position[0] - (dimensions[0] * 0.5)), round(position[1] - (dimensions[1] * 0.5)))
        self.rect = pygame.Rect(button_position, (dimensions[0], dimensions[1]))
        self.render(self.colors['primary'])

    def call(self):
        self.function()

    def render(self, color: tuple[int, int, int]) -> None:
        '''
        Draw the button onto the display.
        
        Args:
            color (tuple) : the color of the center of the button 
        '''
        # Draw the button frame
        frame_pixel_size = 10
        pygame.draw.rect(self.application.screen, self.colors['alt'], self.rect)

        # Draw the button
        pygame.draw.rect(
            self.application.screen, 
            color, 
            pygame.Rect(
                (self.rect.x + (frame_pixel_size // 2),self.rect.y + (frame_pixel_size // 2)),
                (self.rect.width - frame_pixel_size, self.rect.height - frame_pixel_size)
            )
        )

        # Render text in the middle of the button
        font = self.application.get_font(int(self.dimensions[1] - self.text_size))
        label = font.render(self.text, True, self.colors['text'])
        text_position = (self.position[0] - self.dimensions[0] * .45, self.position[1] - self.dimensions[1] * .45)
        self.application.screen.blit(label, text_position)

    def is_hovered(self, mouse_position: tuple[int, int]) -> bool:
        '''
        Test whether the button is being hovered over and rerender the button.
        
        Args:
            mouse_position (tuple): The coordinates of the mouse cursor.

        Returns:
            bool: Whether the button is being hovered over.
        '''
        is_hovered = self.rect.collidepoint(mouse_position)
        if is_hovered:
            self.render(self.colors['hover'])
        else:
            self.render(self.colors['primary'])

        return is_hovered

    def set_position(self, position: tuple[int, int]) -> None:
        '''
        Set the position of a button.

        Args:
            position (tuple): The coordinates of the button.
        '''
        self.position = position
        self.rect = pygame.Rect(
            (round(position[0] - (self.dimensions[0] * .5)), round(position[1] - (self.dimensions[1] * .5))),
            (self.dimensions[0], self.dimensions[1])
        )