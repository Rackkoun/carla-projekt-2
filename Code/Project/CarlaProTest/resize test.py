try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk

    py3 = False
except ImportError:
    import tkinter.ttk as ttk

class test:

    def __init__(self):
        pass
    def main(self):
        self.root=tk.Tk()
        self.root.title=("test resize")
        self.root.geometry("200x200")
        self.root.bind("<Configure>",self.rezize)
        self.root.mainloop()
    def rezize(self,event):
        #print(event.width, event.height)
        print(self.root.winfo_width(),self.root.winfo_height())

if __name__ == "__main__":
    t= test()
    t.main()

