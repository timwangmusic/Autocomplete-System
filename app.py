import tkinter as tk

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parents[1]
print (src_dir)
sys.path.append(str(src_dir))

from src.advanced_trie_server import AdvTrie as Trie


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.app = Trie()

        self.text_box = tk.Entry()
        self.text_box.pack(side='top')

        self.text = tk.StringVar()
        self.text.set("Please enter search term")

        self.text_box["textvariable"] = self.text
        self.text_box.bind("<Key-Return>", self.search)

        self.result_text = tk.StringVar()
        self.result_text.set("No entry")

        self.display = tk.Label(text="Hello, world!")
        self.display["textvariable"] = self.result_text
        self.display.pack(side="bottom")

        self.quit = tk.Button(text="QUIT", fg="red",
                              command=master.destroy)
        self.quit.pack()

    def search(self, event):
        res = self.app.search(self.text.get())
        print(res)
        if len(res) > 0:
            self.result_text.set(res[0])
        else:
            self.result_text.set("no result")


root = tk.Tk()
app = Application(root)
app.mainloop()
