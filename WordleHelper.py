from typing import List, Set, Tuple, Dict
from collections import Counter


class WordleHelper:
    """
    Helper class for filtering words based on Wordle feedback
    and providing strategic word selection
    """

    def __init__(self, word_list: List[str]):
        """Initialize with a list of valid words"""
        self.all_words = [word.upper() for word in word_list if len(word) == 5]
        self.possible_words = self.all_words.copy()

    def reset(self):
        """Reset the possible words to the full list"""
        self.possible_words = self.all_words.copy()

    def filter_words(self, guess: str, feedback: List[Tuple[str, str]]) -> List[str]:
        """
        Filter possible words based on the guess and feedback received

        Args:
            guess: The guessed word
            feedback: List of (letter, color) tuples where color is 'green', 'yellow', or 'gray'

        Returns:
            List of words that match the feedback constraints
        """
        guess = guess.upper()
        filtered = []

        # Extract constraints from feedback
        green_positions = {}  # position -> letter
        yellow_letters = set()  # letters that are in word but not in these positions
        yellow_not_positions = {}  # letter -> set of positions it can't be
        gray_letters = set()  # letters not in word

        for i, (letter, color) in enumerate(feedback):
            if color == 'green':
                green_positions[i] = letter
            elif color == 'yellow':
                yellow_letters.add(letter)
                if letter not in yellow_not_positions:
                    yellow_not_positions[letter] = set()
                yellow_not_positions[letter].add(i)
            elif color == 'gray':
                # Only mark as gray if it's not marked as yellow or green elsewhere
                if letter not in yellow_letters and letter not in green_positions.values():
                    gray_letters.add(letter)

        # Filter words
        for word in self.possible_words:
            valid = True

            # Check green positions
            for pos, letter in green_positions.items():
                if word[pos] != letter:
                    valid = False
                    break

            if not valid:
                continue

            # Check yellow letters (must be in word but not in specified positions)
            for letter in yellow_letters:
                if letter not in word:
                    valid = False
                    break
                # Check if letter is in any of the positions it shouldn't be
                if letter in yellow_not_positions:
                    for pos in yellow_not_positions[letter]:
                        if word[pos] == letter:
                            valid = False
                            break

            if not valid:
                continue

            # Check gray letters (must not be in word)
            for letter in gray_letters:
                if letter in word:
                    valid = False
                    break

            if valid:
                filtered.append(word)

        self.possible_words = filtered
        return filtered

    def get_letter_frequencies(self, words: List[str] = None) -> Dict[str, int]:
        """
        Get frequency of each letter across all possible words

        Args:
            words: List of words to analyze (defaults to current possible words)

        Returns:
            Dictionary mapping letter to frequency count
        """
        if words is None:
            words = self.possible_words

        freq = Counter()
        for word in words:
            # Count unique letters in each word
            freq.update(set(word))

        return dict(freq)

    def get_position_frequencies(self, words: List[str] = None) -> List[Dict[str, int]]:
        """
        Get frequency of each letter at each position

        Args:
            words: List of words to analyze (defaults to current possible words)

        Returns:
            List of 5 dictionaries, one for each position
        """
        if words is None:
            words = self.possible_words

        position_freq = [Counter() for _ in range(5)]
        for word in words:
            for i, letter in enumerate(word):
                position_freq[i][letter] += 1

        return [dict(pf) for pf in position_freq]

    def score_word(self, word: str, words: List[str] = None) -> float:
        """
        Score a word based on letter frequency
        Higher score = more common letters = better for elimination

        Args:
            word: Word to score
            words: List of words to base frequency on (defaults to current possible words)

        Returns:
            Score for the word
        """
        if words is None:
            words = self.possible_words

        word = word.upper()
        freq = self.get_letter_frequencies(words)

        # Score based on unique letters (avoid double letters for better elimination)
        score = sum(freq.get(letter, 0) for letter in set(word))

        return score

    def get_best_guess(self, use_remaining_only: bool = True) -> str:
        """
        Get the best guess based on letter frequency

        Args:
            use_remaining_only: If True, only consider words from possible_words
                              If False, consider all words for better elimination

        Returns:
            Best word to guess
        """
        if not self.possible_words:
            return None

        # If only one word left, return it
        if len(self.possible_words) == 1:
            return self.possible_words[0]

        # If few words left, just pick from remaining
        if len(self.possible_words) <= 2 or use_remaining_only:
            candidate_words = self.possible_words
        else:
            # Use all words for better elimination strategy
            candidate_words = self.all_words

        # Score all candidates
        scored_words = [(word, self.score_word(word)) for word in candidate_words]

        # Sort by score (descending) and return best
        scored_words.sort(key=lambda x: x[1], reverse=True)

        return scored_words[0][0]

    def get_recommended_starters(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get recommended starting words based on letter frequency

        Args:
            top_n: Number of top words to return

        Returns:
            List of (word, score) tuples
        """
        scored_words = [(word, self.score_word(word, self.all_words))
                        for word in self.all_words]
        scored_words.sort(key=lambda x: x[1], reverse=True)

        return scored_words[:top_n]
