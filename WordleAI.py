from typing import List, Tuple, Optional, Any
from WordleHelper import WordleHelper
import random


class WordleAI:
    """
    AI agent that plays Wordle using various strategies
    """

    def __init__(self, word_list: List[str], strategy: str = "frequency"):
        """
        Initialize the AI with a word list and strategy

        Args:
            word_list: List of valid 5-letter words
            strategy: Strategy to use ('frequency', 'random', 'elimination', 'adaptive')
        """
        self.helper = WordleHelper(word_list)
        self.strategy = strategy
        self.guess_history = []
        self.feedback_history = []

        # Pre-compute best starting words
        self.best_starters = [word for word, _ in self.helper.get_recommended_starters(20)]

    def reset(self):
        """Reset the AI for a new game"""
        self.helper.reset()
        self.guess_history = []
        self.feedback_history = []

    def make_guess(self, attempt_number: int = 1) -> str:
        """
        Make a guess based on the current strategy

        Args:
            attempt_number: Current attempt number (1-6)

        Returns:
            The word to guess
        """
        if self.strategy == "random":
            return self._random_strategy()
        elif self.strategy == "frequency":
            return self._frequency_strategy(attempt_number)
        elif self.strategy == "elimination":
            return self._elimination_strategy(attempt_number)
        elif self.strategy == "adaptive":
            return self._adaptive_strategy(attempt_number)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def process_feedback(self, guess: str, feedback: List[Tuple[str, str]]):
        """
        Process feedback from a guess and update internal state

        Args:
            guess: The word that was guessed
            feedback: List of (letter, color) tuples
        """
        self.guess_history.append(guess)
        self.feedback_history.append(feedback)
        self.helper.filter_words(guess, feedback)

    def _random_strategy(self) -> str:
        """Randomly select from remaining possible words"""
        if not self.helper.possible_words:
            return random.choice(self.helper.all_words)
        return random.choice(self.helper.possible_words)

    def _frequency_strategy(self, attempt_number: int) -> str:
        """
        Use letter frequency to guide guessing

        On first guess: Use pre-computed best starter
        On subsequent guesses: Pick word with highest frequency score from remaining
        """
        if attempt_number == 1:
            # Use a good starting word
            return self.best_starters[0]

        # Use helper to find best word from remaining possibilities
        return self.helper.get_best_guess(use_remaining_only=True)

    def _elimination_strategy(self, attempt_number: int) -> str:
        """
        Focus on eliminating words quickly

        Uses all words (not just remaining) to maximize information gain
        """
        if attempt_number == 1:
            return self.best_starters[0]

        # Use all words for elimination, not just remaining
        return self.helper.get_best_guess(use_remaining_only=False)

    def _adaptive_strategy(self, attempt_number: int) -> str:
        """
        Adaptive strategy that changes based on game state

        - Early game: Use elimination strategy
        - Mid game: Switch to frequency when remaining words < 100
        - Late game: Pick from remaining words when < 10 left
        """
        remaining = len(self.helper.possible_words)

        if attempt_number == 1:
            # Good starting word
            return self.best_starters[0]
        elif remaining > 100:
            # Elimination mode - use any word for max information
            return self.helper.get_best_guess(use_remaining_only=False)
        elif remaining > 10:
            # Frequency mode - pick best from remaining
            return self.helper.get_best_guess(use_remaining_only=True)
        else:
            # Endgame - just pick from remaining
            if remaining > 0:
                return self.helper.possible_words[0]
            else:
                return random.choice(self.helper.all_words)

    def get_statistics(self) -> dict:
        """
        Get statistics about the current game state

        Returns:
            Dictionary with statistics
        """
        return {
            "attempts_made": len(self.guess_history),
            "remaining_words": len(self.helper.possible_words),
            "strategy": self.strategy,
            "guesses": self.guess_history,
        }

    def suggest_next_move(self) -> tuple[None, list[Any]] | tuple[Any | None, list[Any]]:
        """
        Suggest the next move and show top alternatives

        Returns:
            Tuple of (best_guess, top_5_alternatives)
        """
        if not self.helper.possible_words:
            return None, []

        # Get top scoring words
        scored = [(word, self.helper.score_word(word))
                  for word in self.helper.possible_words[:100]]  # Limit for performance
        scored.sort(key=lambda x: x[1], reverse=True)

        best = scored[0][0] if scored else None
        alternatives = [word for word, _ in scored[1:6]]

        return best, alternatives


class WordleTrainer:
    """
    Trainer class to run multiple games and collect statistics
    """

    def __init__(self, word_list: List[str]):
        """Initialize trainer with word list"""
        self.word_list = [word.upper() for word in word_list if len(word) == 5]
        self.results = []

    def train(self, ai: WordleAI, num_games: int, secret_words: List[str] = None) -> dict:
        """
        Train the AI by playing multiple games

        Args:
            ai: The AI agent to train
            num_games: Number of games to play
            secret_words: Optional list of secret words to use (for testing)

        Returns:
            Dictionary with training statistics
        """
        from wordle_copy import WordleGame

        wins = 0
        total_attempts = 0
        attempt_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        failures = 0

        for i in range(num_games):
            # Create a new game
            if secret_words and i < len(secret_words):
                # Use provided secret word for testing
                game = WordleGame(self.word_list)
                game.secret_word = secret_words[i].upper()
            else:
                game = WordleGame(self.word_list)

            ai.reset()

            # Play the game
            attempts = 0
            won = False

            while not game.game_over and attempts < 6:
                attempts += 1
                guess = ai.make_guess(attempts)
                success, feedback = game.make_guess(guess)

                if success:
                    ai.process_feedback(guess, feedback)
                    if game.won:
                        won = True
                        break
                else:
                    # Should not happen if AI is working correctly
                    print(f"Warning: Invalid guess {guess}")
                    break

            # Record results
            if won:
                wins += 1
                total_attempts += attempts
                attempt_distribution[attempts] += 1
            else:
                failures += 1

            self.results.append({
                "game": i + 1,
                "won": won,
                "attempts": attempts if won else 6,
                "secret_word": game.secret_word,
                "guesses": ai.guess_history.copy()
            })

        # Calculate statistics
        win_rate = (wins / num_games) * 100 if num_games > 0 else 0
        avg_attempts = total_attempts / wins if wins > 0 else 0

        stats = {
            "total_games": num_games,
            "wins": wins,
            "losses": failures,
            "win_rate": win_rate,
            "average_attempts": avg_attempts,
            "attempt_distribution": attempt_distribution,
            "results": self.results
        }

        return stats
