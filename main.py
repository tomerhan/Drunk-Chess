import sys
from ui.gui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting game...")
    except Exception as e:
        print(f"An error occurred: {e}")
