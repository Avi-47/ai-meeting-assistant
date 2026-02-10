import keyboard

def register_trigger(callback):
    keyboard.add_hotkey("ctrl+space", callback)
