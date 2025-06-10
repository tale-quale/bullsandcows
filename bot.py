import telebot
from telebot import types
import os
from database import Database
from game_logic import Game
from typing import Dict, Optional

# Initialize bot and database
with open('t.txt', 'r') as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)
db = Database()
game = Game()

# Store user states
user_states: Dict[int, str] = {}  # user_id -> state
nickname_inputs: Dict[int, str] = {}  # user_id -> nickname

def get_main_keyboard():
    """Create main menu keyboard."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🎮 Play Game"))
    keyboard.add(types.KeyboardButton("📊 Leaderboard"), types.KeyboardButton("⚙️ Settings"))
    return keyboard

def get_settings_keyboard():
    """Create settings menu keyboard."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("👤 Set Nickname"))
    keyboard.add(types.KeyboardButton("🔙 Back to Main Menu"))
    return keyboard

def get_player_display_name(user_id: int) -> str:
    """Get player's display name (nickname or user_id)."""
    nickname = db.get_nickname(user_id)
    return nickname if nickname else str(user_id)

@bot.message_handler(commands=['start'])
def start(message):
    """Handle /start command."""
    user_id = message.from_user.id
    db.add_player(user_id)
    user_states[user_id] = "main_menu"
    bot.send_message(
        message.chat.id,
        "Welcome to Bulls and Cows! 🎮\n\n"
        "Choose an option from the menu below:",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🎮 Play Game")
def play_game(message):
    """Handle play game button."""
    user_id = message.from_user.id
    if user_id in game.active_games:
        bot.send_message(message.chat.id, "You are already in a game!")
        return

    waiting_player = game.get_waiting_player()
    if waiting_player and waiting_player != user_id:
        # Start game with waiting player
        game.remove_from_waiting(waiting_player)
        game.start_game(waiting_player, user_id)
        
        # Notify both players
        waiting_name = get_player_display_name(waiting_player)
        current_name = get_player_display_name(user_id)
        
        bot.send_message(
            waiting_player,
            f"Game started! You are playing against {current_name}.\n"
            f"Round 1\n"
            f"Please choose your 4-digit number (all digits must be unique)."
        )
        bot.send_message(
            user_id,
            f"Game started! You are playing against {waiting_name}.\n"
            f"Round 1\n"
            f"Please choose your 4-digit number (all digits must be unique)."
        )
    else:
        # Add player to waiting list
        game.add_to_waiting(user_id)
        bot.send_message(message.chat.id, "Waiting for another player...")

@bot.message_handler(func=lambda message: message.text == "📊 Leaderboard")
def show_leaderboard(message):
    """Show the leaderboard."""
    leaderboard = db.get_leaderboard()
    if not leaderboard:
        bot.send_message(message.chat.id, "No games played yet!")
        return

    text = "🏆 Leaderboard 🏆\n\n"
    for i, (nickname, score) in enumerate(leaderboard, 1):
        text += f"{i}. {nickname}: {score} points\n"
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == "⚙️ Settings")
def settings(message):
    """Show settings menu."""
    user_id = message.from_user.id
    user_states[user_id] = "settings"
    bot.send_message(
        message.chat.id,
        "Settings Menu:",
        reply_markup=get_settings_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "👤 Set Nickname")
def set_nickname(message):
    """Handle set nickname button."""
    user_id = message.from_user.id
    user_states[user_id] = "waiting_nickname"
    bot.send_message(
        message.chat.id,
        "Please enter your nickname (you can only set it once):",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: message.text == "🔙 Back to Main Menu")
def back_to_main(message):
    """Return to main menu."""
    user_id = message.from_user.id
    user_states[user_id] = "main_menu"
    bot.send_message(
        message.chat.id,
        "Main Menu:",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_nickname")
def handle_nickname(message):
    """Handle nickname input."""
    user_id = message.from_user.id
    nickname = message.text.strip()
    
    if len(nickname) < 3 or len(nickname) > 20:
        bot.send_message(message.chat.id, "Nickname must be between 3 and 20 characters long.")
        return

    if db.set_nickname(user_id, nickname):
        bot.send_message(
            message.chat.id,
            f"Nickname set to: {nickname}",
            reply_markup=get_main_keyboard()
        )
        user_states[user_id] = "main_menu"
    else:
        bot.send_message(
            message.chat.id,
            "Failed to set nickname. It might be already taken or you already have one.",
            reply_markup=get_main_keyboard()
        )
        user_states[user_id] = "main_menu"

@bot.message_handler(func=lambda message: message.from_user.id in game.active_games)
def handle_game_input(message):
    """Handle game input (guesses and secret numbers)."""
    user_id = message.from_user.id
    game_data = game.active_games[user_id]
    
    if not game.validate_number(message.text):
        bot.send_message(message.chat.id, "Please enter a valid 4-digit number with unique digits.")
        return

    # If player hasn't set their secret number yet
    if game_data['secret'] is None:
        if game.set_secret_number(user_id, message.text):
            opponent_id = game_data['opponent']
            opponent_name = get_player_display_name(opponent_id)
            
            # Check if both players have set their numbers
            if game.active_games[opponent_id]['secret'] is not None:
                # Both numbers are set, start the game
                bot.send_message(
                    user_id,
                    f"Your secret number has been set. {opponent_name} has already set their number.\n"
                    f"Round 1\n"
                    f"It's your turn to guess!"
                )
                bot.send_message(
                    opponent_id,
                    f"Your opponent has set their number.\n"
                    f"Round 1\n"
                    f"It's your turn to guess!"
                )
            else:
                # Wait for opponent
                bot.send_message(
                    user_id,
                    f"Your secret number has been set. Waiting for {opponent_name} to set their number..."
                )
                bot.send_message(
                    opponent_id,
                    f"Your opponent has set their number. It's your turn to set your number."
                )
        else:
            bot.send_message(message.chat.id, "Invalid number. Please try again.")
        return

    # Handle guess
    if not game.is_player_turn(user_id):
        bot.send_message(message.chat.id, "It's not your turn yet. Please wait for your opponent.")
        return

    result = game.make_guess(user_id, message.text)
    if result is None:
        bot.send_message(message.chat.id, "Invalid input or not your turn. Please try again.")
        return

    bulls, cows = result
    opponent_id = game_data['opponent']
    opponent_name = get_player_display_name(opponent_id)
    current_round = game_data['round']
    
    # Notify both players about the guess
    bot.send_message(
        user_id,
        f"Round {current_round}\n"
        f"Your guess: {message.text}\n"
        f"Bulls: {bulls} 🐂\n"
        f"Cows: {cows} 🐄\n"
        f"Waiting for {opponent_name}'s guess..."
    )
    bot.send_message(
        opponent_id,
        f"Round {current_round}\n"
        f"Your opponent's guess: {message.text}\n"
        f"Bulls: {bulls} 🐂\n"
        f"Cows: {cows} 🐄\n"
        f"It's your turn to guess!"
    )

    # Check for winner
    winner = game.check_winner(user_id)
    if winner is not None:
        rounds = game_data['round']
        
        if winner == -1:  # Draw
            db.update_score(user_id, 1)
            db.update_score(opponent_id, 1)
            db.add_match(user_id, opponent_id, rounds)
            
            bot.send_message(user_id, "It's a draw! Both players get 1 point.")
            bot.send_message(opponent_id, "It's a draw! Both players get 1 point.")
        else:
            winner_id = winner
            loser_id = opponent_id if winner == user_id else user_id
            
            db.update_score(winner_id, 3)
            db.add_match(user_id, opponent_id, rounds, winner_id)
            
            bot.send_message(winner_id, "Congratulations! You won! +3 points")
            bot.send_message(loser_id, "Game over! Your opponent won.")
        
        game.end_game(user_id, opponent_id)
        
        # Return to main menu
        bot.send_message(
            user_id,
            "Game ended. Back to main menu:",
            reply_markup=get_main_keyboard()
        )
        bot.send_message(
            opponent_id,
            "Game ended. Back to main menu:",
            reply_markup=get_main_keyboard()
        )
        user_states[user_id] = "main_menu"
        user_states[opponent_id] = "main_menu"

if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling() 