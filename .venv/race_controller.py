# race_controller.py

from deap import base, creator, tools
import random
import numpy as np
from config import config_editor

class RaceController:
    def __init__(self, model):
        self.model = model

        self.LENGTH_CHROM = self.model.REQUIRED_PIT_STOPS
        self.POPULATION_SIZE = 500
        self.P_CROSSOVER = 0.9
        self.P_MUTATION = 0.2
        self.MAX_GENERATIONS = 80
        self.HALL_OF_FAME_SIZE = 3

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.toolbox = base.Toolbox()

        def generate_pit_stops():
            pit_stops = []
            last_pit_lap = 0
            for _ in range(self.model.REQUIRED_PIT_STOPS):
                min_lap = last_pit_lap + self.model.MIN_STINT_LENGTH
                max_lap = self.model.TOTAL_LAPS - (self.model.REQUIRED_PIT_STOPS - len(pit_stops) - 1) * self.model.MIN_STINT_LENGTH
                if min_lap >= max_lap:
                    pit_stops.append(max_lap)
                else:
                    pit_stops.append(random.randint(min_lap, max_lap))
                last_pit_lap = pit_stops[-1]
            pit_stops.sort()
            return pit_stops

        self.toolbox.register("individualCreator", tools.initIterate, creator.Individual, generate_pit_stops)
        self.toolbox.register("populationCreator", tools.initRepeat, list, self.toolbox.individualCreator)
        self.toolbox.register("evaluate", self.model.evaluate_strategy)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("mate", tools.cxTwoPoint)

        def custom_mutate(individual, indpb):
            for i in range(len(individual)):
                if random.random() < indpb:
                    last_pit_lap = individual[i-1] if i > 0 else 0
                    min_lap = last_pit_lap + self.model.MIN_STINT_LENGTH
                    next_pit_lap = individual[i+1] if i < len(individual) - 1 else self.model.TOTAL_LAPS
                    max_lap = next_pit_lap - self.model.MIN_STINT_LENGTH
                    if min_lap < max_lap:
                        individual[i] = random.randint(min_lap, max_lap)
            individual.sort()
            return individual,

        self.toolbox.register("mutate", custom_mutate, indpb=1.0 / self.LENGTH_CHROM)

        self.stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        self.stats.register("min", np.min)
        self.stats.register("avg", np.mean)
        self.hof = tools.HallOfFame(self.HALL_OF_FAME_SIZE)

    def calculate_strategy_laps(self, strategy):
        strategy_laps = []
        last_lap = 0
        for pit_lap in strategy:
            strategy_laps.append(f"{pit_lap - last_lap} кругов")
            last_lap = pit_lap
        strategy_laps.append(f"{self.model.TOTAL_LAPS - last_lap} кругов")
        return strategy_laps

    def run_ga_with_elitism(self):
        population = self.toolbox.populationCreator(n=self.POPULATION_SIZE)

        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (self.stats.fields if self.stats else [])

        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if self.hof is not None:
            self.hof.update(population)

        record = self.stats.compile(population) if self.stats else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)
        print(logbook.stream)

        for gen in range(1, self.MAX_GENERATIONS + 1):
            offspring = self.toolbox.select(population, len(population) - self.HALL_OF_FAME_SIZE)
            offspring = [self.toolbox.clone(ind) for ind in offspring]

            for i in range(0, len(offspring) - 1, 2):
                if random.random() < self.P_CROSSOVER:
                    tools.cxTwoPoint(offspring[i], offspring[i + 1])
                    offspring[i].sort()
                    offspring[i + 1].sort()
                    del offspring[i].fitness.values
                    del offspring[i + 1].fitness.values

            for off in offspring:
                if random.random() < self.P_MUTATION:
                    self.toolbox.mutate(off)
                    if off.fitness.valid:
                        del off.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            if self.hof is not None:
                offspring.extend(self.hof.items)

            population[:] = offspring
            if self.hof is not None:
                self.hof.update(population)

            record = self.stats.compile(population) if self.stats else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            print(logbook.stream)

        return self.hof.items[0], logbook