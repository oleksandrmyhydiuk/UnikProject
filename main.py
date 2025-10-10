import tkinter as tk
from gui import FinanceAppGUI

def main():
    root = tk.Tk()
    app = FinanceAppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()