# main.py

import tkinter as tk
from structure import ClipboardManager

def main():
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()