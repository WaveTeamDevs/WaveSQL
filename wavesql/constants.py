from pathlib import Path
import os
from colorama import Fore

CUR_PATH: Path = Path(os.path.dirname(os.path.realpath(__file__)))
PATH_DB_INIT_SCRIPTS = CUR_PATH / "sql"
CONFIG_PATH = CUR_PATH / "config.ini"


LOG_COLORS = {
    "GREEN": Fore.GREEN,
    "LIGHTGREEN": Fore.LIGHTGREEN_EX,
    "YELLOW": Fore.YELLOW,
    "LIGHTYELLOW": Fore.LIGHTYELLOW_EX,
    "RED": Fore.RED,
    "LIGHTRED": Fore.LIGHTRED_EX,
    "CYAN": Fore.CYAN,
    "LIGHTCYAN": Fore.LIGHTCYAN_EX,
    "BLUE": Fore.BLUE,
    "LIGHTBLUE": Fore.LIGHTBLUE_EX,
    "MAGENTA": Fore.MAGENTA,
    "LIGHTMAGENTA": Fore.LIGHTMAGENTA_EX,
    "WHITE": Fore.WHITE,
    "LIGHTWHITE": Fore.LIGHTWHITE_EX,
    "BLACK": Fore.BLACK,
    "LIGHTBLACK": Fore.LIGHTBLACK_EX,
}
