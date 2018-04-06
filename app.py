import tkinter as tk

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parents[1]
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

        self.search_res = tk.Text(font=('Verdana',10))
        self.search_res.pack()

        self.quit = tk.Button(text="QUIT", fg="pink", bg='blue',
                              command=master.destroy)
        self.quit.pack(side="bottom")

        self.clear = tk.Button(text="Clear", command=lambda: self.search_res.delete(1.0, tk.END))
        self.clear.pack()

    def search(self, event):
        self.search_res.delete(1.0, tk.END)
        res = self.app.search(self.text.get())
        print(res)
        if len(res) > 0:
            for word in res:
                self.search_res.insert(tk.END, word + '\n')
        else:
            self.search_res.insert(tk.END, "no result")


root = tk.Tk()
app = Application(root)
app.mainloop()
