from typing import Any
import pygame

class SongParser:
    def __init__(self, song: list[list[str]], images: dict[str, pygame.Surface]):
        '''
        Class to handle the translation of song files into their components.

        Args:
            song   (list): The song file with all the song data
            images (dict): Contains all the image Surface objects and names the program uses
        '''
        self.images = images
        
        # Deep reverse the entire song, and remove the song metadata which is stored as the last element after reversing
        # E.g. ['tempo=100', 'cleff=treble', 'time_signature=4/4', 'key=C', 'notes=62']
        song.reverse()
        self.song = song[:-1]
        for i, bar in enumerate(self.song):
            bar.reverse()
            self.song[i] = bar
        
        # Dictionary of each note and its on-screen y-value 
        self.note_y_pos = {
            note : int(i * 20 + 60) for i, note in enumerate(
                [note + str(octave) for octave in range(7, 0, -1) for note in ['G', 'F', 'E', 'D', 'C', 'B', 'A']]
            )
        } 

        self.accidentals: dict[str, pygame.Surface | None] = {
            '#': images['sharp'],
            'b': images['flat'],
            'n': None
        }
        
        self.durations = {
            0.25: 'sixteenth_',
            0.5: 'eighth_',
            1.0: 'quarter_',
            2.0: 'half_',
            4.0: 'whole_'
        }
        
        self.current_bar = self.song.pop()

    def _parse(self, note: str) -> dict[str, Any]:
        '''
        Translate a string note/rest name and duration into a dictionary of data.

        Args:
            note (str): Contains information about note/rest name, duration and whether it is sharp or flat or not

        Returns:
            image (dict): All the data of the note, including loaded image files
        '''
        image = {
            'pos': 1280,
            'note_length': float(note[3:-1]),
            'note_name': note[:3],
            'long_duration_bool': 0, # Used to track if a note longer than 1 beat has been spawned for its note duration
            'played': 5, # Number of times microphone detected note must match before the note is successfully played 
            'note_img_offset': 0,
            'note_img': None,
            'tilt': None
        }

        # Lookup the image prefix in the self.durations dict
        note_accidental = note[-1] # Sharp (#), flat (b), natural (n), or rest (r)
        duration = self.durations[image['note_length']] 
        y_pos = self.note_y_pos[note[:2]] 
        tilt = self.accidentals[note[2]]
        
        if note_accidental == 'n':
            # Any note higher than B5 should have it's stem facing downwards
            if y_pos < self.note_y_pos['B5']:
                # Account for height of image file
                image['note_img_offset'] = 18 

                # Flip horizontally and vertically
                image['note_img'] = [
                    pygame.transform.flip(self.images[duration + 'note'], True, True), y_pos - image['note_img_offset']
                ]
            else:
                # Take 118 from y_pos to account for image height of notes
                image['note_img_offset'] = 118
                image['note_img'] = [self.images[duration + 'note'], y_pos - image['note_img_offset']]
        elif note_accidental == 'r':
            # The image should always be at y = 350 if it is a rest
            image['note_img'] = [self.images[duration + 'rest'], 350]

        if tilt:
            image['tilt'] = [tilt, y_pos - 115]
        
        return image
        
    def next_note(self) -> dict[str, Any] | None:
        '''
        Get the next note in the song as a dictionary of data.

        Returns:
            self.note (dict): All the data of the note, including loaded image files
            None: Special condition returned when self.song is empty
        '''
        self.end_of_bar = len(self.current_bar) == 1
        if not self.current_bar:
            if self.song:
                self.current_bar = self.song.pop()
                self.end_of_bar = len(self.current_bar) == 1
            else:
                return
            
        # Parse the next note in the song
        return self._parse(self.current_bar.pop())
