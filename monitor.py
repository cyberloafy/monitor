from math import log2, trunc, pow, copysign
from contextlib import suppress
from time import sleep
from psutil import net_io_counters, virtual_memory, cpu_percent
from argparse import ArgumentParser

DEFAULT_RATE = 1000

SEPARATOR = " | "
TEMPLATE = "{} {}"
COLUMN_WIDTH = 12

ARROW_UP = '↑'
ARROW_DOWN = '↓'

justify = str.rjust


def init(f):
    return f()


@init
def sign():
    _signs = {
        -1: '▼',
        0: ' ',
        1: '▲'
    }

    def inner(i: int):
        return _signs[int(copysign(1, i))]

    return inner


@init
def format_size():
    _units = ("B ", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    _base = 1000
    _log2_base = log2(_base)

    def inner(value: int, precision: int = 1):
        if value <= 0:
            return '-- B '
        multiple = trunc(log2(value) / _log2_base)
        value /= pow(_base, multiple)
        suffix = _units[multiple]
        return f"{value:.{precision}f} {suffix}"

    return inner


@init
def format_number():
    _units = (' ', 'k', 'm', 'g', 't', 'p')
    _no_suffix = _units[0]
    _base = 1000

    def inner(value: int, precision: int = 2):
        if value < _base:
            return f'{value}{_no_suffix}'
        unit = sum(abs(value / pow(_base, i)) >= 1
                   for i in range(1, len(_units)))
        return f'{value / pow(_base, unit):.{precision}f}{_units[unit]}'

    return inner


def join(iterable, separator: str = SEPARATOR):
    return f'{separator}{separator.join(iterable)}{separator}'


COLUMNS = (
    {
        "title": f"{ARROW_UP} Packets",
        "width": 10,
        "delta-index": 2,
        "formatter": format_number
    },
    {
        "title": f"{ARROW_DOWN} Packets",
        "width": 10,
        "delta-index": 3,
        "formatter": format_number
    },
    {
        "title": f"{ARROW_UP} Bytes",
        "width": 9,
        "delta-index": 0,
        "formatter": format_size
    },
    {
        "title": f"{ARROW_DOWN} Bytes",
        "width": 9,
        "delta-index": 1,
        "formatter": format_size
    },
    {
        "title": "CPU",
        "width": 6,
        "formatter": lambda x: f'{x}%',
        "get": cpu_percent
    },
    {
        "title": "Memory",
        "width": 6,
        "formatter": lambda x: f'{x}%',
        "get": lambda: virtual_memory().percent
    }
)


def build_get(column):
    if get := column.get('get'):
        return lambda _: get()
    index = column['delta-index']
    return lambda delta: delta[index]


def complete_column(column: dict):
    extra_length = len(TEMPLATE.format('', sign(0)))
    width = max(column.get('width', 0), len(column['title'])) + extra_length
    # width = COLUMN_WIDTH
    formatter = column['formatter']
    column['width'] = width
    column['formatter'] = lambda x: justify(formatter(x), width - extra_length)


@init
def with_sign():
    _template = TEMPLATE

    def inner(value, last_value, formatter):
        return _template.format(formatter(value), sign(value - last_value))

    return inner


def monitor(gets: tuple, formatters: tuple, rate: float):
    with suppress(KeyboardInterrupt):
        last_counters = net_io_counters()
        last_values = tuple([0] * len(COLUMNS))

        while True:
            sleep(rate)

            counters = net_io_counters()
            delta = tuple((current - last)
                          for current, last
                          in zip(counters, last_counters))
            last_counters = counters

            values = tuple(get(delta) for get in gets)

            print(join(with_sign(v, last_values[i], formatters[i])
                       for i, v
                       in enumerate(values)),
                  end='\r')

            last_values = values


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-r', '--rate',
                        dest='rate', type=int,
                        default=DEFAULT_RATE,
                        help='refresh rate in milliseconds')
    return parser.parse_args()


def main():
    args = get_args()

    for c in COLUMNS:
        complete_column(c)

    header = '\n'.join((join(justify(c['title'], c['width']) for c in COLUMNS),
                        join('-' * c['width'] for c in COLUMNS)))
    width = len(header) // 2 - len(header) % 2
    logo = join((f'{x:^{width}}'
                 for x in ('...:..:.:::.:..:...',
                           '.:.: REAL-TIME RESOURCES MONITOR :.:.',
                           f'(Refresh rate is {args.rate}ms)')),
                '\n')
    print(logo)
    print(header)

    gets = tuple(map(build_get, COLUMNS))
    formatters = tuple(c['formatter'] for c in COLUMNS)
    monitor(gets, formatters, args.rate / 1000)

    print()


if __name__ == '__main__':
    main()
