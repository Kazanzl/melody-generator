#Import from requirement file to update the pyo and those stuffs
import os, winsound
#os.system('python -m pip install -r requirements.txt')
import tkinter as tk
from PIL import ImageTk
from tkinter import messagebox, filedialog
from music import MusicGen
from tkvideo import tkvideo

class Launcher:
    def __init__(self):
        self.music_popup = None
        self.root = tk.Tk()
        self.root.geometry("1080x720+200+20")
        self.root.title('Melody Launcher')
        self.root.iconbitmap('resources/musiclogo.ico') #set ico

        self.root.protocol('WM_DELETE_WINDOW', self.quit)

        bg = ImageTk.PhotoImage(file='resources/backgimg.png', master=self.root)
        bg_lbl = tk.Label(self.root, image=bg)
        bg_lbl.place(x=0,y=0, relwidth=1, relheight=1)

        self.root.columnconfigure(0, weight=1)

        xmu_logo = ImageTk.PhotoImage(file='resources/xmumlogo.png', master=self.root)
        xmu_lbl = tk.Label(self.root, image=xmu_logo)
        xmu_lbl.grid(row=0, column=0)

        title_lbl = tk.Label(self.root, text='Melody Generator', font=('Sylfaen', '36'), bg='black', fg='white')
        title_lbl.grid(row=1, pady=30)

        group_lbl = tk.Label(self.root, text='SOF106 Group 9 (G3)', font=('Sylfaen', '24'), bg='black', fg='white')
        group_lbl.grid(row=2)

        first_launch_btn = tk.Button(self.root, command=self.launch, text='Start New Session', font=('Times New Roman', '20'), bg='black', fg='gold', width=150)
        first_launch_btn.grid(row=3, padx=350, ipady=20, pady=(50, 0))

        load_btn = tk.Button(self.root, command=self.load, text='Load From Old Session', font=('Times New Roman', '20'), bg='black', fg='gold', width=150)
        load_btn.grid(row=4, padx=350, ipady=20, pady=(5, 0))

        exit_btn = tk.Button(self.root, command=self.quit, text='Exit', font=('Times New Roman', '20'), bg='black', fg='gold', width=150)
        exit_btn.grid(row=5, padx=350, ipady=20, pady=(5, 0))
        self.root.mainloop()
    
    def launch(self):
        #ensure there's only one top level 
        if self.music_popup is None or not self.music_popup.window.winfo_exists():
            self.music_popup = MusicGen()
        else:
            self.music_popup.window.lift(self.root)
    
    def load(self):
        folder = tk.filedialog.askdirectory()
        if not folder:
            return
        midifiles = os.listdir(folder)
        if not midifiles:
            tk.messagebox.showerror('Invalid Directory', 'No files detected.')
            return
        for file in midifiles:
            if not file.endswith('.mid'):
                tk.messagebox.showerror('Invalid Directory', 'Non-MIDI files detected.')
                return

        if self.music_popup is None or not self.music_popup.window.winfo_exists():
            self.music_popup = MusicGen(folder)
    
    def quit(self):
        confirm = tk.messagebox.askyesno('Exiting Launcher', 'Are you sure you want to quit?', icon='info')
        if confirm:
            self.root.quit()

Launcher()