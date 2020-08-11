import tkinter as tk

class ActivityStart:
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("TESTING")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.checkOne = tk.IntVar()
        self.checkTwo = tk.IntVar()

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        checkerOne = tk.Checkbutton(self.frame, text='Debug', variable=self.checkOne, onvalue=1, offvalue=0, height=2, width = 5)
        checkerOne.pack()

        checkerTwo = tk.Checkbutton(self.frame, text='Test' , variable=self.checkTwo, onvalue=1, offvalue=0, height=2, width = 5)
        checkerTwo.pack()

        self.btn1 = tk.Button(self.frame, text = 'RUN', width = 25,height=2, command = self.make_new_window)
        self.btn1.pack()

        self.btn2 = tk.Button(self.frame, text='Quit', width=25, height=2, command=self.destructor)
        self.btn2.pack()

    def make_new_window(self):
        ActivityMain(tk.Toplevel(self.root), self)

    def destructor(self):
        self.root.destroy()

class ActivityMain:
    def __init__(self, root, arg):
        self.parameters = arg
        self.root = root
        self.root.title()
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.text = tk.StringVar()
        self.label = tk.Label(self.root, textvariable=self.text)
        self.label.pack(padx=10, pady=10)
        self.text.set(self.parameters.checkOne.get())
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()

    def close_windows(self):
        self.root.destroy()

if __name__ == '__main__':
    app = ActivityStart()
    app.root.mainloop()