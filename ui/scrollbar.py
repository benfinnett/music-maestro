from __future__ import annotations
import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class ScrollBar:
    def __init__(self, 
                 application: Application, 
                 dimensions: tuple[int, int], 
                 position: tuple[int, int], 
                 scroll_length: int, 
                 color: tuple[int, int, int], 
                 alt_color: tuple[int, int, int], 
                 clicked_color: tuple[int, int, int], 
                 scroll_position: int = 0) -> None:
        '''
        Create a scroll bar instance.
        
        Args:
            application (Application): Context of the Application instance required for rendering.
            dimensions (tuple): Width and height of the scroll bar.
            position (tuple): X and Y coordinates of the scroll bar.
            scroll_length (int): The number of pixels to be scrolled.
            color (tuple): Slider track color.
            alt_color (tuple): Slider thumb color when not clicked.
            clicked_color (tuple): Slider thumb color when clicked.
            scroll_position (int): Initial position of the scroll notch. Defaults to 0.
        '''
        self.application = application
        self.dimensions = dimensions
        self.position = position
        # If the scrollable area is less than the width of the scroll bar track, 
        # set to the scroll bar track width (no scrolling needed)
        self.scroll_length = max(scroll_length, dimensions[0] + 1)# add 1 to avoid a division by 0 error
        self.scroll_position = scroll_position
        self.colors = {
            'primary': color,
            'alt': alt_color,
            'clicked': clicked_color
        }
        self.scroll_bar_track = pygame.draw.rect(
            application.screen, 
            color, 
            pygame.Rect(
                (round(position[0] - (dimensions[0] * .5)), round(position[1] - (dimensions[1] * .5))),
                (dimensions[0], dimensions[1])
            )
        )
        # The size of the scroll notch is: (size of scroll bar) / ( (scrolling length) * (size of scroll bar) )
        self.scroll_bar_thumb = pygame.draw.rect(
            application.screen, 
            alt_color, 
            pygame.Rect(
                (self.scroll_bar_track.x + scroll_position, self.scroll_bar_track.y),
                (self.scroll_bar_track.width / (scroll_length + 1000) * self.scroll_bar_track.width, self.scroll_bar_track.height)
            )
        )
        self.was_scroll_bar_clicked = False
        if self.scroll_bar_track.width > self.scroll_bar_thumb.width:
            self.scroll_amount = scroll_length / (self.scroll_bar_track.width - self.scroll_bar_thumb.width)
        else:
            self.scroll_amount = 0

    def _handle_scroll_bar_drag(self, mouse_position: tuple[int, int], mouse_clicked: bool) -> None:
        if mouse_clicked:
            self._update_scroll_bar_position(mouse_position)
        else:
            self.render(self.colors['alt'])
            self.was_scroll_bar_clicked = False

    def _update_scroll_bar_position(self, mouse_position: tuple[int, int]) -> None:
        dx = mouse_position[0] - self.last_mouse_position[0]
        self.scroll_bar_thumb = self.scroll_bar_thumb.move(dx, 0)
        self.scroll_position -= self.scroll_amount * dx
        if self.scroll_bar_track.contains(self.scroll_bar_thumb):
            self.render(self.colors['clicked'])
        else:
            self.scroll_bar_thumb = self.scroll_bar_thumb.move(-dx, 0)
            self.scroll_position += self.scroll_amount * dx

    def render(self, thumb_color: tuple[int, int, int]) -> None:
        '''
        Draw the scroll bar and notch onto the display.
        
        Args:
            thumb_color (tuple): Color of the thumb
        '''
        pygame.draw.rect(self.application.screen, self.colors['primary'], self.scroll_bar_track)
        pygame.draw.rect(self.application.screen, thumb_color, self.scroll_bar_thumb)

    def check(self, mouse_position: tuple[int, int], mouse_clicked: bool) -> None:
        '''
        Check and handle mouse interaction with the scroll bar.

        Args:
            mouse_position (tuple): The current mouse position.
            mouse_clicked (bool): Whether the mouse is clicked.
        '''
        if self.was_scroll_bar_clicked:
            self._handle_scroll_bar_drag(mouse_position, mouse_clicked)
        elif mouse_clicked and self.scroll_bar_thumb.collidepoint(mouse_position):
            self.was_scroll_bar_clicked = True
        self.last_mouse_position = mouse_position
        
    def get_notch_position(self) -> int:
        return self.scroll_position