import wave
import numpy as np
from scipy.io import wavfile
from pyaudio import PyAudio, paInt16

class AudioManager:
    def __init__(self, chunk: int = 1024, rate: int = 44_100):
        '''
        Initialize a SoundData object.

        Args:
            chunk (int): Number of samples grouped together
                         default: 1024
            rate (int): Nampling frequency in Hz
                        default: 44,100
        '''
        self.chunk = chunk
        self.rate  = rate
        self.buffer = None

        # Create an audio stream object from the microphone using PyAudio
        self.audio_stream = PyAudio().open(
            format=paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk
        )

    def _write_stream_to_file(self, filename: str, data: list):
        '''
        Write contents of data to a Wave file.

        Args:
            filename (str): Name of Wave file to be written to
            data (list): Mono audio signal
        '''
        wave_file = wave.open(f'./assets/{filename}.wav', 'wb')
        # Set details of the data being written
        wave_file.setnchannels(1)
        wave_file.setsampwidth(PyAudio().get_sample_size(paInt16))
        wave_file.setframerate(self.rate)
        # Convert the list into a binary string and overwrite the Wave file
        wave_file.writeframes(b''.join(data))
        wave_file.close()

    def _framing(self, data: np.ndarray) -> tuple[np.ndarray, int]:
        '''
        Transform audio signal into a series of overlapping frames.
        A frame (sample) is the amplitude at a point in time.

        Args:
            data (list): Mono audio signal

        Returns:
            frames (list): All the frames
            frame_length (int): Length of each frame
        '''
        # (window length) * (rate), with 0.025 secs being chosen arbitrarily
        frame_length = int(.025 * self.rate)

        # Used to convert from seconds to samples, with 0.01 secs between windows being chosen arbitrarily
        frame_step = int(.01  * self.rate)
        signal_length = len(data)

        # Ensure at least one frame
        number_of_frames = int(np.ceil(abs(signal_length - frame_length) / frame_step)) 

        # Find indices
        index_a = np.tile(np.arange(0, frame_length), (number_of_frames, 1))                               
        index_b = np.tile(np.arange(0, number_of_frames * frame_step, frame_step), (frame_length, 1))

        # Rearrange the array so rows become columns and colums become rows
        indices = index_a + index_b.T

        # Pad out the signal to ensure the frames have at least the same length as the indices array
        padding_amount = number_of_frames * frame_step + frame_length
        padding = np.zeros((padding_amount-signal_length))
        padded_buffer = np.append(data, padding)

        # Ensure data is int32 datatype
        frames = padded_buffer[indices.astype(np.int32, copy=False)]

        return frames, frame_length

    def _get_dominant_frequency(self, frame: np.ndarray):
        '''
        Find the dominant frequency of a single frame.

        Args:
            frame (ndarray): Amplitude information at a point in time
        
        Returns:
            float: Dominant frequency in Hz
        '''
        # Perform fast fourier transform on real input with nfft points to be calculated
        nfft = 2**14
        fourier_transform = np.fft.rfft(frame, nfft)

        magnitude_spectrum = (1 / nfft) * abs(fourier_transform)
        power_spectrum = (1 / (nfft * nfft)) * magnitude_spectrum * magnitude_spectrum

        # Gives the frequencies associated with the coefficients: .fftfreq(window_length,sampling_spacing) where sampling_spacing is the inverse of sampling rate
        frequencies = np.fft.fftfreq(len(power_spectrum), 1 / self.rate)

        # Filter out negative frequencies and return the floor division of 2 for each frequency. Finally, add 1 to each frequency
        frequencies = (frequencies[np.where(frequencies >= 0)] // 2) + 1 

        # Take only the first half of the spectra as only the first part contains useful data   
        power_spectrum = power_spectrum[:len(frequencies)]

        # Get maximum value
        maxiumum_index = np.argmax(power_spectrum)

        # Convert the dominant frequency to Hz
        return frequencies[maxiumum_index]
        
        
    def stream(self, time=.1):
        '''
        Update audio stream buffer.
        
        Args:
            time (float): Length of audio stream buffer in seconds
                          default: 0.1
        '''
        # To record (time) seconds into the buffer, we must take (rate)*(time) samples.
        # In each iteration (chunk) samples are taken, so we must loop (rate)*(time)/(chunk) times.
        buffer_hex = [self.audio_stream.read(self.chunk) for _ in range(int(self.rate / self.chunk * time))]
        self._write_stream_to_file('buffer', buffer_hex)
        self.rate, self.buffer = wavfile.read('./assets/buffer.wav')

    def get_dominant_frequencies(self) -> np.ndarray:
        '''
        Analyse the buffer data to find the dominant frequencies.

        Returns:
            dominant_frequencies (list) : list of the dominant frequencies identified

        Raises:
            ValueError: When `self.buffer` is not a Numpy array
        '''
        # Perform framing on the signal
        if not isinstance(self.buffer, np.ndarray):
            raise ValueError(f'{self.__class__.__name__}.buffer must be of type numpy.ndarray not {type(self.buffer)}')
        frames, frame_length = self._framing(self.buffer)
        # Perform Hamming window function on the frames
        # w(n) = .54 - .46*cos((2*(pi)*n)/(M-1)) , 0 <= n <= M-1 where M = number of points in the output window
        windows = frames * np.hamming(frame_length)

        # Find the dominant frequency for each frame
        dominant_frequencies = np.array([self._get_dominant_frequency(window) for window in windows])
        dominant_frequencies = np.round(dominant_frequencies, 3)
        dominant_frequencies = np.unique(dominant_frequencies)

        return dominant_frequencies

    def get_note_from_frequency(self, note_frequencies: dict, frequencies: np.ndarray):
        '''
        Convert a list of frequencies into their likeliest music note.
        
        Args:
            notes_dict (dict): Dictionary of notes and their associated frequencies
            frequencies (ndarray): Numpy array of frequencies
            
        Returns:
            note (str): Single note or None if no note identified   
        '''
        # If 1.0 is a dominant frequency assume it is background noise
        if 1.0 in frequencies:
            return 'rest'
        
        # Initialise closest_match
        closest_match = [None, float('inf')]

        for note, targets in note_frequencies.items():
            weight = 0
            for freq in frequencies:
                min_distance_from_target = min(
                    [abs(100 * round(np.sin((np.pi / np.log(2)) * np.log(freq / target_freq)), 4)) for target_freq in targets]
                )
                if not min_distance_from_target:
                    min_distance_from_target = -100
                weight += min_distance_from_target
                
            if weight < closest_match[1]:
                closest_match = [note, weight]
        
        return closest_match[0]