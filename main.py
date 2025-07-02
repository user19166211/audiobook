import pyttsx3
import PyPDF2
from tkinter.filedialog import *

# asks to open a file's name
book = askopenfilename()
pdfreader = PyPDF2.PdfReader(book) 
pages = len(pdfreader.pages) # returns number of pages in the pdf

#read all data in PDF pages
for num in range(0,pages):
    page = pdfreader.pages[num] #gets the page at the number 'num', returned as an object
    text = page.extract_text() #extracts plaintext of the page
    player = pyttsx3.init()
    player.say(text)
    player.runAndWait()