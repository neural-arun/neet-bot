import sqlite3
import os
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), 'neet_bot.db')
_local = threading.local()

def get_conn():
    if not hasattr(_local, 'conn') or _local.conn is None:
        _local.conn = sqlite3.connect(DB_PATH)
        _local.conn.execute('PRAGMA journal_mode=WAL')
        _local.conn.row_factory = sqlite3.Row
    return _local.conn

def init_db():
    conn = get_conn()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chapter TEXT NOT NULL,
            total_q INTEGER NOT NULL,
            answered_q INTEGER DEFAULT 0,
            correct_q INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            q_index INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            user_answer TEXT,
            correct_answer TEXT NOT NULL,
            options_json TEXT,
            is_correct INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS analytics (
            key TEXT PRIMARY KEY,
            value INTEGER DEFAULT 0
        );
    ''')
    conn.commit()

def upsert_user(user_id, username):
    conn = get_conn()
    conn.execute(
        'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
        (user_id, username)
    )
    conn.commit()

def create_session(user_id, chapter, total_q):
    conn = get_conn()
    cur = conn.execute(
        'INSERT INTO sessions (user_id, chapter, total_q) VALUES (?, ?, ?)',
        (user_id, chapter, total_q)
    )
    conn.commit()
    return cur.lastrowid

def get_active_session(user_id):
    conn = get_conn()
    cur = conn.execute(
        'SELECT * FROM sessions WHERE user_id = ? AND status = ? ORDER BY id DESC LIMIT 1',
        (user_id, 'active')
    )
    return cur.fetchone()

def save_answer(session_id, q_index, question_text, user_answer, correct_answer, options_json, is_correct):
    conn = get_conn()
    conn.execute(
        '''INSERT OR REPLACE INTO answers
           (session_id, q_index, question_text, user_answer, correct_answer, options_json, is_correct)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (session_id, q_index, question_text, user_answer, correct_answer, options_json, is_correct)
    )
    conn.commit()

def get_answers(session_id):
    conn = get_conn()
    cur = conn.execute(
        'SELECT * FROM answers WHERE session_id = ? ORDER BY q_index',
        (session_id,)
    )
    return cur.fetchall()

def finish_session(session_id):
    conn = get_conn()
    conn.execute('UPDATE sessions SET status = ? WHERE id = ?', ('done', session_id))
    conn.commit()

def update_session_score(session_id, answered_q, correct_q):
    conn = get_conn()
    conn.execute(
        'UPDATE sessions SET answered_q = ?, correct_q = ? WHERE id = ?',
        (answered_q, correct_q, session_id)
    )
    conn.commit()

# ── Analytics Functions ──
def increment_stat(key_name):
    conn = get_conn()
    conn.execute(
        'INSERT INTO analytics (key, value) VALUES (?, 1) ON CONFLICT(key) DO UPDATE SET value = value + 1',
        (key_name,)
    )
    conn.commit()

def get_analytics_summary():
    conn = get_conn()
    
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    session_count = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]

    stats = {}
    rows = conn.execute('SELECT key, value FROM analytics').fetchall()
    for r in rows:
        stats[r['key']] = r['value']

    recent_users_cur = conn.execute('''
        SELECT u.user_id, u.username, u.created_at, COUNT(s.id) as session_count
        FROM users u
        LEFT JOIN sessions s ON u.user_id = s.user_id
        GROUP BY u.user_id
        ORDER BY u.created_at DESC
        LIMIT 20
    ''').fetchall()
    recent_users = [dict(r) for r in recent_users_cur]

    recent_sessions_cur = conn.execute('''
        SELECT s.id, COALESCE(u.username, CAST(s.user_id AS TEXT)) as username, s.chapter, s.total_q, s.correct_q, s.created_at
        FROM sessions s
        LEFT JOIN users u ON s.user_id = u.user_id
        ORDER BY s.created_at DESC
        LIMIT 15
    ''').fetchall()
    recent_sessions = [dict(r) for r in recent_sessions_cur]

    return {
        'telegram_users_count': user_count,
        'telegram_sessions_count': session_count,
        'site_visits': stats.get('site_visits', 0),
        'telegram_clicks': stats.get('telegram_clicks', 0),
        'web_tests_started': stats.get('web_tests_started', 0),
        'web_tests_completed': stats.get('web_tests_completed', 0),
        'recent_users': recent_users,
        'recent_sessions': recent_sessions
    }
