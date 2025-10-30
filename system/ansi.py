from typing import Optional

RESET = '\x1b[0m'

STYLES = {
    'bold': '\x1b[1m',
    'underline': '\x1b[4m',
    'normal': RESET, # tbf I don't really need this
}

TEXT_COLORS = {
    'gray': '\x1b[30m',
    'red': '\x1b[31m',
    'green': '\x1b[32m',
    'yellow': '\x1b[33m',
    'blue': '\x1b[34m',
    'pink': '\x1b[38;5;218m',
    'cyan': '\x1b[36m',
    'white': '\x1b[37m',
    'purple' : '\x1b[0;35m'
}

BACKGROUND_COLORS = {
    'firefly_dark_blue': '\x1b[40m',
    'orange': '\x1b[41m',
    'marble_blue': '\x1b[42m',
    'greyish_turquoise': '\x1b[43m',
    'gray': '\x1b[44m',
    'indigo': '\x1b[45m',
    'light_gray': '\x1b[46m',
    'white': '\x1b[47m',
}

def get_ansi_codes(style: Optional[str], text_color: Optional[str], background_color: Optional[str]):
    """
    Returns a string containing the combined ANSI codes.
    Does NOT include the text or the reset code.
    """

    style_code = STYLES.get(style, '') #type: ignore
    text_code = TEXT_COLORS.get(text_color, '') #type: ignore
    bg_code = BACKGROUND_COLORS.get(background_color, '') #type: ignore
    
    return f"{style_code}{text_code}{bg_code}"

def format_ansi(text, style: Optional[str] = None, text_color: Optional[str] = None, background_color: Optional[str] = None, no_reset=False):
    """
    Returns a string of text fully wrapped with ANSI codes
    and a reset code at the end to prevent overflowing of the formatting to the rest of the terminal.
    """
    codes = get_ansi_codes(style, text_color, background_color)
    if no_reset:
        return f"{codes}{text}"

    return f"{codes}{text}{RESET}"

