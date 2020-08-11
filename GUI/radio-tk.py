import tkinter as tk
import logging
class APP:
    def __init__(self):
        self.config_debugger()

        self.root = tk.Tk()
        self.root.title("Radio TESTING")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.debug_on_off = tk.IntVar()

        chk_btn = tk.Checkbutton(self.root, text='Debug', variable=self.debug_on_off, onvalue=1, offvalue=0, height=5, width = 5)
        chk_btn.pack()

        btn1 = tk.Button(self.root, text="check", command=self.check)
        btn1.pack(fill="both", expand=True, padx=10, pady=10)

        btn2 = tk.Button(self.root, text="exit!", command=self.destructor)
        btn2.pack(fill="both", expand=True, padx=10, pady=10)

    def config_debugger(self):
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
        logging.debug('Ready.')

    def check(self):
        logging.debug('checked.')
        logging.debug(self.debug_on_off.get())


    def destructor(self):
        self.root.destroy()

if __name__=="__main__":
    app = APP()
    app.root.mainloop()