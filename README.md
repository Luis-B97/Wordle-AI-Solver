WordleHelper
An AI-powered Wordle solver and helper that uses multiple strategies to play and solve Wordle puzzles efficiently.
Features

Multiple AI Strategies: Random, Frequency-based, Elimination, and Adaptive approaches
Interactive Training: Train and compare different strategies
Game Simulation: Full Wordle game implementation for testing
Performance Analytics: Track win rates, attempt distributions, and strategy effectiveness
Rich Terminal UI: Beautiful visualizations with the rich library

Project Structure
WordleHelper/
├── WordleHelper.py      # Core word filtering and analysis logic
├── WordleAI.py          # AI agent with multiple strategies
├── wordle_copy.py       # Wordle game implementation
├── train_ai.py          # Training interface and comparison tools
├── word_list.txt        # Valid 5-letter word list
└── README.md           # This file
Installation

Clone the repository:

bashgit clone https://github.com/Luis-B97/WordleHelper.git
cd WordleHelper

Install dependencies (optional, for better visuals):

bashpip install rich
Usage
Interactive Training Menu
Run the main training script:
bashpython train_ai.py
This provides options to:

Watch the AI play a single game
Train a specific strategy
Compare all strategies
Run custom training scenarios

Using the AI in Code
pythonfrom WordleAI import WordleAI, WordleTrainer
from wordle_copy import load_words_from_file

# Load word list
word_list = load_words_from_file("word_list.txt")

# Create an AI with adaptive strategy
ai = WordleAI(word_list, strategy="adaptive")

# Make guesses and process feedback
guess = ai.make_guess(attempt_number=1)
# ... get feedback from game ...
ai.process_feedback(guess, feedback)
AI Strategies

Random: Randomly selects from remaining possible words
Frequency: Uses letter frequency analysis to pick optimal words
Elimination: Maximizes information gain to eliminate possibilities quickly
Adaptive: Switches strategies based on game state (best overall performance)

Training Results
The adaptive strategy typically achieves:

~95-98% win rate
Average of 3-4 attempts per win
Optimal performance across different word difficulties

How It Works
WordleHelper

Filters words based on green/yellow/gray feedback
Calculates letter frequencies and position frequencies
Scores words for strategic selection

WordleAI

Implements four different solving strategies
Maintains guess history and feedback
Adapts approach based on remaining possibilities

Training System

Simulates thousands of games
Tracks performance metrics
Compares strategy effectiveness

Example Output
WORDLE AI TRAINER
==================================================

Strategy Comparison
==================================================
Strategy     | Win Rate | Avg Attempts | Wins | Losses
------------------------------------------------------------
random       |   75.00% |         4.20 |   75 |     25
frequency    |   90.00% |         3.80 |   90 |     10
elimination  |   92.00% |         3.60 |   92 |      8
adaptive     |   96.00% |         3.40 |   96 |      4
Technologies Used

Python 3.x
Type hints for better code clarity
Rich library for terminal UI (optional)

Future Improvements

 Add entropy-based word selection
 Implement hard mode compliance
 Add web interface
 Export game histories
 Support for different word list sizes

License
See LICENSE file for details.
Contributing
Contributions welcome! Feel free to:

Report bugs
Suggest new strategies
Improve documentation
Add features

Author
Luis B
