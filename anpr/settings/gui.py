#!/home/laxz/miniconda3/envs/tfk/bin/python
import tkinter as tk
from configparser import SafeConfigParser
from os import path
class ActivityStart:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('300x200') 

        self.parser = SafeConfigParser()
        self.configpath = './anpr_mm.cfg'

        self.debug = tk.BooleanVar()
        self.test = tk.BooleanVar()
        self.localrun = tk.BooleanVar()
        self.read_settings() ###IMPORTANT###
        self.root.title("MM ANPR SETTINGS")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        frame = tk.Frame(self.root)
        frame.pack()
        chkOne = tk.Checkbutton(frame, text='Debug', variable=self.debug, onvalue=True, offvalue=False, height=2, width = 5)
        chkOne.pack()
        chkTwo = tk.Checkbutton(frame, text='Test' , variable=self.test, onvalue=True, offvalue=False, height=2, width = 5)
        chkTwo.pack()
        chkThree = tk.Checkbutton(frame, text='Self camera' , variable=self.localrun, onvalue=True, offvalue=False, height=2, width = 10)
        chkThree.pack()
        btn1 = tk.Button(frame, text = 'SET & Exit', width = 25,height=2, command = self.apply_settings)
        btn1.pack()
        btn2 = tk.Button(frame, text='Quit', width=25, height=2, command=self.destructor)
        btn2.pack()


    def read_settings(self):
        try:
            if path.exists(self.configpath):
                self.parser.read(self.configpath)
                self.debug.set(self.parser.get('gui', 'debug'))
                self.test.set(self.parser.get('gui','test'))
                self.localrun.set(self.parser.get('gui','localrun'))
            else: raise FileNotFoundError('404.Config File Not Found!\nYou may need to download "{}" from repo.'.format(self.configpath))
        except FileNotFoundError as e404:
            print(e404)
            exit()
        except Exception as e:
            print(e,'\nMaybe wrong configuration in {}'.format(self.configpath))
            exit()

    def apply_settings(self):
        self.parser.set('gui', 'debug', str(self.debug.get()))
        self.parser.set('gui', 'test', str(self.test.get()))
        self.parser.set('gui', 'localrun', str(self.localrun.get()))
        with open(self.configpath, 'w') as f:
            self.parser.write(f)
        self.destructor()

    def destructor(self):
        self.root.destroy()

if __name__ == '__main__':
    app = ActivityStart()
    app.root.mainloop()