import tkinter as tk
from pyo import *
from tkvideo import tkvideo
import winsound, os, random
from tkinter import ttk, filedialog
from mgen import *

class MusicGen:
    def __init__(self, savefolder=None):
        musicfiles = []
        for file in os.listdir('resources'):
            if file.endswith('.wav'):
                musicfiles.append(file)
        self.random_bgm = random.choice(musicfiles)
        print(self.random_bgm)
        winsound.PlaySound(f'resources/{self.random_bgm}', winsound.SND_ALIAS | winsound.SND_LOOP + winsound.SND_ASYNC)

        self.savefolder = savefolder

        self.window = tk.Toplevel()
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.window.geometry('1408x792')
        #self.window.state('zoomed') #if you want maximized

        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()


        self.bg_label = tk.Label(self.window)
        self.bg_label.place(x=0,y=0, relwidth=1, relheight=1)
        player = tkvideo("resources/Musicbg.mp4", self.bg_label, loop = 1, size = (width, height))
        player.play()


        for i in range(6):
            self.window.rowconfigure(i, weight=1)
            self.window.columnconfigure(i, weight=1)

        self.num_bars = tk.IntVar(value=4)
        tk.Label(self.window, text='Number of bars', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=0, column=0, pady=(40, 5), padx=(20, 20))
        ttk.Spinbox(self.window, from_=1, to=80, textvariable=self.num_bars, font=('Sylfaen', '16'), width=15, state='readonly', wrap=True).grid(row=0, column=1, pady=(40, 5))
        
        self.time_sign = tk.StringVar()
        tk.Label(self.window, text='Time Signature', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=0, column=2, pady=(40, 5), padx=(20, 20))
        time_sign_box = ttk.Combobox(self.window, values=TIME_SIGNS, font=('Sylfaen', '16'), textvariable=self.time_sign, state='readonly', width=15)
        time_sign_box.current(0)
        time_sign_box.grid(row=0, column=3, pady=(40, 5), padx=(20, 20))

        self.key = tk.StringVar()
        tk.Label(self.window, text='Key', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=1, column=0, pady=(5, 5), padx=(20, 20))
        key_box = ttk.Combobox(self.window, values=KEYS, font=('Sylfaen', '16'), textvariable=self.key, state='readonly', width=15)
        key_box.current(0)
        key_box.grid(row=1, column=1, pady=(5, 5), padx=(20, 20))

        self.num_steps = tk.IntVar(value=1)
        tk.Label(self.window, text='Number of pitches\n(2 or 3 for chords)', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=1, column=2, pady=(5, 5), padx=(20, 20))
        ttk.Spinbox(self.window, from_=1, to=3, textvariable=self.num_steps, font=('Sylfaen', '16'), width=15, state='readonly', wrap=True).grid(row=1, column=3, pady=(5, 5))

        self.scale = tk.StringVar()
        tk.Label(self.window, text='Scale/Mode', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=2, column=0, pady=(5, 5), padx=(20, 20))
        key_box = ttk.Combobox(self.window, values=SCALES, font=('Sylfaen', '16'), textvariable=self.scale, state='readonly', width=15)
        key_box.current(0)
        key_box.grid(row=2, column=1, pady=(5, 5), padx=(20, 20))

        self.octave = tk.IntVar(value=4)
        tk.Label(self.window, text='Octave\n(As lowest pitch)', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=2, column=2, pady=(5, 5), padx=(20, 20))
        ttk.Spinbox(self.window, from_=1, to=6, textvariable=self.octave, font=('Sylfaen', '16'), width=15, state='readonly', wrap=True).grid(row=2, column=3, pady=(5, 5))
        
        self.bpm = tk.IntVar(value=120)
        tk.Label(self.window, text='BPM', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=3, column=0, pady=(5, 5), padx=(20, 20))
        ttk.Spinbox(self.window, from_=20, to=220, textvariable=self.bpm, font=('Sylfaen', '16'), width=15, state='readonly', wrap=True).grid(row=3, column=1, pady=(5, 5))

        self.num_mutation = tk.IntVar(value=10)
        tk.Label(self.window, text='Mutation Count', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=3, column=2, pady=(5, 5), padx=(20, 20))
        ttk.Spinbox(self.window, from_=1, to=99, textvariable=self.num_mutation, font=('Sylfaen', '16'), width=15, state='readonly', wrap=True).grid(row=3, column=3, pady=(5, 5))

        self.population_size = tk.IntVar(value=10)
        tk.Label(self.window, text='Population Size', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=4, column=0, pady=(5, 5), padx=(20, 20))
        ttk.Spinbox(self.window, from_=3, to=20, textvariable=self.population_size, font=('Sylfaen', '16'), width=15, state='readonly', wrap=True).grid(row=4, column=1, pady=(5, 5))

        self.mutation_probability = tk.StringVar(value=0.7)
        tk.Label(self.window, text='Mutation Probability', font=('Sylfaen', '18'), bg='black', fg='white').grid(row=4, column=2, pady=(5, 5), padx=(20, 20))
        ttk.Scale(self.window, orient=tk.HORIZONTAL, length=150, from_=0.0, to=1.0, variable=self.mutation_probability, command=self.check_prob_increments).grid(row=4, column=3, pady=(5, 5), padx=(20, 20))
        tk.Label(self.window, textvariable=self.mutation_probability, font=('Sylfaen', '18'), bg='black', fg='white').grid(row=5, column=3, sticky='n')

        tk.Button(self.window, text='Cancel', font=('Sylfaen', '30'), width=15, command=self.close).grid(row=6, column=0, columnspan=2, pady=(0, 20))
        tk.Button(self.window, text='Generate', font=('Sylfaen', '30'), width=15, command=self.generate).grid(row=6, column=2, columnspan=2, pady=(0, 20))

        self.rating = tk.IntVar()
        rate_label = tk.Label(self.window, text='Rate (0-5)', font=('Sylfaen', '48'))
        rate_box = ttk.Combobox(self.window, values=[0, 1, 2, 3, 4, 5], font=('Sylfaen', '48'), textvariable=self.rating, state='readonly', width=15)
        rate_box.current(0)

        back_btn = tk.Button(self.window, text='Quit', font=('Sylfaen', '48'), width=15, command=self.back)
        proceed_btn = tk.Button(self.window, text='Proceed', font=('Sylfaen', '48'), width=15, command=self.proceed_rating)
        self.rating_widgets = [rate_label, rate_box, back_btn, proceed_btn]

        if self.savefolder is not None:
            self.resume()

    def close(self):
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.window.destroy()

    def check_prob_increments(self, value):
        value = self.mutation_probability.get()
        if len(value) > 3:
            self.mutation_probability.set(round(float(value), 1))
    
    def generate(self):
        tk.messagebox.showinfo('Save Location', 'Choose a location to save relevant files.', parent=self.window)
        self.folder = tk.filedialog.askdirectory()

        self.window.lift()
        if not self.folder:
            return
        self.bg_label.lift()
        winsound.PlaySound(None, winsound.SND_PURGE)

        for i, widget in enumerate(self.rating_widgets):
            widget.grid(row=(i//2)*3, column=(i%2)*2, rowspan=3, columnspan=2, padx=(30, 30), pady=(40, 40))
            widget.lift()

        time_sign = (int(self.time_sign.get()[0]), int(self.time_sign.get()[-1]))
        population_id = 0
        self.server = Server().boot()

        #initialize an empty population with meta data
        self.musics = Music(self.key.get(), self.scale.get(), self.octave.get(), time_sign, self.bpm.get(),  self.num_steps.get(), population_id, self.num_mutation.get(), float(self.mutation_probability.get()))
        
        max_beats = int(self.num_bars.get()) * 4/time_sign[1] * time_sign[0]

        #populate the pool
        for _ in range(self.population_size.get()):
            self.musics.add_melody(*generate_music(max_beats))
        
        self.run()
    
    def resume(self):
        self.window.lift()
        self.bg_label.lift()
        winsound.PlaySound(None, winsound.SND_PURGE)

        for i, widget in enumerate(self.rating_widgets):
            widget.grid(row=(i//2)*3, column=(i%2)*2, rowspan=3, columnspan=2, padx=(30, 30), pady=(40, 40))
            widget.lift()
        
        self.server = Server().boot()
        self.musics = Music.generate_from_folder(self.savefolder)
        # self.key = self.musics.key
        # self.scale = self.musics.scale
        # self.octave = self.musics.octave
        # self.time_sign = self.musics.time_sign
        # self.bpm = self.musics.bpm
        # self.num_steps = self.musics.num_steps
        # self.generation = self.musics.generation
        self.num_mutation.set(self.musics.num_mutations)
        self.mutation_probability.set(self.musics.mutation_probability) 
        self.population_size.set(len(self.musics.population))
        self.musics.generation += 1
        self.run()

    def back(self):
        self.musics.population[self.count].stop_playing()
        self.bg_label.lower()
        for widget in self.rating_widgets:
            widget.lower()
        winsound.PlaySound(f'resources/{self.random_bgm}', winsound.SND_ALIAS | winsound.SND_LOOP + winsound.SND_ASYNC)
    
    def proceed_rating(self):
        self.server.stop()
        current_melody = self.musics.population[self.count]
        current_melody.stop_playing()
        current_melody.set_rating(self.rating.get())
        self.pool.append([current_melody.note_degrees, current_melody.durations, self.rating.get()])
        self.rating.set(0)
        self.count += 1
        
        if self.count == self.population_size.get():
            if self.savefolder is None:
                self.musics.save_to_midi(self.folder, first_time_saving=True)
            else:
                self.musics.save_to_midi(self.savefolder, first_time_saving=False)
            cont = tk.messagebox.askyesno('Reached Last Melody', 'The session has been successfully saved and can be resumed in the future. Proceed to next generation?', parent=self.window)
            if cont:
                self.perform_ga()
            else:
                self.bg_label.lower()
                for widget in self.rating_widgets:
                    widget.lower()
                self.window.lift()
                winsound.PlaySound(f'resources/{self.random_bgm}', winsound.SND_ALIAS | winsound.SND_LOOP + winsound.SND_ASYNC)
                return
        else:
            self.musics.population[self.count].start_playing(self.server)
    
    def run(self):
        self.pool = []
        self.count = 0
        self.window.lift()
        self.musics.population[0].start_playing(self.server)
    
    def perform_ga(self):
        #elitism
        elitists = elitist_selection(self.pool, lambda x: x[2])
        next_gen = [[note, rhythm] for note, rhythm, _ in elitists]

        crossovers_remaining = (len(self.musics.population) - len(elitists))//2
        for _ in range(crossovers_remaining):
            #single point crossover
            parents = selection_pair(self.pool, lambda x: x[2])
            note_parents, rhythm_parents, _ = zip(*parents)

            *note_children, p = single_point_crossover(*note_parents)
            *rhythm_children, _ = single_point_crossover(*rhythm_parents, cutpoint=p)

            #mutation
            note_children = [mutate_note(child, self.num_mutation.get(), float(self.mutation_probability.get())) for child in note_children]
            rhythm_children = [mutate_rhythm(child, self.num_mutation.get(), float(self.mutation_probability.get())) for child in rhythm_children]

            for notes, rhythms in list(zip(note_children, rhythm_children)):
                notes[0] = 0
                next_gen.append([notes, rhythms])
        
        self.musics.generation += 1
        new_population = []
        for notes, rhythms in next_gen:
            new_population.append(Melody(notes, rhythms, self.musics.key, self.musics.scale, self.musics.octave, self.musics.time_sign, self.musics.bpm, self.musics.num_steps))

        self.musics.population = new_population
        self.run()

        