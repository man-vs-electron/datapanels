import threading

# A global lock that gets acquired before changing the page and released afterwards.
# Acquire and release this before doing complex drawing on a panel.
ui_lock = threading.Lock()

