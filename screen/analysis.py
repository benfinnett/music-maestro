from __future__ import annotations
from math import ceil

import pygame
from screen.screen import BaseScreen
from ui.button import Button
from user.user import User

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class Analysis(BaseScreen):
    def __init__(self, application: Application):
        super().__init__(application)

    def update_user(self) -> None:
        if not self.application.user.logged_in:
            return
        
        self.user_data = self.application.user.get_data()

        highscore = int(self.user_data.get(self.song_name, 0))
        self.user_data[self.song_name] = max(self.accuracy, highscore)
        self.application.user.save(self.user_data)

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

    def render_static_elements(self) -> None:
        # Background color and image
        background_image = self.application.images['menu_background_d']
        image_position = (round(640 - (background_image.get_size()[0] * .5)), round(360 - (background_image.get_size()[1] * .5)))
        self.application.screen.blit(background_image, image_position)
        self.application.screen.blit(self.application.overlay, (0, 0))

        # Title text
        title = self.application.get_font(50).render('Song Performance', True, (0,0,0))
        song_name_text = self.application.get_font(40).render(f'Song name: {self.song_name}', True, (0,0,0))
        score_text = self.application.get_font(40).render(f'Score: {self.score}', True, (0,0,0))
        percent_text  = self.application.get_font(40).render(f'Accuracy: {self.accuracy}%', True, (0,0,0))
        self.application.screen.blit(title, (490,36))
        self.application.screen.blit(song_name_text, (25,86))
        self.application.screen.blit(score_text, (25,126))
        self.application.screen.blit(percent_text, (25,170))

        # Highscore text
        if self.application.user.logged_in:
            highscore_text = self.application.get_font(40).render(f'High score: {self.user_data[self.song_name]}%', True, (0, 0, 0))
            self.application.screen.blit(highscore_text, (25, 210))

        self.render_performance_graph()

    def render_performance_graph(self) -> None:
        if self.score <= 1:
            return
        
        # Draw graph Y and X axis
        pygame.draw.line(self.application.screen, (0, 0, 0), (640, 125), (640, 625), 4) # Y-axis
        pygame.draw.line(self.application.screen, (0, 0, 0), (640, 625), (1140, 625), 4) # X-axis

        # Create a translucent underlay under the graph area to obscure potentially distracting background image
        graph_underlay = pygame.Surface((498, 499))
        graph_underlay.set_alpha(200)
        graph_underlay.fill(self.application.BACKGROUND_COLOR)
        self.application.screen.blit(graph_underlay, (643, 125))

        # Convert x and y value to x and y on-screen coordinates
        # Ceiling of: (origin_y - offset) - ((length of axis / range of percents) * i)
        y = lambda k: int(ceil((625 - 10) - (((500 / (100 - min_percent)) * (k - min_percent)))))
        # Ceiling of: (origin_x) + ((total length of axis - text height / range of percents) * i)
        x = lambda k: int(ceil((640 - 5) + (((500 / (self.song_length - 1)) * k))))

        min_percent = int(min(self.accuracy_breakdown) * .1) * 10
        # Prevent axis from having only one value on it
        if min_percent == 100:
            min_percent = 90 

        # Calculate positions of and display graph y-axis label text
        for i in range(0, (100 - min_percent) + 10, 10): 
            text = self.application.get_font(20).render(f'{i + min_percent}%', True, (0, 0, 0))
            self.application.screen.blit(text, (590, y(i + min_percent))) 

        # Calculate positions of and display graph x-axis label text
        x_positions = []
        for i in range(self.song_length): 
            if i == 0 or self.song_length <= 20 or i == self.song_length - 1: 
                text = self.application.get_font(20).render(str(i + 1), True, (0, 0, 0))
                self.application.screen.blit(text, (x(i), 640))
            x_positions.append(x(i) + 6)

        # Label text for axes 
        y_label = self.application.get_font(30).render('Accuracy', True, (0, 0, 0))
        self.application.screen.blit(y_label, (450, 350))
        x_label = self.application.get_font(30).render('Note count', True, (0, 0, 0))
        self.application.screen.blit(x_label, (830, 660))

        # Plot points
        percents = [y(percent) + 10 for percent in self.accuracy_breakdown]   
        last_point = None
        for point in zip(x_positions, percents):
            if last_point:
                pygame.draw.aaline(self.application.screen, (0, 0, 0), point, last_point, 4)
            last_point = point
            pygame.draw.circle(self.application.screen, (255, 0, 0), point, 4)            

    def load_performance_results(self) -> None:
        self.song_name: str = self.application.performance_results.get('song_name', 'Undefined')
        self.song_length: int = self.application.performance_results.get('song_length', 0)
        self.score: int = self.application.performance_results.get('score', 0)
        self.accuracy: int = self.application.performance_results.get('accuracy', 0)
        self.accuracy_breakdown: list[int] = self.application.performance_results.get('accuracy_breakdown', [])

    def setup(self) -> None:
        self.application.clear_screen()
        self.load_performance_results()
        self.update_user()
        self.render_static_elements() 
        self.add_buttons()