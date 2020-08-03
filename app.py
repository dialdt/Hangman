from flask import Flask, render_template, request, redirect, url_for
import requests
import random
import json

# Initial setup
words = [
   'corn',
    'bread',
    'baby',
    'rye',
    'milk',
    'drink'
]
guessLimit = 10
userGuesses = 0
userGuess = ""
word = ""
letterList = []
lettersGuessed = []
blankWord = []
win = False
lose = False
rightOrWrongMsg = ""
guessProgressMsg = ""
uri = 'https://random-word-api.herokuapp.com/word?number=1'

app = Flask(__name__)

def reset():
    global word, letterList, guessLimit, blankWord, rightOrWrongMsg, guessProgressMsg, win, lettersGuessed, lose
    response = requests.get(uri)
    data = json.loads(response.text)
    word = data[0]
    #word = words[random.randint(0, len(words) - 1)]
    letterList = [char for char in word]
    blankWord = []
    for i in letterList:
        blankWord.append("_")
    guessLimit = 10
    win = False
    lose = False
    rightOrWrongMsg = ""
    guessProgressMsg = ""
    lettersGuessed = []

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')

@app.route('/play', methods=["GET", "POST"])
def play():
    def checkGuess(g):
        global lettersGuessed, win, rightOrWrongMsg, guessProgressMsg
        # Check if user's guess is correct but they haven't found the whole word
        if g in lettersGuessed:
            rightOrWrongMsg = 'Already guessed that one buster!'
        else:
            lettersGuessed.append(g)
            # Check if user has guessed all letters correctly
            win = all(elem in lettersGuessed for elem in letterList)
            if g in letterList and win == False:
                rightOrWrongMsg = 'Marvellous!'
                populateWord(getIndexPositions(letterList, g), g)
                # give a guess back if correct
                trackGuesses(1)
            else:
                rightOrWrongMsg = 'Too bad...'
                trackGuesses(-1)

    def getIndexPositions(list_of_elems, element):
        ''' Returns the indexes of all occurrences of give element in
        the list- listOfElements '''
        index_pos_list = []
        index_pos = 0
        while True:
            try:
                # Search for item in list from indexPos to the end of list
                index_pos = list_of_elems.index(element, index_pos)
                # Add the index position in list
                index_pos_list.append(index_pos)
                index_pos += 1
            except ValueError as e:
                break
        return index_pos_list

    def trackGuesses(n):
        global guessLimit, rightOrWrongMsg, guessProgressMsg, rightOrWrongMsg, lose
        guessLimit = guessLimit + n
        if guessLimit == 1:
            guessProgressMsg = 'Last chance saloon!'
        elif guessLimit == 0:
            lose = True

    def populateWord(indexes, guess):
        global blankWord
        for i in indexes:
            blankWord[i] = guess

    if request.method == 'POST':
        req = request.form
        guess = req.get('guess')
        if len(guess) > 1:
            global rightOrWrongMsg
            rightOrWrongMsg = "One letter at a time there kid!"
        else: 
            checkGuess(guess)

    if win or lose:
        return render_template('winorlose.html', win = win, lose = lose, word = word)
    else: 
        return render_template(
            'play.html', 
            blankWord = blankWord,
            win = win,
            rightOrWrongMsg = rightOrWrongMsg,
            guessProgressMsg = guessProgressMsg,
            lose = lose,
            lettersGuessed = lettersGuessed,
            userGuesses = guessLimit
            )

@app.route('/reset')
def res():
    reset()
    return redirect('/play')
