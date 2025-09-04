# agent_ga.py
from deap import base, creator, tools
import random
import numpy as np
from config import config_editor
import peremennue


class AgentGA:
    """Represents a single racing agent using a genetic algorithm to find its strategy."""

    def __init__(self, name, engine):
        self.name = name
        self.engine = engine
        self.final_position = None

        self.LENGTH_CHROM = config_editor["REQUIRED_PIT_STOPS"]
        self.POPULATION_SIZE = 50
        self.P_CROSSOVER = 0.9
        self.P_MUTATION = 0.2
        self.MAX_GENERATIONS = 50

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.toolbox = base.Toolbox()

        def generate_pit_stops():
            pit_stops = []
            last_pit_lap = 0
            for _ in range(self.LENGTH_CHROM):
                min_lap = last_pit_lap + config_editor["MIN_STINT_LENGTH"]
                max_lap = config_editor["TOTAL_LAPS"] - (self.LENGTH_CHROM - len(pit_stops) - 1) * config_editor[
                    "MIN_STINT_LENGTH"]
                if min_lap >= max_lap:
                    pit_stops.append(max_lap)
                else:
                    pit_stops.append(random.randint(min_lap, max_lap))
                last_pit_lap = pit_stops[-1]
            pit_stops.sort()
            return pit_stops

        self.toolbox.register("individualCreator", tools.initIterate, creator.Individual, generate_pit_stops)
        self.toolbox.register("populationCreator", tools.initRepeat, list, self.toolbox.individualCreator)
        self.toolbox.register("evaluate", self.evaluate_strategy)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("mate", tools.cxTwoPoint)

        def custom_mutate(individual, indpb):
            for i in range(len(individual)):
                if random.random() < indpb:
                    last_pit_lap = individual[i - 1] if i > 0 else 0
                    next_pit_lap = individual[i + 1] if i < len(individual) - 1 else config_editor["TOTAL_LAPS"]
                    min_lap = last_pit_lap + config_editor["MIN_STINT_LENGTH"]
                    max_lap = next_pit_lap - config_editor["MIN_STINT_LENGTH"]
                    if min_lap < max_lap:
                        individual[i] = random.randint(min_lap, max_lap)
            individual.sort()
            return individual,

        self.toolbox.register("mutate", custom_mutate, indpb=1.0 / self.LENGTH_CHROM)

    def evaluate_strategy(self, individual):
        return random.uniform(90 * config_editor["TOTAL_LAPS"], 110 * config_editor["TOTAL_LAPS"]),

    def find_best_strategy(self):
        population = self.toolbox.populationCreator(n=self.POPULATION_SIZE)

        for gen in range(self.MAX_GENERATIONS):
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.P_CROSSOVER:
                    self.toolbox.mate(child1, child2)
                    child1.sort()
                    child2.sort()
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.P_MUTATION:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            population[:] = offspring

        best_individual = tools.selBest(population, 1)[0]
        return best_individual