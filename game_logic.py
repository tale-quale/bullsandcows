from typing import Tuple, Dict, Optional
import random

class Game:
    def __init__(self):
        self.active_games: Dict[int, Dict] = {}  # player_id -> game_data
        self.waiting_players: set[int] = set()

    def generate_number(self) -> str:
        """Generate a random 4-digit number with unique digits."""
        digits = list(range(10))
        random.shuffle(digits)
        return ''.join(map(str, digits[:4]))

    def validate_number(self, number: str) -> bool:
        """Validate if the number is a valid 4-digit number with unique digits."""
        return (len(number) == 4 and 
                number.isdigit() and 
                len(set(number)) == 4)

    def calculate_bulls_and_cows(self, secret: str, guess: str) -> Tuple[int, int]:
        """Calculate bulls and cows for a guess."""
        bulls = sum(1 for i in range(4) if secret[i] == guess[i])
        cows = sum(1 for digit in guess if digit in secret) - bulls
        return bulls, cows

    def start_game(self, player1_id: int, player2_id: int) -> None:
        """Start a new game between two players."""
        self.active_games[player1_id] = {
            'opponent': player2_id,
            'secret': self.generate_number(),
            'guesses': [],
            'round': 1
        }
        self.active_games[player2_id] = {
            'opponent': player1_id,
            'secret': self.generate_number(),
            'guesses': [],
            'round': 1
        }

    def make_guess(self, player_id: int, guess: str) -> Optional[Tuple[int, int]]:
        """Make a guess and return bulls and cows if valid."""
        if player_id not in self.active_games:
            return None
        
        game_data = self.active_games[player_id]
        if not self.validate_number(guess):
            return None

        bulls, cows = self.calculate_bulls_and_cows(game_data['secret'], guess)
        game_data['guesses'].append((guess, bulls, cows))
        return bulls, cows

    def check_winner(self, player_id: int) -> Optional[int]:
        """Check if there's a winner in the game."""
        if player_id not in self.active_games:
            return None

        game_data = self.active_games[player_id]
        opponent_id = game_data['opponent']
        opponent_data = self.active_games[opponent_id]

        # Check if both players have made their guesses in this round
        if len(game_data['guesses']) < game_data['round'] or len(opponent_data['guesses']) < opponent_data['round']:
            return None

        # Get the last guesses
        player_last_guess = game_data['guesses'][-1]
        opponent_last_guess = opponent_data['guesses'][-1]

        # Check for win conditions
        if player_last_guess[1] == 4 and opponent_last_guess[1] == 4:
            return -1  # Draw
        elif player_last_guess[1] == 4:
            return player_id
        elif opponent_last_guess[1] == 4:
            return opponent_id

        # Increment round if no winner
        game_data['round'] += 1
        opponent_data['round'] += 1
        return None

    def end_game(self, player1_id: int, player2_id: int) -> None:
        """End the game and clean up."""
        if player1_id in self.active_games:
            del self.active_games[player1_id]
        if player2_id in self.active_games:
            del self.active_games[player2_id]

    def add_to_waiting(self, player_id: int) -> None:
        """Add a player to the waiting list."""
        self.waiting_players.add(player_id)

    def remove_from_waiting(self, player_id: int) -> None:
        """Remove a player from the waiting list."""
        self.waiting_players.discard(player_id)

    def get_waiting_player(self) -> Optional[int]:
        """Get a waiting player if available."""
        return next(iter(self.waiting_players)) if self.waiting_players else None 