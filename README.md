# Bulls and Cows Telegram Bot

A Telegram bot implementation of the classic Bulls and Cows game, where two players try to guess each other's 4-digit numbers.

## Game Rules

1. Each player chooses a 4-digit number with unique digits
2. Players take turns guessing each other's numbers
3. For each guess, the player receives:
   - Bulls (🐂): Number of digits that are correct and in the right position
   - Cows (🐄): Number of digits that are correct but in the wrong position
4. The first player to guess the opponent's number wins
5. If both players guess correctly in the same round, it's a draw

## Scoring System

- Win: 3 points
- Draw: 1 point
- Loss: 0 points

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a file named `t.txt` in the project directory and add your Telegram bot token (obtained from @BotFather)

3. Run the bot:
```bash
python bot.py
```

## Features

- 🎮 Play against other players
- 📊 View leaderboard
- 👤 Set custom nickname
- 💾 Persistent score tracking
- 🏆 Match history

## Commands

- `/start` - Start the bot and show main menu
- Main menu options:
  - 🎮 Play Game - Start a new game
  - 📊 Leaderboard - View top players
  - ⚙️ Settings - Access settings menu
    - 👤 Set Nickname - Set your custom nickname
    - 🔙 Back to Main Menu - Return to main menu

## How to Play

1. Start the bot with `/start`
2. Click "🎮 Play Game" to start a new game
3. Wait for another player to join
4. When the game starts, choose your 4-digit number
5. Take turns guessing each other's numbers
6. The first player to guess correctly wins!

## Database

The bot uses SQLite to store:
- Player information (telegram_id, nickname, score)
- Match history (players, rounds, winner) 