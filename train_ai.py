#!/usr/bin/env python3
"""
Wordle AI Training Script
Train and evaluate different AI strategies for playing Wordle
"""

import sys
from typing import List
from WordleAI import WordleAI, WordleTrainer
from wordle_copy import WordleGame, load_words_from_file

# Try to import rich for better terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    from rich.panel import Panel
    from rich.layout import Layout
    from rich import box
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Install 'rich' for better visualization: pip install rich")


class TrainingUI:
    """UI handler for training visualization"""

    def __init__(self, use_rich: bool = True):
        """Initialize UI with or without rich library"""
        self.use_rich = use_rich and RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()

    def print_header(self, text: str):
        """Print a header"""
        if self.use_rich:
            self.console.print(f"\n[bold cyan]{text}[/bold cyan]")
        else:
            print(f"\n{'=' * 50}")
            print(text)
            print('=' * 50)

    def print_feedback_colored(self, guess: str, feedback: List):
        """Print a guess with colored feedback"""
        if self.use_rich:
            text = Text()
            for letter, color in feedback:
                if color == 'green':
                    text.append(f" {letter} ", style="bold white on green")
                elif color == 'yellow':
                    text.append(f" {letter} ", style="bold black on yellow")
                else:
                    text.append(f" {letter} ", style="bold white on rgb(120,120,120)")
            self.console.print(text)
        else:
            # Fallback to simple text
            display = ""
            for letter, color in feedback:
                if color == 'green':
                    display += f"[{letter}]"
                elif color == 'yellow':
                    display += f"({letter})"
                else:
                    display += f" {letter} "
            print(display)

    def show_game(self, game: WordleGame, ai: WordleAI, show_secret: bool = False):
        """Display current game state"""
        if show_secret:
            self.print_header(f"Game - Secret: {game.secret_word}")
        else:
            self.print_header("Game in Progress")

        for i, (guess, feedback) in enumerate(zip(ai.guess_history, ai.feedback_history)):
            print(f"Attempt {i + 1}: ", end="")
            self.print_feedback_colored(guess, feedback)

        remaining = len(ai.helper.possible_words)
        print(f"\nRemaining possible words: {remaining}")

    def show_statistics(self, stats: dict):
        """Display training statistics"""
        self.print_header("Training Results")

        if self.use_rich:
            # Create a nice table with rich
            table = Table(title="Statistics", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Total Games", str(stats['total_games']))
            table.add_row("Wins", str(stats['wins']))
            table.add_row("Losses", str(stats['losses']))
            table.add_row("Win Rate", f"{stats['win_rate']:.2f}%")
            table.add_row("Avg Attempts (when won)", f"{stats['average_attempts']:.2f}")

            self.console.print(table)

            # Attempt distribution
            dist_table = Table(title="Attempt Distribution", box=box.ROUNDED)
            dist_table.add_column("Attempts", style="cyan")
            dist_table.add_column("Count", style="magenta")
            dist_table.add_column("Percentage", style="yellow")

            for attempts in range(1, 7):
                count = stats['attempt_distribution'][attempts]
                pct = (count / stats['wins'] * 100) if stats['wins'] > 0 else 0
                dist_table.add_row(str(attempts), str(count), f"{pct:.1f}%")

            self.console.print(dist_table)
        else:
            # Simple text output
            print(f"Total Games: {stats['total_games']}")
            print(f"Wins: {stats['wins']}")
            print(f"Losses: {stats['losses']}")
            print(f"Win Rate: {stats['win_rate']:.2f}%")
            print(f"Avg Attempts: {stats['average_attempts']:.2f}")
            print("\nAttempt Distribution:")
            for attempts in range(1, 7):
                count = stats['attempt_distribution'][attempts]
                print(f"  {attempts} attempts: {count}")

    def show_progress(self, iterable, description: str):
        """Show progress bar"""
        if self.use_rich:
            return track(iterable, description=description)
        else:
            return iterable


def demo_single_game(word_list: List[str], strategy: str = "adaptive", show_steps: bool = True):
    """
    Run a single demo game with visualization
    """
    ui = TrainingUI()
    ui.print_header(f"Demo Game - Strategy: {strategy}")

    # Create game and AI
    game = WordleGame(word_list)
    ai = WordleAI(word_list, strategy=strategy)

    print(f"Secret word: {'???' if not show_steps else game.secret_word}")
    print("Starting game...\n")

    attempt = 0
    while not game.game_over and attempt < 6:
        attempt += 1

        # AI makes a guess
        guess = ai.make_guess(attempt)
        print(f"\nAttempt {attempt}: AI guesses '{guess}'")

        # Process the guess
        success, feedback = game.make_guess(guess)

        if success:
            # Show feedback
            ui.print_feedback_colored(guess, feedback)

            # Update AI with feedback
            ai.process_feedback(guess, feedback)

            # Show remaining possibilities
            remaining = len(ai.helper.possible_words)
            print(f"Remaining possible words: {remaining}")

            if show_steps and remaining <= 10:
                print(f"Possibilities: {', '.join(ai.helper.possible_words[:10])}")

            if game.won:
                print(f"\n✓ AI won in {attempt} attempts!")
                break
        else:
            print(f"Error: {feedback}")
            break

    if not game.won:
        print(f"\n✗ AI failed. The word was: {game.secret_word}")

    return game.won, attempt


def train_multiple_strategies(word_list: List[str], num_games: int = 100):
    """
    Train and compare multiple strategies
    """
    ui = TrainingUI()
    strategies = ["random", "frequency", "elimination", "adaptive"]

    ui.print_header("Training Multiple Strategies")
    print(f"Running {num_games} games per strategy...\n")

    results = {}

    for strategy in strategies:
        print(f"\nTraining '{strategy}' strategy...")

        ai = WordleAI(word_list, strategy=strategy)
        trainer = WordleTrainer(word_list)

        stats = trainer.train(ai, num_games)
        results[strategy] = stats

        print(f"  Win Rate: {stats['win_rate']:.2f}%")
        print(f"  Avg Attempts: {stats['average_attempts']:.2f}")

    # Show comparison
    ui.print_header("Strategy Comparison")

    if ui.use_rich:
        table = Table(title="Strategy Performance", box=box.ROUNDED)
        table.add_column("Strategy", style="cyan")
        table.add_column("Win Rate", style="magenta")
        table.add_column("Avg Attempts", style="yellow")
        table.add_column("Wins", style="green")
        table.add_column("Losses", style="red")

        for strategy in strategies:
            stats = results[strategy]
            table.add_row(
                strategy,
                f"{stats['win_rate']:.2f}%",
                f"{stats['average_attempts']:.2f}",
                str(stats['wins']),
                str(stats['losses'])
            )

        ui.console.print(table)
    else:
        print("\nStrategy | Win Rate | Avg Attempts | Wins | Losses")
        print("-" * 60)
        for strategy in strategies:
            stats = results[strategy]
            print(f"{strategy:12} | {stats['win_rate']:7.2f}% | {stats['average_attempts']:12.2f} | "
                  f"{stats['wins']:4} | {stats['losses']:6}")


def interactive_menu():
    """Interactive menu for training options"""
    print("\n" + "=" * 50)
    print("WORDLE AI TRAINER")
    print("=" * 50)
    print("\n1. Demo single game (watch AI play)")
    print("2. Train single strategy")
    print("3. Compare all strategies")
    print("4. Custom training")
    print("5. Exit")

    choice = input("\nSelect option (1-5): ").strip()
    return choice


def main():
    """Main entry point"""
    # Load word list
    word_list = load_words_from_file("word_list.txt")
    if word_list is None:
        print("Error: word_list.txt not found!")
        return

    print(f"Loaded {len(word_list)} words")

    while True:
        choice = interactive_menu()

        if choice == "1":
            # Demo single game
            strategy = input(
                "Choose strategy (random/frequency/elimination/adaptive) [adaptive]: ").strip() or "adaptive"
            show_steps = input("Show detailed steps? (y/n) [y]: ").strip().lower() != 'n'
            demo_single_game(word_list, strategy, show_steps)
            input("\nPress Enter to continue...")

        elif choice == "2":
            # Train single strategy
            strategy = input(
                "Choose strategy (random/frequency/elimination/adaptive) [adaptive]: ").strip() or "adaptive"
            num_games = int(input("Number of games [100]: ").strip() or "100")

            ui = TrainingUI()
            ai = WordleAI(word_list, strategy=strategy)
            trainer = WordleTrainer(word_list)

            print(f"\nTraining '{strategy}' strategy with {num_games} games...")
            stats = trainer.train(ai, num_games)

            ui.show_statistics(stats)
            input("\nPress Enter to continue...")

        elif choice == "3":
            # Compare strategies
            num_games = int(input("Number of games per strategy [100]: ").strip() or "100")
            train_multiple_strategies(word_list, num_games)
            input("\nPress Enter to continue...")

        elif choice == "4":
            # Custom training
            print("\nCustom training options:")
            strategy = input("Strategy: ").strip()
            num_games = int(input("Number of games: ").strip())

            ui = TrainingUI()
            ai = WordleAI(word_list, strategy=strategy)
            trainer = WordleTrainer(word_list)

            stats = trainer.train(ai, num_games)
            ui.show_statistics(stats)
            input("\nPress Enter to continue...")

        elif choice == "5":
            print("\nThanks for training!")
            break

        else:
            print("Invalid option!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted!")
        sys.exit(0)