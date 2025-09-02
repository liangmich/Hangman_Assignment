"""Hangman game using Python and NLTK corpus."""

import os
import sys
import time
import random
import nltk

# NLTK corpus imports
try:
    from nltk.corpus import words as nltk_words
    from nltk.corpus import brown
except ImportError:
    nltk.download("words", quiet=True)
    nltk.download("brown", quiet=True)
    from nltk.corpus import words as nltk_words
    from nltk.corpus import brown

# Conditional imports for timed input
MSVCRT = None
SELECT_MODULE = None

if os.name == "nt":
    import msvcrt
    MSVCRT = msvcrt
else:
    import select
    SELECT_MODULE = select

# Default constants
DEFAULT_MAX_LIVES = 6
DEFAULT_TIME_LIMIT = 15
MAX_WORD_LENGTH = 8


def load_word_lists():
    """Load words and phrases from NLTK corpus."""
    words_list = [
        w.lower() for w in nltk_words.words()
        if w.isalpha() and len(w) <= MAX_WORD_LENGTH
    ]
    brown_words = [w.lower() for w in brown.words() if w.isalpha()]
    return words_list, brown_words


# Load global word lists
WORDS_LIST, BROWN_WORDS = load_word_lists()


class HangmanGame:
    """Class to handle Hangman game logic."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, max_lives=DEFAULT_MAX_LIVES, mode="basic",
                 time_limit=DEFAULT_TIME_LIMIT):
        """Initialize game settings and select word or phrase."""
        self.words = WORDS_LIST
        self.brown_words = BROWN_WORDS
        self.max_lives = max_lives
        self.lives = max_lives
        self.mode = mode
        self.time_limit = time_limit
        self.answer = self._choose_word()
        self.guessed_letters = set()
        self.display_word = self._init_display()

    def _choose_word(self):
        """Choose a random word or phrase based on mode."""
        if self.mode == "basic":
            return random.choice(self.words).lower()
        phrase_length = random.randint(3, 5)
        return " ".join(
            random.choice(self.brown_words)
            for _ in range(phrase_length)
        ).lower()

    def _init_display(self):
        """Create display string with underscores for letters."""
        return "".join("_" if c.isalpha() else c for c in self.answer)

    def _update_display(self, letter):
        """Update display string with correctly guessed letter."""
        new_display = list(self.display_word)
        for i, c in enumerate(self.answer):
            if c == letter:
                new_display[i] = letter
        self.display_word = "".join(new_display)

    def is_won(self):
        """Return True if all letters have been guessed."""
        return "_" not in self.display_word

    def is_lost(self):
        """Return True if lives are zero."""
        return self.lives <= 0

    def timed_input(self, prompt, timeout):
        """Get input from user with a timeout."""
        if os.name == "nt":
            return self._windows_timed_input(prompt, timeout)
        return self._posix_timed_input(prompt, timeout)

    def _render_timer_line(self, prompt, typed, remaining):
        """Render prompt with countdown timer."""
        line = f"\r{prompt}{typed}   {remaining:2d}s"
        sys.stdout.write(line + " " * 10)
        sys.stdout.flush()

    def _windows_timed_input(self, prompt, timeout):
        """Timed input for Windows systems."""
        typed = ""
        end = time.time() + timeout
        while True:
            remaining = int(max(0, end - time.time()))
            self._render_timer_line(prompt, typed, remaining)
            if time.time() >= end:
                sys.stdout.write("\n")
                return None
            if MSVCRT and MSVCRT.kbhit():
                ch = MSVCRT.getwch()
                if ch in ("\r", "\n"):
                    sys.stdout.write("\n")
                    return typed.strip()
                if ch == "\b":
                    typed = typed[:-1]
                else:
                    typed += ch
            time.sleep(0.05)

    def _posix_timed_input(self, prompt, timeout):
        """Timed input for Linux/Mac systems."""
        end = time.time() + timeout
        sys.stdout.write(prompt)
        sys.stdout.flush()
        typed = ""
        last_shown = None
        while True:
            remaining = int(max(0, end - time.time()))
            if remaining != last_shown:
                self._render_timer_line(prompt, typed, remaining)
                last_shown = remaining
            if time.time() >= end:
                sys.stdout.write("\n")
                return None
            if SELECT_MODULE:
                rlist, _, _ = SELECT_MODULE.select([sys.stdin], [], [], 0.2)
                if rlist:
                    line = sys.stdin.readline()
                    sys.stdout.write("\n")
                    return line.strip()

    def play(self):
        """Run the main game loop."""
        print("Welcome to Hangman!")
        print(f"Game Mode: {self.mode.title()}")
        print(
            f"You have {self.lives} lives. "
            "Guess letters to reveal the word/phrase."
        )
        print(f"You have {self.time_limit} seconds per guess.\n")

        while not self.is_lost() and not self.is_won():
            print(f"\nLives left: {self.lives}")
            print("Word: " + " ".join(self.display_word))
            guess = self.timed_input("Enter a letter: ", self.time_limit)

            if not guess:
                print("Time is up! You lost a life.")
                self.lives -= 1
                continue

            guess = guess.lower()
            if len(guess) != 1 or not guess.isalpha():
                print("Please enter a single letter.")
                continue

            if guess in self.guessed_letters:
                print("You've already guessed that letter. -1 life")
                self.lives -= 1
                continue

            self.guessed_letters.add(guess)

            if guess in self.answer:
                self._update_display(guess)
                print(f"Correct! Letter '{guess}' is in the word.")
            else:
                self.lives -= 1
                print(f"Wrong! Letter '{guess}' is not in the word.")

        if self.is_won():
            print(f"\nCongratulations! You guessed the word: {self.answer}")
        else:
            print(f"\nGame Over! The correct answer was: {self.answer}")


if __name__ == "__main__":
    print("Choose game mode:")
    print("1. Basic (single word)")
    print("2. Intermediate (phrase)")
    USER_MODE = input("Enter 1 or 2: ").strip()
    USER_MODE = "intermediate" if USER_MODE == "2" else "basic"
    game_instance = HangmanGame(mode=USER_MODE,
                                time_limit=DEFAULT_TIME_LIMIT)
    game_instance.play()
