import random
from typing import Any, List, Tuple, Callable

SCALE_DEGREES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  #melody can take 2 octaves of notes, note 15 is rest note
NOTE_VALUES = [2, 1, 0.5, 0.25] #melody can take 4 different note durations

Genome = List[Any]

def generate_genomes(options: Genome, length: int, weights: List[float] = None) -> Genome:
    return random.choices(options, k=length, weights=weights)

def elitist_selection(population: Genome, key: Callable[[Any], int]) -> List[Genome]:
    population = sorted(population, key=key, reverse=True)
    if len(population) % 2 == 0:
        num_elitists = 2
    else:
        num_elitists = 1
    return population[0:num_elitists]

def selection_pair(population: Genome, fitness_func: Callable[[Any], int]) -> List[Genome]:
    weighted_pop = []
    for genome in population:
        weighted_pop += [genome] * int(fitness_func(genome)+1)
    return random.sample(weighted_pop, k=2)

def single_point_crossover(x: Genome, y: Genome, cutpoint: int = None) -> Tuple[Genome, Genome, int]:
    if cutpoint is None:
        min_length = min(len(x), len(y))
        if min_length < 2:
            return x, y
        p = random.randrange(1, min_length)
    else:
        p = cutpoint
    return x[0:p] + y[p:], x[0:p] + y[p:], p

def mutate_note(genome: Genome, times: int, probability: float) -> Genome:
    for _ in range(times):
        index = random.randrange(len(genome))
        if random.random() < probability:
            genome[index] = (genome[index]+1) % (len(SCALE_DEGREES)-2)
    return genome

def mutate_rhythm(genome: Genome, times: int, probability: float) -> Genome:
    for _ in range(times):
        index = random.randrange(len(genome))
        if random.random() < probability:
            note_dur = NOTE_VALUES.index(genome[index])
            genome[index] = NOTE_VALUES[(note_dur+1) % len(NOTE_VALUES)]
    return genome