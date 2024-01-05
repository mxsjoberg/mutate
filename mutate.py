import random
import math
import sympy as sp

from tabulate import tabulate

random.seed(42)

program = """
f: (x, y) -> -x * (y / 2 - 10); [10, 20] [-5, 7]
p: 10 4
"""

def print_as_table(population):
    table = tabulate(
        population,
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

def parse(program):
    for line in program.split("\n"):
        line = line.strip()
        if len(line) == 0:
            pass
        elif line[0] == "f":
            fdef, ffun = line.split("->")[0], line.split("->")[1]
            args = fdef.split(":")[1].strip()
            fexpr, frange = ffun.split(";")[0].strip(), ffun.split(";")[1].strip()

            symbols = sp.symbols(args[1:-1].split(","))
            expr = sp.sympify(fexpr)

            f = sp.lambdify(symbols, expr, 'numpy')
            # print(f(1, 2))

            ranges = []
            for range_ in frange.split("] ["):
                frange_cleaned = range_.replace("[", "").replace("]", "")
                ranges.append((int(frange_cleaned.split(",")[0]), int(frange_cleaned.split(",")[1])))
            # print(ranges)

            print(f"f: {expr}, s.t. {symbols} {ranges}\n")

        elif line[0] == "p":
            args = line.split(":")[1].strip()
            npop, mbits = int(args.split(" ")[0]), int(args.split(" ")[1])
            # print(npop, mbits)

            print(f"npop: {npop}, mbits: {mbits}\n")
            
            current_population = generate_population(f, npop, ranges[0], ranges[1], mbits)
            print_as_table(current_population)

if __name__ == "__main__":
    parse(program)

