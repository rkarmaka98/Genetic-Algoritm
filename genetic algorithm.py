#########################################
###### Genetic Algo for solving knapsack #####
#########################################
from collections import namedtuple
from functools import partial
from typing import List, Optional, Callable, Tuple
from random import choices, randint, random, randrange

# list of 1s and 0s (included or not)
Genome = List[int]
Population = List[Genome]

# new implementation for diff problem
FitnessFunc = Callable[[Genome], int]
# takes nothings and outputs population
PopulateFunc = Callable[[], Population]
# takes in population and fitness then become parents of next generation sol
SelectionFunc= Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc= Callable[[Genome], Genome]

Thing = namedtuple('Thing', ['name','value', 'weight'])

things =[
    Thing('Laptop', 500, 2200),
    Thing('Headphone', 150, 160),
    Thing('Coffee mug', 60, 350),
    Thing('Notepad', 40, 333),
    Thing('Water Bottle', 30, 192)
]

# Genetic representation of solution
def generate_genome(length: int) -> Genome:
    # to generate genome create set of random 1s and 0s of lenth k 
    return choices([0,1], k=length)

# Function to generate new solution
def generate_population(size: int, genome_length: int) -> Population:
    # calling genome function multiple times until population is desired size
    return [generate_genome(genome_length) for _ in range(size)]

# Fitness function to evaluate solutions
def fitness(genome: Genome, things: [Thing], weight_limit: int) -> int:
    if len(genome) != len(things):
        raise ValueError("genome and things must be of same length")

    # initialize weight and value to zero
    weight=0
    value=0

    # check if genome at any index has a thing then accumulate weight and value 
    for i,thing in enumerate(things):
        if genome[i] ==1:
            weight += thing.weight
            value += thing.value

            # check if the current weight of the genome exceeds weight limit 
            if weight > weight_limit:
                return 0

    return value

# Select function to select the solution to generate new solution for next generation
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    # population with higher fitness is likely to be chosen
    return choices(
        population=population,
        weights= [fitness_func(genome) for genome in population],
        # k =2 means we need a pair
        k=2
    )

# Crossover function
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of same length")

    length=len(a)
    if length<2:
        return a,b

    # randomly choose index to cut the genome in half
    p = randint(1, length -1)
    return a[0:p] + b[p:], b[:p] + a[p:]

# Mutation Function
def mutation(genome: Genome, num: int =1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome

# Function which actually run the evolution
def run_evolution(
    populate_func: PopulateFunc,
    fitness_func: FitnessFunc,
    fitness_limit: int,
    selection_func: SelectionFunc = selection_pair,
    crossover_func: CrossoverFunc = single_point_crossover,
    mutation_func: MutationFunc = mutation,
    generation_limit: int = 100
) -> Tuple[Population, int]:
    # first generation
    population= populate_func()

    for i in range(generation_limit):
        # sort the population by fitness
        population = sorted(
            population,
            key = lambda genome: fitness_func(genome),
            reverse=True
        )

        if fitness_func(population[0]) >= fitness_limit:
            break

        # pick top 2 solutions as parent for next gen
        next_generation = population[0:2]

        for j in range(int(len(population) /2) -1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation
        
    population = sorted(
        population,
        key = lambda genome: fitness_func(genome),
        reverse=True
    )

    return population, i


population, generations = run_evolution(
    populate_func=partial(
        generate_population, size =10, genome_length=len(things)
    ),
    fitness_func=partial(
        fitness, things =things, weight_limit=3000
    ),
    fitness_limit=740,
    generation_limit=100
)

def genome_to_things(genome: Genome, things: [Thing]) -> [Thing]:
    result =[]
    # print(things)
    for i, thing in enumerate(things):
        if genome[i] ==1:
            result += [thing.name]
    
    return result

print("number of generations", generations)
print("best solution", genome_to_things(population[0],things))