from math import log2, trunc, pow, copysign
from contextlib import suppress
from time import sleep
from typing import Union
from psutil import net_io_counters, virtual_memory, cpu_percent
from argparse import ArgumentParser
import re
import requests
import os

VERSION = '1.1.0'
REPO_URL = 'https://raw.githubusercontent.com/cyberloafy/monitor/main/monitor.py'


class FancyString:
    _prefix = '#'
    _styles = {
        'r': '\033[0m',  # reset
        '0': '\033[0m',  # reset
        'b': '\033[1m',  # bold
        '1': '\033[1m',  # bold
        'd': '\033[91m',  # red
        '2': '\033[91m',  # red
        'y': '\033[33m',  # yellow
        '3': '\033[33m',  # yellow
        'g': '\033[92m',  # green
        '4': '\033[92m',  # green
        'c': '\033[36m',  # cyan
        '5': '\033[36m',  # cyan
        'l': '\033[94m',  # blue
        '6': '\033[94m',  # blue
        'p': '\033[95m',  # purple
        '7': '\033[95m',  # purple
        _prefix: _prefix
    }
    _pattern = re.compile(f'{_prefix}([{"".join(_styles.keys())}])')
    _reset = f'{_prefix}0'
    _styles_enabled = True

    def __init__(self, s: str, styles_enabled: bool = False):
        self._s = s + self._reset * (not s.endswith(self._reset))
        self._length = (len(s)
                        - 2 * s.count(self._prefix)
                        + 3 * s.count(self._prefix * 2))
        self._fancy = self._replace(styles_enabled or self._styles_enabled)

    @property
    def str(self) -> str:
        return self._s

    @property
    def fancy(self) -> str:
        return self._fancy

    def justify(self, width: int, align: int = 1, filler: str = ' ') -> str:
        w = max(width - len(self), 0)
        ws = (w // 2, w // 2 + w % 2)
        fill = lambda n, s=0: filler * sum(ws[i] for i in range(s, n))
        return f'{fill(align)}{self}{fill(2 * (align < 2), align)}'

    def _get_style(self, match: re.Match, enabled: bool) -> str:
        return self._styles[match.group(1)] if enabled else ''

    def _replace(self, styles_enabled: bool) -> str:
        s = self._s
        matches: tuple[re.Match[str]] = tuple(self._pattern.finditer(s))
        if not matches:
            return s
        return ''.join((s[:matches[0].span()[0]],
                        self._get_style(matches[0], styles_enabled),
                        *(s[matches[i].span()[1]:matches[i + 1].span()[0]]
                          + self._get_style(matches[i + 1], styles_enabled)
                          for i in range(len(matches) - 1)),
                        s[matches[-1].span()[1]:]))

    def __len__(self) -> int:
        return self._length

    def __str__(self) -> str:
        return self.fancy

    @staticmethod
    def set_styles_enabled(value: bool = True):
        FancyString._styles_enabled = value

    @staticmethod
    def _get_pattern():
        p = FancyString._prefix
        return re.compile(f'{p}([{p}{"".join(FancyString._styles.keys())}])')

    @staticmethod
    def set_prefix(prefix: str = _prefix):
        del FancyString._styles[FancyString._prefix]
        FancyString._styles[prefix] = prefix
        FancyString._prefix = prefix
        FancyString._pattern = FancyString._get_pattern()
        FancyString._reset = f'{prefix}0'


f = FancyString

DEFAULT_RATE = 1000

V_SEPARATOR = f(" | ")
H_SEPARATOR = f('-')

ARROW_UP = '↑'
ARROW_DOWN = '↓'

ALIGN = 2


def init(function):
    return function()


@init
def sign():
    _signs = {
        -1: '▼',
        0: ' ',
        1: '▲'
    }

    def inner(i: int):
        return _signs[int(copysign(1, i)) * bool(i)]

    return inner


@init
def format_size():
    _placeholder = '#'
    _units = (f'{_placeholder} ', *tuple(f'{m}{_placeholder}'
                                         for m in 'KMGTPEZY'))
    _base = 1024
    _log2_base = log2(_base)

    def inner(value: int, unit: str = 'B', precision: int = 1):
        if value <= 0:
            return f'-- {_units[0].replace(_placeholder, unit)}'
        multiple = trunc(log2(value) / _log2_base)
        value /= pow(_base, multiple)
        suffix = _units[multiple].replace(_placeholder, unit)
        return f"{value:.{precision}f} {suffix}"

    return inner


@init
def format_number():
    _units = (' ', 'k', 'm', 'g', 't', 'p')
    _no_suffix = _units[0]
    _base = 1000
    _non_positive = f'--{_units[0]}'

    def inner(value: int, precision: int = 2):
        if value <= 0:
            return _non_positive
        if value < _base:
            return f'{value}{_no_suffix}'
        unit = sum(abs(value / pow(_base, i)) >= 1
                   for i in range(1, len(_units)))
        return f'{value / pow(_base, unit):.{precision}f}{_units[unit]}'

    return inner


@init
def get_percent_style():
    _levels = (
        (85.0, 'db'),
        (65.0, 'y')
    )

    def prefix(style: str):
        return '#' + '#'.join(style)

    def inner(value: float):
        for threshold, style in _levels:
            if value >= threshold:
                return prefix(style)
        return prefix('r')

    return inner


def join(iterable, separator: Union[str, FancyString] = V_SEPARATOR):
    s = (separator if isinstance(separator, FancyString)
         else f(separator)).fancy
    return f'{s}{s.join(iterable)}{s}'


COLUMN_DEFINITIONS = {
    "packets-in": {
        "title": f"{ARROW_UP} Packets",
        "widest-value": 999.9,
        "width": 7,
        "delta-index": 2,
        "formatter": format_number
    },
    "packets-out": {
        "title": f"{ARROW_DOWN} Packets",
        "widest-value": 999.9,
        "width": 7,
        "delta-index": 3,
        "formatter": format_number
    },
    "bytes-in": {
        "title": f"{ARROW_UP} Bytes",
        "widest-value": 1023.9,
        "width": 9,
        "delta-index": 0,
        "formatter": format_size
    },
    "bytes-out": {
        "title": f"{ARROW_DOWN} Bytes",
        "widest-value": 1023.9,
        "width": 9,
        "delta-index": 1,
        "formatter": format_size
    },
    "cpu": {
        "title": "CPU",
        "widest-value": 100.0,
        "formatter": lambda x: f'{x}%',
        "style": get_percent_style,
        "get": cpu_percent
    },
    "memory": {
        "title": "Memory",
        "widest-value": 100.0,
        "width": 6,
        "formatter": lambda x: f'{x}%',
        "style": get_percent_style,
        "get": lambda: virtual_memory().percent
    }
}

COLUMNS_ORDER = (
    "packets-in",
    "packets-out",
    "bytes-in",
    "bytes-out",
    "cpu",
    "memory"
)

COLUMNS = tuple(COLUMN_DEFINITIONS[column] for column in COLUMNS_ORDER)


def get_style(column: dict):
    return (style if not isinstance(style := column.get('style', ''), str)
            else lambda x: style)


def build_get(column):
    if get := column.get('get'):
        return lambda _: get()
    index = column['delta-index']
    return lambda delta: delta[index]


def complete_column(column: dict):
    fmt = column['formatter']
    width = len(max(column['title'],
                    f'{fmt(column["widest-value"])} {sign(0)}',
                    key=len))
    column['width'] = width
    style = get_style(column)

    def formatter(x, last_x, *args):
        dx = x - last_x
        return f(f'{style(x)}{fmt(x, *args)} {sign(dx)}').justify(width, ALIGN)

    column['formatter'] = formatter
    column['get'] = build_get(column)


def make_header():
    return (join(f(c['title']).justify(c['width']) for c in COLUMNS) +
            '\n' +
            join(H_SEPARATOR.fancy * c['width'] for c in COLUMNS))


def make_logo(rate_ms: int):
    width = (len(V_SEPARATOR) +
             sum(len(V_SEPARATOR) + c['width'] for c in COLUMNS))
    return join((f(x).justify(width)
                 for x in (
                     '#p...:..:.:::.:..:...',
                     '#p.:.: #b#lREAL-TIME RESOURCES MONITOR#r #p:.:.',
                     f'#y(Refresh rate is {rate_ms}ms)')),
                '\n')


def enable_bits():
    factor = 8
    unit = 'b'

    def complete(index: int):
        get = COLUMNS[index]['get']
        formatter = COLUMNS[index]['formatter']
        COLUMNS[index]['get'] = lambda _: get(_) * factor
        COLUMNS[index]['title'] = COLUMNS[index]['title'].replace('Bytes',
                                                                  'Bits')
        COLUMNS[index]['formatter'] = lambda x, last_x: formatter(x,
                                                                  last_x,
                                                                  unit)

    for i, c in enumerate(COLUMNS):
        if any(word in c['title'].lower() for word in ('bits', 'bytes')):
            complete(i)


def last_print(message: str):
    print(f(message).fancy)
    exit()


@init
def confirm():
    _options = {
        'y': True,
        'n': False
    }
    _separator = '/'

    def inner(question: str, default: bool = True):
        order = tuple(sorted(_options.items(), key=lambda k, v: v == default))
        message = f'{f(question)} [{order[0].upper()}{_separator}{order[1]}]'
        while (response := input(message).lower()) and response not in _options:
            pass
        return _options.get(response, default)

    return inner


@init
def update():
    _version_pattern = re.compile("VERSION\\s*=\\s*'(\\d\\.\\d\\.\\d)'")

    _failed_to_fetch_message = f"""
#b#d'[!] Failed to fetch the script from the repo [!]#r
You may try to access the file (e.g. via browser): 
#y{REPO_URL}#r""".lstrip()

    _no_version_message = f"""
#b#d[!] Couldn't find the 'VERSION' in fetched script [!]""".lstrip()

    _update_to_newer_version_message = f"""
Your current version is #g{VERSION}#r.
But a newer version #b#p{{}}#r is available.
Do you wish to update?""".lstrip()

    _backup_message = f"""
Do you wish to make a backup of your current file {__file__}?""".lstrip()

    _failed_to_update_message = f"""
#b#d[!] Failed to update the {__file__} [!]#r
OS error message: {{}}""".lstrip()

    _failed_to_backup_message = f"""
#b#d[!] Failed to backup the {__file__} [!]
OS error message: {{}}""".lstrip()

    _text_differs_message = f"""
The version is up to date, but the script content differs from yours.
Probably, you've made some local changes.
Do you wish to reset them?""".lstrip()

    _actual_version_message = f"""
#gYou are up to date!""".lstrip()

    def backup():
        filepath = f'{__file__}.backup'
        print(f"Backup file: {filepath}")
        try:
            os.rename(__file__, filepath)
        except OSError as e:
            last_print(_failed_to_backup_message.format(e))

    def update_file(text: str):
        if confirm(_backup_message, False):
            backup()
        overwrite_file(text)

    def overwrite_file(text: str):
        try:
            with open(__file__, 'w') as file:
                file.write(text)
        except OSError as e:
            last_print(_failed_to_update_message.format(e))

    def inner():
        response = requests.get(REPO_URL)
        if response.status_code != 200:
            return last_print(_failed_to_fetch_message)

        text = response.text
        if not (match := _version_pattern.match(text)):
            return last_print(_no_version_message)

        version = match.group(1)
        if version > VERSION:
            if confirm(_update_to_newer_version_message.format(version)):
                return update_file(text)
            return last_print("Update canceled")

        with open(__file__) as file:
            current_text = file.read()
            if current_text != text:
                if confirm(_text_differs_message, False):
                    return update_file(text)
            return last_print(_actual_version_message)

    return inner


def monitor(gets: tuple,
            formatters: tuple,
            rate: float):
    with suppress(KeyboardInterrupt):
        last_counters = net_io_counters()
        last_values = tuple([0] * len(COLUMNS))

        while True:
            counters = net_io_counters()
            delta = tuple((current - last)
                          for current, last
                          in zip(counters, last_counters))
            last_counters = counters

            values = tuple(get(delta) for get in gets)

            print(join(formatters[i](value, last_value)
                       for i, (value, last_value)
                       in enumerate(zip(values, last_values))),
                  end='\r')

            last_values = values

            sleep(rate)


def run():
    pass


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-r', '--rate',
                        dest='rate', type=int,
                        default=DEFAULT_RATE,
                        help=f'''specify custom refresh rate in milliseconds
                        ({DEFAULT_RATE}ms by default)''')
    parser.add_argument('-f', '--fancy',
                        dest='fancy', action='store_true',
                        help='enable rich visuals (colors, bold font)')
    parser.add_argument('-t', "--tiny",
                        dest='tiny', action='store_true',
                        help="hide the logo and refresh-rate")
    parser.add_argument('-b', '--bits',
                        dest='bits', action='store_true',
                        help='''Show traffic in bits instead of bytes
                        (technically displays the value*8)''')
    parser.add_argument('-u', '--update',
                        dest='update', action='store_true',
                        help='check for never version and update if needed')
    return parser.parse_args()


def main():
    args = get_args()
    fancy = bool(args.fancy)
    FancyString.set_styles_enabled(fancy)

    if args.update:
        update()

    rate_ms = args.rate
    rate_s = rate_ms / 1000

    for c in COLUMNS:
        complete_column(c)

    if args.bits:
        enable_bits()
    if not args.tiny:
        print(make_logo(rate_ms))

    print(make_header())

    gets = tuple(c['get'] for c in COLUMNS)
    formatters = tuple(c['formatter'] for c in COLUMNS)
    monitor(gets, formatters, rate_s)

    print()


if __name__ == '__main__':
    main()
