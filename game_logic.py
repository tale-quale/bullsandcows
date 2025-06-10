from typing import Tuple, Dict, Optional
import random

class Game:
    def __init__(self):
        self.active_games: Dict[int, Dict] = {}  # player_id -> game_data
        self.waiting_players: set[int] = set()

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
            'secret': None,  # Will be set by player
            'guesses': [],
            'round': 1,
            'current_turn': player1_id  # First player starts
        }
        self.active_games[player2_id] = {
            'opponent': player1_id,
            'secret': None,  # Will be set by player
            'guesses': [],
            'round': 1,
            'current_turn': player1_id  # First player starts
        }

    def set_secret_number(self, player_id: int, number: str) -> bool:
        """Set the secret number for a player."""
        if player_id not in self.active_games:
            return False
        
        if not self.validate_number(number):
            return False

        self.active_games[player_id]['secret'] = number
        return True

    def is_player_turn(self, player_id: int) -> bool:
        """Check if it's the player's turn."""
        if player_id not in self.active_games:
            return False
        return self.active_games[player_id]['current_turn'] == player_id

    def make_guess(self, player_id: int, guess: str) -> Optional[Tuple[int, int]]:
        """Make a guess and return bulls and cows if valid."""
        if player_id not in self.active_games:
            return None
        
        game_data = self.active_games[player_id]
        
        # Check if it's player's turn
        if not self.is_player_turn(player_id):
            return None

        # Check if both players have set their secret numbers
        if game_data['secret'] is None or self.active_games[game_data['opponent']]['secret'] is None:
            return None

        if not self.validate_number(guess):
            return None

        # Calculate bulls and cows against opponent's secret number
        opponent_id = game_data['opponent']
        opponent_secret = self.active_games[opponent_id]['secret']
        bulls, cows = self.calculate_bulls_and_cows(opponent_secret, guess)
        
        game_data['guesses'].append((guess, bulls, cows))
        
        # Switch turns
        game_data['current_turn'] = game_data['opponent']
        self.active_games[game_data['opponent']]['current_turn'] = game_data['opponent']
        
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

    def get_game_state(self, player_id: int) -> Dict:
        """Get the current state of the game for a player."""
        if player_id not in self.active_games:
            return {}
        return self.active_games[player_id] 