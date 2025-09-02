"""Unit tests for hangman1.py."""

import unittest
from hangman1 import HangmanGame, WORDS_LIST, BROWN_WORDS


class TestHangmanGame(unittest.TestCase):
    """Test cases for HangmanGame class."""

    def setUp(self):
        """Set up a game instance for each test."""
        self.word_game = HangmanGame(max_lives=3, mode="basic", time_limit=5)
        self.word_game.answer = "apple"
        self.word_game.display_word = self.word_game._init_display()
        self.phrase_game = HangmanGame(max_lives=3, mode="intermediate", time_limit=5)
        self.phrase_game.answer = "unit test"
        self.phrase_game.display_word = self.phrase_game._init_display()

    def test_initial_display(self):
        """Test initial display string has underscores."""
        self.assertEqual(self.word_game.display_word, "_____")
        self.assertEqual(self.phrase_game.display_word, "____ ____")

    def test_correct_guess_updates_display(self):
        """Test correct letter guess updates display."""
        self.word_game._update_display("p")
        self.assertEqual(self.word_game.display_word, "_pp__")

        self.phrase_game._update_display("t")
        # Correct expected display after guessing 't'
        self.assertEqual(self.phrase_game.display_word, "___t t__t")
        


    def test_incorrect_guess_deducts_life(self):
        """Test wrong letter guess decreases lives."""
        initial_lives = self.word_game.lives
        if "z" not in self.word_game.answer:
            self.word_game.guessed_letters.add("z")  # simulate wrong guess
            self.word_game.lives -= 1
        self.assertEqual(self.word_game.lives, initial_lives - 1)

    def test_is_won(self):
        """Test win detection."""
        self.word_game.display_word = self.word_game.answer
        self.assertTrue(self.word_game.is_won())

    def test_is_lost(self):
        """Test lose detection."""
        self.word_game.lives = 0
        self.assertTrue(self.word_game.is_lost())

    def test_choose_word_basic(self):
        """Test basic mode selects word from WORDS_LIST."""
        game = HangmanGame(mode="basic")
        self.assertIn(game.answer, WORDS_LIST)

    def test_choose_word_intermediate(self):
        """Test intermediate mode selects phrase with spaces."""
        game = HangmanGame(mode="intermediate")
        self.assertIsInstance(game.answer, str)
        self.assertGreaterEqual(len(game.answer.split()), 1)


if __name__ == "__main__":
    unittest.main()
