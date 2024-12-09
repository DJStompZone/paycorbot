import os

DEBUG_MODE = os.getenv("PAYCORBOT_DEBUG", False) in [True, "true", "True"]

def log(*args, always = False, **kwargs):
    if DEBUG_MODE:
        print(*args, **kwargs)
