import requests
import pathlib,os
import random
import tkinter as tk
from PIL import ImageTk, Image
from dataclasses import dataclass, field
from typing import List
#from functools import partial

# Current working directory (established upon execution of file)
current_dir = pathlib.Path(__file__).parent.resolve() # current directory

# Request websites: Dictionary Check and Random Word Generator
end_point = 'https://api.dictionaryapi.dev/api/v2/entries/en/'
random_word = 'https://random-word-api.herokuapp.com/word'

###############
## FUNCTIONS ##
###############

## FIND INDICES ##
def find_indices(input_list, item): # Checks for all the instances of an item in the list and returns the indices
    indices = []
    for idx, value in enumerate(input_list):
        if value == item:
            indices.append(idx)
    return indices

## HM Class ##
@dataclass
class HangmanObject():
    hm_count: int = 0
    incorrect_guesses: List[str] = field(default_factory= lambda: [])
    secret_word: str = ''
    secret_word_progress: List[str] = field(default_factory= lambda:[])

## HM Window Class (inherits from Tk and from HangmanObject)
class HmWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # HM State
        self.hm_state = {
            0:'HangmanTitleCard.png',
            1:'hm1.png',
            2:'hm2.png',
            3:'hm3.png',
            4:'hm4.png',
            5:'hm5.png',
            6:'hm6.png',
            7:'hm7.png',
            }
        
        # HM Object
        self.HangmanObject = HangmanObject()

        # Configure the root window
        self.title('HANGMAN GAME')

        # Create the frames for the window
        self.main_hud = tk.Canvas(master=self, relief=tk.RIDGE, borderwidth=2, width= 400, height = 400, bg='white') # This is the display where cards will go
        self.stat_frame = tk.Frame(master=self, relief=tk.RIDGE, borderwidth=2, width = 150, height = 200, bg='white') # This is the status frame
        self.instruction_frame = tk.Frame(master=self, relief=tk.RIDGE, borderwidth=2, width=250, height=100) # Here go the instructions
        self.entry_frame = tk.Frame(master=self, relief=tk.RIDGE, borderwidth=2,width=250,height=100) # Here goes the entry text box and the entry button

        # Organize the window
        self.main_hud.grid(row=0,columnspan=2)
        self.stat_frame.grid(row=1,rowspan=2,column=0,padx=5,pady=5,sticky='NS')
        self.instruction_frame.grid(row=1,column=1)
        self.entry_frame.grid(row=2,column=1)

        # Initialize content of the Stat Frame 
        self.inc_gss_lbl = tk.Label(master=self.stat_frame, relief=tk.RAISED, text= f"Incorrect Guesses ({self.HangmanObject.hm_count}/{len(self.hm_state)-1}):\nNo wrong guesses yet")
        self.sec_wrd_lbl = tk.Label(master=self.stat_frame, relief=tk.RAISED, text= f"Secret Word: {self.HangmanObject.secret_word}\nNo Secret Word yet!")

        # Organize the Stat Frame
        self.inc_gss_lbl.grid(row=0,column=0,pady=5,sticky='EW')
        self.sec_wrd_lbl.grid(row=1,column=0,pady=5,sticky='EW')

        # Initial content of Main HUD
        img_path = os.path.join(current_dir, self.hm_state[0])
        self.img = ImageTk.PhotoImage(Image.open(img_path))
        self.img_lbl = tk.Label(master=self.main_hud, image=self.img)
        self.img_lbl.pack()

        # Initial content of the Instruction Frame
        self.instruction_lbl = tk.Label(master=self.instruction_frame, text="Welcome to the Hangman Game! 1: Against another Player 2: Against Computer ")
        self.instruction_lbl.pack()

        # Intial content of the Entry Frame
        self.text_entry = tk.Entry(master=self.entry_frame)
        self.text_entry.pack(side=tk.LEFT, padx='100')
        self.enter_button = tk.Button(master=self.entry_frame, text="Enter", command = self.mode_selection)
        self.bind('<Return>',self.mode_selection)
        self.enter_button.pack(side=tk.LEFT)

    def mode_selection(self,event=None): # Chooses the mode (single player or against the computer) 
        if self.text_entry.get() ==  '1': 
            self.instruction_lbl['text'] = 'Playing against another player. Choose a Secret Word: '
            self.text_entry.delete(0,tk.END)
            self.enter_button['command'] = self.sec_wrd_input
            self.bind('<Return>',self.sec_wrd_input)
            return
        elif self.text_entry.get() == '2':
            self.instruction_lbl['text'] = 'Random secret word will be generated'
            self.text_entry.delete(0,tk.END)
            self.text_entry.insert(tk.END,'Press enter to continue')
            self.text_entry.configure(state='disabled')
            self.enter_button['command'] = self.sec_wrd_generator
            self.bind('<Return>',self.sec_wrd_generator)
        else:
            self.instruction_lbl['text'] = 'That is not a valid input! 1: Against another Player 2: Against Computer'
            self.text_entry.delete(0,tk.END)
            return
        
    def sec_wrd_generator(self,event=None): # Generates a secret word from online requests, but if it times out loads an offline library
        response = requests.get(random_word,timeout=5)
        if response.status_code == 200:
            filename = os.path.join(current_dir, 'hangman_words.txt')
            txt = open(filename,'r')
            word_list = txt.readlines()
            txt.close()
            self.HangmanObject.secret_word = word_list[random.randint(0,len(word_list))]
            self.HangmanObject.secret_word = self.HangmanObject.secret_word.lower().strip()
        else:
            self.HangmanObject.secret_word = response.text[2:-2].lower().strip()

        self.HangmanObject.secret_word_progress = len(self.HangmanObject.secret_word)*['_']

        self.enter_button['command'] = self.game_loop
        self.bind('<Return>',self.game_loop)
        self.enter_button['text'] = 'Please enter your guess (single letter): '

        self.text_entry.delete(0,tk.END)
        self.text_entry.configure(state='normal')

        self.inc_gss_lbl['text'] = f"Incorrect Guesses ({self.HangmanObject.hm_count}/{len(self.hm_state)-1}):\n{','.join(self.HangmanObject.incorrect_guesses)}"
        self.sec_wrd_lbl['text'] = f"Secret Word:\n{' '.join(self.HangmanObject.secret_word_progress)}"
        #self.inc_list_lbl['text'] = f"{','.join(self.HangmanObject.incorrect_guesses)}"
        #self.sec_wrd_progress_lbl['text'] = f"{' '.join(self.HangmanObject.secret_word_progress)}"
        return
    
    def sec_wrd_input(self,event=None):
        secret_word = self.text_entry.get().strip().lower()
        response = requests.get(end_point + secret_word)
        if not secret_word:
            self.instruction_lbl['text'] = 'The secret word cannot be blank. Please type a secret word: '
            self.text_entry.delete(0,tk.END)
            return
        elif not response.status_code == 200:
            self.instruction_lbl['text'] = 'That word is not in our dictionary. Please type a secret word: '
            self.text_entry.delete(0,tk.END)
            return
        else:
            self.HangmanObject.secret_word = secret_word
            self.HangmanObject.secret_word_progress = len(secret_word)*['_']

            self.instruction_lbl['text'] = 'Please enter your guess (single letter): '
            self.text_entry.delete(0,tk.END)

            self.inc_gss_lbl['text'] = f"Incorrect Guesses ({self.HangmanObject.hm_count}/{len(self.hm_state)-1}):\n{','.join(self.HangmanObject.incorrect_guesses)}"
            self.sec_wrd_lbl['text'] = f"Secret Word:\n{' '.join(self.HangmanObject.secret_word_progress)}"

            self.enter_button['command'] = self.game_loop
            self.bind('<Return>',self.game_loop)
            return 

    def game_loop(self,event=None):
        if not (guess:= self.text_entry.get()).lower().strip().isalpha() or len(guess) > 1:
            self.instruction_lbl['text'] = 'Guess cannot be blank and must be a single letter. Please try again: '
            self.text_entry.delete(0,tk.END)
            return
        elif guess in self.HangmanObject.incorrect_guesses or guess in self.HangmanObject.secret_word_progress:
            self.instruction_lbl['text'] = 'You have already guessed that letter. Please try again: '
            self.text_entry.delete(0,tk.END)
            return
        else:
            guess_indices = find_indices(self.HangmanObject.secret_word, guess)

        if not guess_indices and self.HangmanObject.hm_count < (len(self.hm_state) - 2): # See how we can make this not dependent of a fixed number in case hm_states changes
            self.HangmanObject.hm_count  += 1
            self.HangmanObject.incorrect_guesses.append(guess)

            self.inc_gss_lbl['text'] = f"Incorrect Guesses ({self.HangmanObject.hm_count}/{len(self.hm_state)-1}):\n{','.join(self.HangmanObject.incorrect_guesses)}"
            self.sec_wrd_lbl['text'] = f"Secret Word:\n{' '.join(self.HangmanObject.secret_word_progress)}"

            img_path = os.path.join(current_dir, str(self.hm_state[self.HangmanObject.hm_count]))
            self.img = ImageTk.PhotoImage(Image.open(img_path))
            self.img_lbl.configure(image=self.img)
            self.img_lbl.image = self.img

            self.instruction_lbl['text'] = 'That guess was wrong, please try again: '
            self.text_entry.delete(0,tk.END)
            return
            
        elif guess_indices:
            for pos in guess_indices:
                self.HangmanObject.secret_word_progress[pos] = guess
            if "".join(self.HangmanObject.secret_word_progress) == self.HangmanObject.secret_word:
                self.instruction_lbl['text'] = f'You win! The secret word was "{self.HangmanObject.secret_word}"'
                self.text_entry.destroy()

                self.inc_gss_lbl['text'] = f"Incorrect Guesses ({self.HangmanObject.hm_count}/{len(self.hm_state)-1}):\n{','.join(self.HangmanObject.incorrect_guesses)}"
                self.sec_wrd_lbl['text'] = f"Secret Word:\n{' '.join(self.HangmanObject.secret_word_progress)}"
                return
            else:
                self.instruction_lbl['text'] = 'That guess was correct, please enter next guess: '
                self.text_entry.delete(0,tk.END)

                self.inc_gss_lbl['text'] = f"Incorrect Guesses ({self.HangmanObject.hm_count}/{len(self.hm_state)-1}):\n{','.join(self.HangmanObject.incorrect_guesses)}"
                self.sec_wrd_lbl['text'] = f"Secret Word:\n{' '.join(self.HangmanObject.secret_word_progress)}"
                return
        else:
            self.HangmanObject.hm_count += 1

            self.instruction_lbl['text'] = f'You lose! The word was: "{self.HangmanObject.secret_word}"'
            self.text_entry.destroy()
            self.enter_button.destroy()

            self.inc_gss_lbl['text'] = f"Incorrect Guesses ({self.HangmanObject.hm_count}/{len(self.hm_state)-1}):\n{','.join(self.HangmanObject.incorrect_guesses)}"
            self.sec_wrd_lbl['text'] = f"Secret Word:\n{' '.join(self.HangmanObject.secret_word_progress)}"
            return

# Runs the game
HmWindow().mainloop()