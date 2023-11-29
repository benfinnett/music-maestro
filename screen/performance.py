from __future__ import annotations
import threading

import pygame
from audio.song_parser import SongParser
from screen.screen import BaseScreen

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from application import Application

class Performance(BaseScreen):
    def __init__(self, application: Application):
        super().__init__(application)
        self.clock_speed = 60

    def _get_song_info_from_file(self) -> None:
        '''
        Set up song information from a given metadata list in the format:
            (song_name, song_difficulty, song_path)
        E.g.
            ('Ode to Joy', 'Easy', '.\\assets\\songs\\Ode to Joy - Easy.txt')
        
        Looks up file in .\\assets\\songs
        '''
        # Read the song file into a list
        with open(self.song[2], mode='r') as file:
            song_data = file.read().split('|') 

        # Strip all newlines and split into individual notes
        song_contents = [bar.strip('\n').split(',') for bar in song_data]
        
        self.song_parser = SongParser(song_contents, self.application.images)
        self.note_buffer = [self.song_parser.next_note()]
        
        # Identify song variables
        key = song_contents[-1][3].split('=')[1]
        # The key of C and Am have no special notation, so only load the key image if it is not C or Am
        if key not in ['C', 'Am']: 
            key = self.application.images[key + '_key_signature']

        self.song_information: dict[str, Any] = {
            'tempo': int(song_contents[-1][0].split('=')[1]),
            'cleff': self.application.images[song_contents[-1][1].split('=')[1] + '_cleff'],
            'time_signature': song_contents[-1][2].split('=')[1].split('/'),
            'key': key,
            'song_length': int(song_contents[-1][4].split('=')[1]),
            'metronome': 'left',
            'current_mic_note': 'X',
            'current_note': 'Y'
        }

        self.score = 0
        self.accuracy_breakdown = []

        self.ticks_per_beat = (60 * self.clock_speed) / self.song_information['tempo']
        self.scroll_speed = self.song_information['tempo'] / 20

    def _run_audio_stream(self) -> None:
        while True:
            self.application.audio.stream() 
            if self.performance_event != 'playing':
                break

    def fade_in(self) -> None:
        '''
        Perform a fade-in transition from the background to the current screen content.
        '''
        for i in range(200):
            self.render_static_elements()

            overlay = pygame.Surface(self.application.WINDOW_SIZE)
            overlay.set_alpha(round(255 - (255 / 200) * i))
            overlay.fill(self.application.BACKGROUND_COLOR)
            self.application.screen.blit(overlay, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.application.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.application.set_screen('song_select')
                        return
                
            pygame.display.flip()

    def handle_countdown(self) -> None:
        # Update the countdown each second when performance_event isn't set to 'playing'
        if self.tick % 60 != 0 or self.is_playing():
            return
        
        countdown_number = 4 - (self.tick // 60)
        self.performance_event = self.application.get_font(500).render(str(countdown_number), True, (0, 0, 0))
        if countdown_number == 0:
            self.tick = 1
            self.performance_event = 'playing'
            self.stream_thread.start()
    
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.application.quit()
            
            # Allow user to press Escape to stop playing and return to the main menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.is_playing():
                    self.performance_event = None
                    self.stream_thread.join()
                    self.application.set_screen('main_menu')

    def run_performance_loop(self) -> None:
        # Initialize a thread for running the audio stream in the background
        self.stream_thread = threading.Thread(target=self._run_audio_stream)

        while True:
            self.render_dynamic_elements()
            self.render_static_elements()
            
            self.application.clock.tick(self.clock_speed)
            self.tick += 1

            self.handle_countdown()

            # Handle song completion
            if self.note_buffer == [None]:
                self.performance_event = None
                self.stream_thread.join()

                self.application.performance_results = {
                    'song_name': self.application.song[0] if self.application.song else 'Undefined',
                    'song_length': self.song_information['song_length'],
                    'score': self.score,
                    'accuracy': round(100 * self.score / self.song_information['song_length']),
                    'accuracy_breakdown':  self.accuracy_breakdown
                }

                self.application.set_screen('analysis')
                return

            if self.is_playing():
                latest_note = self.note_buffer[-1]
                
                # Handle long duration notes
                if latest_note and self.tick % self.ticks_per_beat == 0:
                    latest_note['long_duration_bool'] += 1

                # Toggle metoronome position on the appropriate tick
                if (self.tick - self.song_information['metronome_offset']) % self.ticks_per_beat == 0:
                    self.song_information['metronome'] = 'right' if self.song_information['metronome'] == 'left' else 'left'

                # When the latest note's duration has passed 
                note_length_passed = latest_note and self.tick % round(self.ticks_per_beat * latest_note['note_length']) == 0
                if latest_note and note_length_passed:
                    if self.song_parser.end_of_bar:
                        # Add the barline to the note buffer when the end of the bar is reached
                        barline = {
                            'pos': 1280,
                            'note_length': latest_note['note_length'],
                            'note_name': 'barline',
                            'long_duration_bool': 0,
                            'played': 5,
                            'note_img_offset': 0,
                            'note_img': None,
                            'tilt': None
                        }
                        self.note_buffer.append(barline)
                        self.song_parser.end_of_bar = False
                    else:
                        # Otherwise get the next note
                        if latest_note['note_length'] > 1:
                            if latest_note['long_duration_bool'] == latest_note['note_length']:
                                self.note_buffer.append(self.song_parser.next_note())
                            else:
                                self.tick += self.ticks_per_beat
                        else:
                            self.note_buffer.append(self.song_parser.next_note())

                        if self.song_parser.end_of_bar and self.note_buffer[-1]:
                            # To make sure the note length isn't extended by the barline 
                            # (latest_note_length / 2) + barline_length = latest_note_length
                            self.note_buffer[-1]['note_length'] /= 2

                if self.tick > 10:
                    current_mic_frequencies = self.application.audio.get_dominant_frequencies()
                    self.song_information['current_mic_note'] = self.application.audio.get_note_from_frequency(self.application.notes, current_mic_frequencies)

                # Handle a successful microphone and current note match
                if self.song_information['current_note'] in self.song_information['current_mic_note'].split('/'):
                    for note in self.note_buffer:
                        if not note:
                            continue

                        note_name = note['note_name'][0] if note['note_name'][-1] == 'n' else note['note_name'][0] + note['note_name'][-1]

                        if note_name == self.song_information['current_note']:
                            note['played'] -= 1
                            break
                
                # Handle note interaction 
                for i, note in enumerate(self.note_buffer):
                    if note:
                        note['pos'] -= self.scroll_speed                  
                        if self.hitbox_rect.left < note['pos'] < self.hitbox_rect.right:
                            if note['note_name'][-1] == 'n':
                                self.song_information['current_note'] = note['note_name'][0]
                            else:
                                self.song_information['current_note'] = note['note_name'][0] + note['note_name'][-1]
                        elif note['pos'] < self.hitbox_rect.left - 40:
                            note['played'] = 1099511627776 # 2 ** 40
                        
                        # User has played the correct note at the correct time
                        if note['played'] <= 0:
                            note['pos'] = -40
                            self.song_information['current_note'] = 'X'
                            self.score += 1    

                        # Delete the note when it's x-position is off screen
                        if note['pos'] <= -60:
                            del self.note_buffer[i] 
                            if note['note_name'] != 'barline':
                                # Percent of notes played correctly out of all the notes so far
                                self.accuracy_breakdown.append(round(100 * self.score / (len(self.accuracy_breakdown) + 1)))
                        else:
                            self.note_buffer[i] = note
            
            self.handle_events()
            
            self.song_information['tick'] = self.tick
            pygame.display.flip()
    
    def render_static_elements(self) -> None:
        self.render_stave()
        self.render_fadeout_gradient()
        cleff_rect = self.application.screen.blit(self.song_information['cleff'], (0, 310)) # Render cleff
        key_signature_rect_right = self.render_key_signature(cleff_rect)
        beats_text_rect = self.render_time_signature(key_signature_rect_right)
        self.render_hitbox(beats_text_rect)
        self.render_performance_info_text()

    def render_dynamic_elements(self, **kwargs: Any) -> None:
        self.application.screen.fill(self.application.BACKGROUND_COLOR) 
        self.application.screen.blit(self.application.images['metronome_' + self.song_information['metronome']], (1000, 100))
        self.render_detected_note_text()
        self.render_notes_and_barlines()

        # Draw countdown text when needed
        if isinstance(self.performance_event, pygame.Surface):
            self.application.screen.blit(self.performance_event, (500, 10))

    def render_key_signature(self, previous_rect: pygame.Rect) -> int:
        # The key of C and Am do not have any special notation so return
        if self.song_information['key'] in ['C', 'Am']:
            return previous_rect.right - 50

        key_rect = self.application.screen.blit(self.song_information['key'], (previous_rect.right - 75, 300))
        return key_rect.right
    
    def render_time_signature(self, previous_rect: int) -> pygame.Rect:
        beats_text = self.application.get_font(80).render(self.song_information['time_signature'][0], True, (0, 0, 0))
        per_bar_text = self.application.get_font(80).render(self.song_information['time_signature'][1], True, (0, 0, 0))
        beats_text_rect = self.application.screen.blit(beats_text, (previous_rect, 350))
        self.application.screen.blit(per_bar_text, (previous_rect, 430))
        return beats_text_rect
    
    def render_hitbox(self, previous_rect: pygame.Rect) -> None:
        self.hitbox_rect = self.application.screen.blit(self.hitbox, (previous_rect.right + 25, 340))
        
        self.song_information['metronome_offset'] = round(
            ((self.application.screen.get_width() - self.hitbox_rect.left) / self.scroll_speed) / self.ticks_per_beat
        )

    def render_performance_info_text(self) -> None:
        title = self.application.get_font(30).render(f'Now playing - {self.song[0]}', True, (0, 0, 0)) 
        score_text = self.application.get_font(60).render('Score: ' + str(self.score), True, (0, 0, 0))
        self.application.screen.blit(title, (0, 0)) 
        self.application.screen.blit(score_text, (0, 40))
    
    def render_notes_and_barlines(self) -> None:
        for note in self.note_buffer:
            if not note:
                continue

            elif note['note_name'] == 'barline':
                pygame.draw.line(self.application.screen, (0, 0, 0), (note['pos'], 360), (note['pos'], 520), 4)
                continue

            image, y_offset = note['note_img']
            if note['tilt']:
                self.application.screen.blit(image, (note['pos'] - 25, y_offset))
            else:
                self.application.screen.blit(image, (note['pos'], y_offset))
                
            # Draw note ledger lines
            if y_offset + note['note_img_offset'] > 540:
                ledger_lines = ((y_offset + note['note_img_offset']) - 520) // 40
                for line in range(ledger_lines):
                    pygame.draw.line(
                        self.application.screen, 
                        (0, 0, 0), 
                        (note['pos'] - 10, 560 + (40 * line)), 
                        (note['pos'] + 60, 560 + (40 * line)), 
                        width=5
                    )
            elif 0 < y_offset < 340:
                ledger_lines = (360 - (y_offset + note['note_img_offset'])) // 40
                for line in range(ledger_lines):
                    pygame.draw.line(
                        self.application.screen, 
                        (0, 0, 0), 
                        (note['pos'] - 10, 320 - (40 * line)), 
                        (note['pos'] + 60, 320 - (40 * line)), 
                        width=5
                    )

    def render_detected_note_text(self) -> None:
        if not self.is_playing():
            return
        
        # Get the current microphone frequencies and detected note, and display it
        current_mic_note = self.song_information['current_mic_note']
        note = self.application.get_font(30).render(f'Detected note: {current_mic_note}', True, (0, 0, 0))
        self.application.screen.blit(note, (975, 675))

    def render_fadeout_gradient(self) -> None:
        # Draw note fadeout gradient 
        fadeout_steps = 50
        # 275 pixels is the distance between left of screen to left of hitbox
        fadeout_gradient = [pygame.Surface((int(275 / fadeout_steps), 720)) for _ in range(fadeout_steps)]
        for i, part in enumerate(fadeout_gradient):
            part.set_alpha(260 - int((255 / len(fadeout_gradient)) * (i + 1)))
            part.fill(self.application.BACKGROUND_COLOR)
            self.application.screen.blit(part, (part.get_rect().width * i, 0))

    def render_stave(self) -> None:
        for i in range(0, 200, 40): 
            pygame.draw.line(self.application.screen, (0, 0, 0), (0, 360 + i), (1280, 360 + i), 5)

    def setup(self) -> None:
        # Ensure Application.song is set
        if not self.application.song:
            raise ValueError('Application.song must be set before initialising Performance')
        self.song = self.application.song

        self.hitbox = pygame.Surface((50, 200)) 
        self.hitbox.set_alpha(200)
        self.hitbox.fill((153, 217, 234)) 

        self._get_song_info_from_file() 
        self.fade_in()
        
        self.performance_event = None
        self.tick = 1
        self.run_performance_loop()

    def is_playing(self):
        return self.performance_event == 'playing'