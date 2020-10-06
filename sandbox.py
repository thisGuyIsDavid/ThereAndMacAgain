from app.utils.inputs import get_key

keypad_inputs = {
    'KEY_KP0': 0,
    'KEY_KP1': 0,
    'KEY_KP2': 0,
    'KEY_KP3': 0,
    'KEY_KP4': 0,
    'KEY_KP5': 0,
    'KEY_KP6': 0,
    'KEY_KP7': 0,
    'KEY_KP8': 0,
    'KEY_KP9': 0,
    'KEY_KPPLUS': 0,
    'KEY_KPMINUS': 0,
    'KEY_BACKSPACE': 0,
    'KEY_KPASTERISK': 0,
    'KEY_NUMLOCK': 0,
    'KEY_KPSLASH': 0,
    'KEY_KPENTER': 0,
    'KEY_TAB': 0
}


def main():
    """Just print out some event infomation when keys are pressed."""
    while 1:
        events = get_key()
        if events:
            for event in events:
                key_pressed = keypad_inputs.get(event.code, None)
                if key_pressed is None:
                    print('\t', event.code)
                    continue
                if keypad_inputs[event.code] == 0:
                    print(event.code, '\n')
                    keypad_inputs[event.code] = 1
                else:
                    keypad_inputs[event.code] = 0


if __name__ == "__main__":
    main()