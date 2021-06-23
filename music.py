#Import from requirement file to update the pyo and those stuffs
import os
os.system('python -m pip install -r requirements.txt')
#Import tkinter
import tkinter as tk
#import pyo Audio
from pyo import *
# XD Dont need comment for every line, affect readability

#s = server()
#Under s, boot()
#e = Events(argument)
s = Server().boot()
e = Events(midinote=[54], beat=[1.0], midivel=[10], bpm=100,
            attack=0.001,
            decay=0.05,
            sustain=0.5,
            release=0.005)
e.play()
s.start()
e.stop(1)
input("Any Key To Boot")
s.stop()

#Tkinter Interface
#Continue on tomorrow21/6
#Recalling for designs and those stuffs

'''

I'm going to try changing the `num_notes` input to `time_signature`, 
because `num_notes` is not really a good parameter.


'''

#Number of bar
#Notes per bar
#Number of steps
#Introduce Pauses
#Key
#Scale
#Scale Root
#Population size
#Number of mutations
#Rating fitness
#Display result
#Save population into midi file
#Continue or not input
