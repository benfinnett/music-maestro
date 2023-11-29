from __future__ import annotations
import numpy as np
import pygame
from screen.screen import BaseScreen

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class Calibrate(BaseScreen):
    def __init__(self, application: Application):
        super().__init__(application)
        self.current_note = None

    def run_calibration(self) -> None:
        for self.current_note in self.application.notes:
            tick = 0
            buffering = True
            buffer = {}
            while buffering:
                self.render_static_elements()

                self.application.clock.tick(60)
                tick += 1

                if tick < 40:
                    self.application.audio.stream()
                    current_frequencies = self.application.audio.get_dominant_frequencies()
                    self.render_dynamic_elements(current_frequencies=current_frequencies)

                    # Creates a dictionary of how many times each dominant frequency appears in the timeframe
                    for frequency in current_frequencies:
                        if frequency > 1:
                            buffer[int(frequency)] = buffer.get(int(frequency), 0) + 1
                else:
                    buffering = False
                    # Extract top 3 most frequent frequencies
                    sorted_buffer = dict(sorted(buffer.items(), key=lambda item: item[1], reverse=True)) # {667.0: 9, 668.0: 7, 665.0: 7, 671.0: 7, 654.0: 6, 673.0: 5, ...}
                    top_3_occurances = list(sorted(set(sorted_buffer.values()), reverse=True))[:3] # [9, 7, 6]

                    self.application.notes[self.current_note] = [
                        frequency for frequency, occurences in sorted_buffer.items() if occurences in top_3_occurances
                    ]
                    
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.application.quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.application.reset_notes()
                            self.application.set_screen('options')
                            return
                
                pygame.display.flip()
        
        self.application.set_screen('options')

    def render_static_elements(self) -> None:
        # Background color and image
        self.application.screen.fill(self.application.BACKGROUND_COLOR)
        background_image = self.application.images['menu_background_b']
        image_position = (round(640 - (background_image.get_size()[0] * .5)), round(360 - (background_image.get_size()[1] * .5)))
        self.application.screen.blit(background_image, image_position)
        self.application.screen.blit(self.application.overlay, (0, 0))

        # Title
        title_text = self.application.get_font(40).render('Please play the following note once:', True, (0, 0, 0))
        self.application.screen.blit(title_text, (490, 36))

        # Esc to cancel
        escape_text = self.application.get_font(20).render('Press Esc to cancel', True, (0, 0, 0))
        self.application.screen.blit(escape_text, (500, 100))
    
    def render_dynamic_elements(self, **kwargs: np.ndarray) -> None:
        note_text = self.application.get_font(400).render(self.current_note, True, (0, 0, 0))
        self.application.screen.blit(note_text, (0, 25))

        current_frequencies = kwargs.get('current_frequencies', None)
        if current_frequencies is not None:
            average_frequency = round(sum(current_frequencies) / len(current_frequencies))
            current_mic_note = self.application.audio.get_note_from_frequency(self.application.notes, current_frequencies)
            note = self.application.get_font(30).render(f'Frequency: {average_frequency:03d}Hz (closest standard note {current_mic_note})', True, (0, 0, 0))
            self.application.screen.blit(note, (10, 675))
    
    def setup(self) -> None:
        self.run_calibration()