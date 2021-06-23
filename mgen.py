from __future__ import annotations
import click, random
from datetime import datetime
from typing import List, Tuple, NoReturn
from midiutil import MIDIFile
from pyo import *
from collections import namedtuple
from ga import *

SCALE_DEGREES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  #melody can take 2 octaves of notes, note 15 is rest note
NOTE_VALUES = [2, 1, 0.5, 0.25] #melody can take 4 different note durations
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]

class Music:
    def __init__(self, scale_degrees: List[int], durations: List[int], key: str, scale: str, octave: str,
                 time_sign: Tuple[int, int], bpm: int, num_steps: int, generation: int):
        self.scale_degrees = scale_degrees
        self.durations = durations
        self.pitches, self.velocities = self.info_from_degrees(scale_degrees, key, scale, octave, num_steps)

        self.scale = EventScale(root=key, scale=scale, first=octave)

        self.time_sign = time_sign
        self.bpm = bpm
        self.generation = generation

        self.events = []
        #create midi events from each melody line
        for notes in self.pitches:
            self.events.append(
                Events(
                midinote=EventSeq(notes, occurrences=1),
                beat=EventSeq(durations, occurrences=1),
                midivel=EventSeq(self.velocities, occurrences=1),
                attack=0.001,
                decay=0.05,
                sustain=0.4,
                release=0.005,
                bpm=bpm)
                )

    #save melody as midi
    def save_to_midi(self, filename: str) -> NoReturn:
        mf = MIDIFile(1)

        track = 0
        channel = 0

        time = 0.0
        mf.addTrackName(track, time, "Sample Track")
        mf.addTempo(track, time, self.bpm)
        mf.addTimeSignature(track, time, self.time_sign[0], int(math.log2(self.time_sign[1])), 24)

        for notes in self.pitches:
            time = 0
            for i, note in enumerate(notes):
                mf.addNote(track, channel, note, time, self.durations[i], self.velocities[i])
                time += self.durations[i]

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            mf.writeFile(f)

    @classmethod
    def generate_from_midi(cls, filename: str) -> Music:
        ...
    
    @staticmethod
    def info_from_degrees(scale_degrees: List[int], key: str, scale: str, octave: int, num_steps: int) -> Tuple[List[int], List[int]]:
        scl = EventScale(root=key, scale=scale, first=octave)

        pitches = []

        scale_degrees = [degree%7 for degree in scale_degrees]
        for step in range(num_steps):
            pitches.append([scl[(degree + step*2) % (len(scl)-1)] for degree in scale_degrees])
        
        vels = [0 if degree == 15 else 60 for degree in scale_degrees]
    
        return pitches, vels

    def rate_fitness(self, s: Server) -> int:
        for e in self.events:
            e.play()
        s.start()

        rating = input("rating (0-5)")

        for e in self.events:
            e.stop()
        s.stop()

        try:
            self.rating = int(rating)
        except ValueError:
            self.rating = 0

        return self.rating
    
    @staticmethod
    def get_fitness(music):
        return music.rating

def generate_music(time_sign: Tuple[int, int], max_beats: int, chaos: float):
    full_melody = []
    full_rhythm = []
    full_duration = 0.0

    #generate note values until it occupies all the bars
    while full_duration < max_beats:
        
        #takes different weights depending whether on beat or off beat and based on chaos value
        if full_duration.is_integer():
            if full_duration + 1 >= 4/time_sign[1] * time_sign[0]:
                half_note_weight = (1-chaos)/16
            else:
                half_note_weight = (1-chaos)/3
            weights = [half_note_weight, 1-chaos, (1-chaos)/4, chaos/4]

        elif str(full_duration).endswith(('25', '75')):
            if full_duration + 1 >= 4/time_sign[1] * time_sign[0]:
                half_note_weight = chaos/16
                quarter_note_weight = chaos/16 
                eighth_note_weight = chaos/16
            else:
                half_note_weight = chaos/8
                quarter_note_weight = chaos/4
                eighth_note_weight = chaos/2
            weights = [half_note_weight, quarter_note_weight, eighth_note_weight, 1-chaos]

        else:
            if full_duration + 1 >= 4/time_sign[1] * time_sign[0]:
                half_note_weight = chaos/16
                quarter_note_weight = chaos/16
            else:
                half_note_weight = chaos/4
                quarter_note_weight = chaos/2
            weights = [half_note_weight, quarter_note_weight, 1-chaos, (1-chaos)/2]
        
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

@click.command()
@click.option("--num-bars", default=8, prompt='Number of bars:', type=int)
@click.option("--time-sign-numerator", default=4, prompt='Time signature (numerator):', type=int)
@click.option("--time-sign-denominator", default=4, prompt='Time signature (denominator):', type=int)
@click.option("--num-steps", default=1, prompt='Number of notes stacked above (1 = single note, >2 = chords):', type=int)
@click.option("--key", default="C", prompt='Key:', type=click.Choice(KEYS, case_sensitive=False))
@click.option("--scale", default="major", prompt='Scale:', type=click.Choice(SCALES, case_sensitive=False))
@click.option("--bpm", default=120, prompt='BPM:', type=int)
@click.option("--chaos", default=0.2, prompt='Chaos value[0-1](higher value means more chaotic):', type=float)
@click.option("--octave", default=4, prompt='Start at which octave?:', type=int)
@click.option("--population-size", default=10, prompt='Population size:', type=int)
@click.option("--num-mutations", default=2, prompt='Number of mutations:', type=int)
@click.option("--mutation-probability", default=0.5, prompt='Mutations probability:', type=float)
def main(num_bars: int, time_sign_numerator: int, time_sign_denominator: int, num_steps: int, key: str, scale: str, chaos: float, octave: int,
         population_size: int, num_mutations: int, mutation_probability: float, bpm: int):

    
    folder = str(int(datetime.now().timestamp()))
    time_sign = (time_sign_numerator, time_sign_denominator)
    max_beats = num_bars * 4/time_sign[1] * time_sign[0]

    s = Server().boot()

    music_population = []

    population_id = 0

    for _ in range(population_size):
        melody, rhythm = generate_music(time_sign, max_beats, chaos)
        
        music = Music(melody, rhythm, key, scale, octave, time_sign, bpm, num_steps, population_id)

        music_population.append(music)

    while True:
        #rate and pool
        pool = []
        for music in music_population:
            rating = music.rate_fitness(s)
            #create pool with scale degrees and durations genomes
            pool.append([music.scale_degrees, music.durations, rating])
        
        print(f"population {population_id} done")
    
        print("saving population midi …")
        for i, music in enumerate(music_population):
            music.save_to_midi(f"{folder}/{population_id}/{scale}-{key}-{i}.mid")
        
        print("done")

        cont = input("continue [y/n]")
        if cont == 'n':
            break
        
        #elitism
        elitists = elitist_selection(pool, lambda x: x[2])
        next_gen = [[note, rhythm] for note, rhythm, _ in elitists]

        crossovers_remaining = (len(music_population) - len(elitists))//2
        for _ in range(crossovers_remaining):
            #single point crossover
            parents = selection_pair(pool, lambda x: x[2])
            note_parents, rhythm_parents, _ = zip(*parents)

            *note_children, p = single_point_crossover(*note_parents)
            *rhythm_children, _ = single_point_crossover(*rhythm_parents, cutpoint=p)

            #mutation
            note_children = [mutate_note(child, num_mutations, mutation_probability) for child in note_children]
            rhythm_children = [mutate_rhythm(child, num_mutations, mutation_probability) for child in rhythm_children]

            for notes, rhythms in list(zip(note_children, rhythm_children)):
                notes[0] = 0
                next_gen.append([notes, rhythms])
        
        population_id += 1
        new_population = []
        for notes, rhythms in next_gen:
            new_population.append(Music(notes, rhythms, key, scale, octave, time_sign, bpm, num_steps, population_id))

        music_population = new_population
    
if __name__ == '__main__':
    main()
