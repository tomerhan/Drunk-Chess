import os
import sys

# Crucial for Android/Pydroid 3 display driver
if 'ANDROID_ARGUMENT' in os.environ:
    os.environ['SDL_VIDEODRIVER'] = 'android'

try:
    import pygame
    # Force full init early
    pygame.init()
    pygame.display.init()
    pygame.font.init()
except Exception as e:
    print(f"Pygame initialization notice: {e}")

# Now import UI, which expects Pygame to be ready
from ui.gui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Drunk Chess...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
