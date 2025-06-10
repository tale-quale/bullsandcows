import sqlite3
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_name: str = "game.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create players table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            telegram_id INTEGER PRIMARY KEY,
            nickname TEXT UNIQUE,
            score INTEGER DEFAULT 0
        )
        ''')

        # Create matches table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER,
            player2_id INTEGER,
            rounds INTEGER,
            winner_id INTEGER,
            FOREIGN KEY (player1_id) REFERENCES players (telegram_id),
            FOREIGN KEY (player2_id) REFERENCES players (telegram_id),
            FOREIGN KEY (winner_id) REFERENCES players (telegram_id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_player(self, telegram_id: int) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO players (telegram_id) VALUES (?)', (telegram_id,))
        conn.commit()
        conn.close()

    def set_nickname(self, telegram_id: int, nickname: str) -> bool:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE players SET nickname = ? WHERE telegram_id = ?', (nickname, telegram_id))
            conn.commit()
            success = cursor.rowcount > 0
        except sqlite3.IntegrityError:
            success = False
        conn.close()
        return success

    def get_nickname(self, telegram_id: int) -> Optional[str]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT nickname FROM players WHERE telegram_id = ?', (telegram_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def update_score(self, telegram_id: int, points: int) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE players SET score = score + ? WHERE telegram_id = ?', (points, telegram_id))
        conn.commit()
        conn.close()

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT COALESCE(nickname, CAST(telegram_id AS TEXT)), score 
        FROM players 
        ORDER BY score DESC 
        LIMIT 10
        ''')
        result = cursor.fetchall()
        conn.close()
        return result

    def add_match(self, player1_id: int, player2_id: int, rounds: int, winner_id: Optional[int] = None) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO matches (player1_id, player2_id, rounds, winner_id)
        VALUES (?, ?, ?, ?)
        ''', (player1_id, player2_id, rounds, winner_id))
        conn.commit()
        conn.close() 