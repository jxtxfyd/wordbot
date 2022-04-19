import random
import sqlite3

class Hangman:
    chosen_word = ""
    guessed_letters = ""
    remaining_guesses = 6

    game_ended = False
    game_won = False

    def start_game(self):
        random.seed()
        conn = sqlite3.connect('wordbot.db')
        cursor = conn.cursor()
        row = cursor.execute("select word from lookup order by RANDOM() LIMIT 1;").fetchone()
        self.chosen_word = row[0]
        conn.close()

        new_string = ""
        for i in range(0, len(self.chosen_word)):
            new_string += "?"
        self.guessed_letters = new_string

    def get_game_status(self):
        message = ""

        if not self.game_ended:
            letters = ""
            for i in range(0, len(self.guessed_letters)):
                letters += self.guessed_letters[i] + " "
            message = '{} guesses left \n'.format(self.remaining_guesses)
            message += letters

        if self.game_ended and self.game_won:
            message += '\n You won! You correctly guessed ' + '`{}`'.format(self.chosen_word)
        elif self.game_ended and not self.game_won:
            message += '\n You lost! The correct word was ' + '`{}`'.format(self.chosen_word)

        return message

    def guess(self, message):
        args = message.split(' ')
        guess = ""
        contains_guess = False

        if len(args) > 1:
            guess = args[1]

        for i in range(0, len(self.chosen_word)):
            if guess[0] == self.chosen_word[i]:
                self.guessed_letters = self.guessed_letters[:i] + guess[0] + self.guessed_letters[i + 1:]
                contains_guess = True
        if not contains_guess:
            self.remaining_guesses -= 1

        unguessed_letters = False
        for letter in self.guessed_letters:
            if letter == "?":
                unguessed_letters = True

        if not unguessed_letters:
            self.game_ended = True
            self.game_won = True

        if self.remaining_guesses < 0:
            self.game_ended = True
            self.game_won = False 