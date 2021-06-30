from __future__ import annotations
import random, os, json
from datetime import datetime
from typing import List, Tuple, NoReturn
from mido import Message, MidiFile, MidiTrack, MetaMessage
from mido.midifiles.units import bpm2tempo, tempo2bpm
from pyo import *
from ga import *

SCALE_DEGREES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  #melody can take 2 octaves of notes, note 15 is rest note
NOTE_VALUES = [2, 1, 0.5, 0.25] #melody can take 4 different note durations
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]
TIME_SIGNS = ['4/4', '3/4', '2/4', '6/8']
NUM_OF_STEPS = ['1', '2', '3']
        
class Melody:
    def __init__(self, note_degrees: List[int], durations: List[float], key: str, scale: str, octave: str,
                 time_sign: Tuple[int, int], bpm: int, num_steps: int, pitches: List[int] = None, velocities: List[int] = None):
        self.note_degrees = note_degrees
        self.durations = durations

        self.key = key
        self.scale = scale
        self.octave = octave
        self.time_sign = time_sign
        self.bpm = bpm
        self.num_steps = num_steps

        self.pitches = pitches
        self.velocities = velocities

        self.events = []
        #create midi events from each melody line
        for notes in self.pitches:
            self.events.append(
                Events(
                midinote=EventSeq(notes, occurrences=1),
                beat=EventSeq(self.durations, occurrences=1),
                midivel=EventSeq(self.velocities, occurrences=1),
                attack=0.001,
                decay=0.05,
                sustain=0.4,
                release=0.005,
                bpm=bpm)
                )

    @property
    def note_degrees(self):
        return self._note_degrees
    
    @property
    def durations(self):
        return self._durations

    @property
    def pitches(self):
        return self._pitches

    @property
    def velocities(self):
        return self._velocities
    
    @note_degrees.setter
    def note_degrees(self, degrees: List[int]):
        if any(degree < 0 or degree > 15 for degree in degrees):
            raise ValueError('Note degree out of range (0-15)')
        self._note_degrees = degrees
    
    @durations.setter
    def durations(self, durs: List[float]):
        if any(dur not in NOTE_VALUES for dur in durs):
            raise ValueError('Note durations invalid')
        self._durations = durs
    
    @pitches.setter
    def pitches(self, pitches: List[int]):
        if pitches is None:
            scl = EventScale(root=self.key, scale=self.scale, first=self.octave)

            pitches = []
            degrees = [degree%7 for degree in self.note_degrees]
            for step in range(self.num_steps):
                pitches.append([scl[(degree + step*2) % (len(scl)-1)] for degree in degrees])
        else:
            for pitch in pitches:
                try:
                    if any(note < 0 or note > 127 for note in pitch):
                        raise ValueError('Pitch out of range (0-127)')
                except IndexError:
                    raise IndexError('No pitch layers found')

        self._pitches = pitches
    
    @velocities.setter
    def velocities(self, vels: List[int]):
        if vels is None:
            vels = [0 if degree == 15 else 100 for degree in self.note_degrees]
        elif any(vel < 0 or vel > 127 for vel in vels):
            raise ValueError('Velocity out of range (0-127)')
        self._velocities = vels

    def start_playing(self, s: Server) -> NoReturn:
        for e in self.events:
            e.play()
        s.start()

    def stop_playing(self) -> NoReturn:
        for e in self.events:
            e.stop()

    def set_rating(self, value: int) -> NoReturn:
        self.rating = value

    @staticmethod
    def get_fitness(music):
        return music.rating

class Music:
    def __init__(self, key: str, scale: str, octave: str, time_sign: Tuple[int, int], bpm: int, 
                 num_steps: int, generation: int, num_mutations: int, mutation_probability: float, population: List[Melody] = []) -> NoReturn:
        self.key = key
        self.scale = scale
        self.octave = octave
        self.time_sign = time_sign
        self.bpm = bpm
        self.num_steps = num_steps
        self.generation = generation
        self.num_mutations = num_mutations
        self.mutation_probability = mutation_probability
        self.population = population
    
    def add_melody(self, note_degrees: List[int], durations: List[float], pitches: List[int] = None, velocities: List[int] = None) -> NoReturn:
        melody = Melody(note_degrees, durations, self.key, self.scale, self.octave, self.time_sign, self.bpm, self.num_steps, pitches, velocities)
        self.population.append(melody)
    
    def save_to_midi(self, folder: str, first_time_saving: bool) -> NoReturn:
          
        for i, melody in enumerate(self.population):
            midi = MidiFile()

            TICKS = midi.ticks_per_beat

            meta = MidiTrack()
            midi.tracks.append(meta)
            meta.append(MetaMessage('time_signature', numerator=self.time_sign[0], denominator=self.time_sign[1]))
            meta.append(MetaMessage('key_signature', key=self.key))
            meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(self.bpm)))

            track = MidiTrack()
            midi.tracks.append(track)
            for j, notes in enumerate(zip(*melody.pitches)):
                #set notes on
                for note in notes:
                    track.append(Message('note_on', note=note, velocity=melody.velocities[j], time=0))
                
                #set notes off
                for k, note in enumerate(notes):
                    if k == 0:
                        track.append(Message('note_off', note=note, velocity=melody.velocities[j], time=int(melody.durations[j]*TICKS)))
                    track.append(Message('note_off', note=note, velocity=melody.velocities[j], time=0))

            if first_time_saving:
                metadata = {'scale': self.scale, 'num_steps': self.num_steps, 'generation': self.generation, 'num_mutations': self.num_mutations, 'mutation_probability': self.mutation_probability}
                with open(f'{folder}/meta.json', 'w') as f:
                     json.dump(metadata, f, indent=4)
                os.makedirs(f'{folder}/{self.generation}', exist_ok=True)
                midi.save(filename=f'{folder}/{self.generation}/{self.key}-{self.scale}-{i}.mid')
            else:
                parent_dir = os.path.dirname(folder)
                os.makedirs(f'{parent_dir}/{self.generation}', exist_ok=True)
                midi.save(filename=f'{parent_dir}/{self.generation}/{self.key}-{self.scale}-{i}.mid')

    @classmethod
    def generate_from_folder(cls, folder: str) -> Melody: 
        
        rootfolder = os.listdir(os.path.dirname(folder))
        for filename in rootfolder:
            if filename.endswith('.json'):
                data_json = filename
                break
        
        with open(f'{os.path.dirname(folder)}/{data_json}') as f:
            data = json.load(f)

        scale = data['scale']
        num_steps = data['num_steps']
        generation = data['generation']
        num_mutations = data['num_mutations']
        mutation_probability = data['mutation_probability']
        
        midifilenames = os.listdir(folder)
        key = bpm = octave = time_sign = None
        #iterate the whole population of midis
        for i, filename in enumerate(midifilenames):
            midi = MidiFile(f'{folder}/{filename}')
            #retrieve the melody and rhythm from each track (we only use 1 track for this application)
            for track in midi.tracks:
                melody = []
                rhythm = []
                velocity = []
                
                note_on = False # a flag to determine the lowest pitch of each chord if there's a chord (the lowest pitch is the first note of each note_on)
                for msg in track:
                    if msg.is_meta:
                        if msg.type == 'time_signature':
                            time_sign = (msg.numerator, msg.denominator)
                        elif msg.type == 'key_signature':
                            key = msg.key.replace('m', '')
                        elif msg.type == 'set_tempo':
                            bpm = tempo2bpm(msg.tempo)
                    else:
                        if msg.type == 'note_on':
                            if not note_on:
                                note_on = True
                                melody.append(msg.note)
                                velocity.append(msg.velocity)
                            else:
                                continue
                        else:
                            if note_on:
                                note_on = False
                                dur = msg.time/midi.ticks_per_beat
                                rhythm.append(dur)
            
            if i == 0:
                octave = min(melody)//12 
                music_population = cls(key, scale, octave, time_sign, bpm, num_steps, generation, num_mutations, mutation_probability)
            
            scl = EventScale(root=key, scale=scale, first=octave)
            note_degree = []
            for pitch, vel in zip(melody, velocity):
                if vel == 0:
                    note_degree.append(15)
                else:
                    degree = scl.data.index(pitch)
                    note_degree.append(degree)

            music_population.add_melody(note_degree, rhythm)
        return music_population

def generate_music(max_beats: int):
    full_melody = []
    full_rhythm = []
    full_duration = 0.0

    #generate note values until it occupies all the bars
    while full_duration < max_beats:
        weights = [0.05, 0.5, 0.4, 0.05]
        while True:
            duration = generate_genomes(NOTE_VALUES, 1, weights)[0]
            if full_duration + duration > max_beats:
                continue
            full_duration += duration
            break            

        while True:
            melody = generate_genomes(SCALE_DEGREES, 1)[0]
            try:
                if melody == full_melody[-1] and random.random() > 0.2:
                    continue
            except IndexError:
                pass

            break

        full_melody += [melody]
        full_rhythm += [duration]

    full_melody = [0] + full_melody[1:] #make sure first note is root note

    return full_melody, full_rhythm