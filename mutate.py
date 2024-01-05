import random
import math
import sympy as sp

from tabulate import tabulate

random.seed(42)

def print_as_table(population):
    table = tabulate(
        population[:10] if len(population) > 10 else population,
        headers=['n', 'encoding', 'decoded x, y', 'cost'],
        floatfmt=".3f",
        tablefmt="simple"
    )
    print(table, end="\n\n")

def encode(x, x_low, x_high, m):
    """Encode decimal number into binary

    x (int)                 : decimal number
    x_low (int)             : lower bound of x
    x_high (int)            : upper bound of x
    m (int)                 : number of bits
    """
    decimal = round((x - x_low) / ((x_high - x_low) / (2 ** m - 1)))
    binary = []
    while decimal >= 1:
        if decimal % 2 == 1:
            binary.append(1)
        else:
            binary.append(0)
        decimal = math.floor(decimal / 2)
    while len(binary) < 4:
        binary.append(0)

    return list(reversed(binary))

assert encode(9, -10, 14, 5) == [1, 1, 0, 0, 1]

def decode(B, x_low, x_high, m):
    """Decode binary into decimal number

    B (list)                : binary number
    x_low (int)             : lower bound of x
    x_high (int)            : upper bound of x
    m (int)                 : number of bits
    """

    return x_low + int((''.join(map(str, B))), 2) * ((x_high - x_low) / ((2 ** m) - 1))

assert int(decode([1, 1, 0, 0, 1], -10, 14, 5)) == 9

# TODO: generalize to n-range
def generate_population(f, n_pop, x_range, y_range, m_bits):
    """Generate initial population

    f (function)            : cost function
    n_pop (int)             : number of population
    x_range (list)          : range of x
    y_range (list)          : range of y
    m_bits (int)            : number of bits
    """
    pop_lst = []
    for i in range(n_pop):
        x = random.randint(x_range[0], x_range[1])
        y = random.randint(y_range[0], y_range[1])
        # encoded values
        x_encoded = encode(x, x_range[0], x_range[1], m_bits)
        y_encoded = encode(y, y_range[0], y_range[1], m_bits)
        # decoded values
        x_decoded = round(decode(x_encoded, x_range[0], x_range[1], m_bits), 2)
        y_decoded = round(decode(y_encoded, y_range[0], y_range[1], m_bits), 2)
        # determine initial cost
        cost = round(f(x_decoded, y_decoded), 2)
        # append to list
        pop_lst.append([i, x_encoded + y_encoded, [x_decoded, y_decoded], cost])
    
    # sort on cost
    pop_lst.sort(key = lambda x: x[3])
    # update index
    for i in range(len(pop_lst)): pop_lst[i][0] = i

    return pop_lst

# TODO: set random crossover points
def generate_offsprings(population, crossover):
    """Generate offsprings

    population (list)       : population
    crossover (list)        : crossover points
    """
    n = 0
    offsprings_lst = []

    while n < len(population):
        offsprings_lst.append(
            population[n][1][0:crossover[0]] +
            population[n + 1][1][crossover[0]:crossover[1]] +
            population[n][1][crossover[1]:]
        )
        offsprings_lst.append(
            population[n + 1][1][0:crossover[0]] +
            population[n][1][crossover[0]:crossover[1]] +
            population[n + 1][1][crossover[1]:]
        )
        # pair-wise
        n += 2

    return offsprings_lst

def mutate(offsprings, m_bits, mu=0.1):
    """Mutate offsprings

    offsprings (list)       : offsprings
    mu (float)              : mutation rate
    m_bits (int)            : number of bits
    """
    nbits = round(mu * (len(offsprings) * m_bits * 2))
    for i in range(nbits):
        offspring = random.randint(0, len(offsprings) - 1)
        bit = random.randint(0, m_bits * 2 - 1)
        # flip bits
        if offsprings[offspring][bit] == 1:
            offsprings[offspring][bit] = 0
        else:
            offsprings[offspring][bit] = 1

    return offsprings

def update_population(f, current_population, offsprings, keep, x_range, y_range, m_bits):
    """Update population

    f (function)                : cost function
    current_population (list)   : current population
    offsprings (list)           : offsprings
    keep (int)                  : number of population to keep
    x_range (list)              : range of x
    y_range (list)              : range of y
    m_bits (int)                : number of bits
    """
    offsprings_lst = []
    for i in range(len(offsprings)):
        # decoded values
        x_decoded = round(decode(offsprings[i][:4], x_range[0], x_range[1], m_bits), 2)
        y_decoded = round(decode(offsprings[i][4:], y_range[0], y_range[1], m_bits), 2)
        # determine initial cost
        cost = round(f(x_decoded, y_decoded), 2)
        # append to list
        offsprings_lst.append([i, offsprings[i], [x_decoded, y_decoded], cost])
    # sort on cost
    offsprings_lst.sort(key = lambda x: x[3])
    # update index
    for i in range(len(offsprings_lst)):
        offsprings_lst[i][0] = i
    # discard current population
    current_population[keep:] = offsprings_lst[:keep]
    # sort on cost
    current_population.sort(key = lambda x: x[3])
    # update index
    for i in range(len(current_population)):
        current_population[i][0] = i

    return current_population

### ---

def parse_function(line):
    fdef, fexpr = line.split("->")[0], line.split("->")[1]
    args = fdef.split(":")[1].strip()
    symbols = sp.symbols(args[1:-1].split(","))
    expr = sp.sympify(fexpr)

    fun = sp.lambdify(symbols, expr, 'numpy')
    # print(f(1, 2))

    print(f"function -> {expr}\n")

    return fun, symbols

def parse_ranges(line):
    args = line.split(":")[1].strip()
    ranges = []
    for range_ in args.split("] ["):
        frange_cleaned = range_.replace("[", "").replace("]", "")
        ranges.append((int(frange_cleaned.split(",")[0]), int(frange_cleaned.split(",")[1])))

    print(f"ranges -> {ranges}\n")

    return ranges

def parse_population(line):
    args = line.split(":")[1].strip()
    npop, mbits = int(args.split(" ")[0]), int(args.split(" ")[1])

    print(f"population : npop -> {npop}, mbits -> {mbits}\n")
    
    pop = generate_population(fun, npop, ranges[0], ranges[1], mbits)
    print_as_table(pop)

    return pop, npop, mbits

# f: (x, y) -> -x * (y / 2 - 10)
# r: [10, 20] [-5, 7]
# p: 10 4
# !mutate 10

if __name__ == "__main__":
    fun = None
    pop = None
    npop = None
    mbits = None
    offsprings = None
    solution = None
    # symbols = []
    # ranges = []
    
    # parse(program)
    while True:
        line = input("> ")
        
        line = line.strip()

        if line == "quit":
            break

        if line[0] == "f":
            fun, symbols = parse_function(line)

        if line[0] == "r":
            ranges = parse_ranges(line)

        if line[0] == "p":
            pop, npop, mbits = parse_population(line)

        if line.startswith("!mutate"):
            args = line.split(" ")
            if len(args) > 1:
                MAX_RUNS = int(line.split(" ")[1])
            else:
                MAX_RUNS = 100

            for i in range(MAX_RUNS):
                # generate offsprings
                offsprings = generate_offsprings(pop, [3, 6])
                # mutate
                offsprings = mutate(offsprings, mbits)
                # update population
                pop = update_population(
                    fun,
                    pop,
                    offsprings,
                    2,
                    ranges[0],
                    ranges[1],
                    mbits
                )

            solution = pop[0][2]

            print_as_table(pop)

            print(f"solution -> {solution}\n")


