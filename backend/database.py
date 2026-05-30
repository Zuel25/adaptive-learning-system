import sqlite3
from flask import g
from datetime import datetime
import json

# Database configuration
DATABASE = 'adaptive_learning.db'

def get_db():
    """
    Get database connection
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    """
    Close database connection
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    """
    Initialize database with tables and sample data
    """
    app.teardown_appcontext(close_db)
    
    with app.app_context():
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        # Create tables
        cursor.executescript('''
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Student profiles
            CREATE TABLE IF NOT EXISTS student_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL UNIQUE,
                level TEXT DEFAULT 'dasar',
                pretest_score INTEGER DEFAULT 0,
                pretest_completed BOOLEAN DEFAULT 0,
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users(id)
            );

            -- Materials
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                level TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Pre-test questions
            CREATE TABLE IF NOT EXISTS pretest_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Practice questions
            CREATE TABLE IF NOT EXISTS practice_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT,
                level TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (material_id) REFERENCES materials(id)
            );

            -- Practice results
            CREATE TABLE IF NOT EXISTS practice_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                score INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users(id),
                FOREIGN KEY (material_id) REFERENCES materials(id)
            );
        ''')

        # Check if data already exists
        cursor.execute('SELECT COUNT(*) as count FROM users')
        if cursor.fetchone()['count'] == 0:
            # Insert sample users
            from werkzeug.security import generate_password_hash
            
            cursor.execute('''
                INSERT INTO users (name, email, password, role) VALUES
                (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?)
            ''', (
                'Siswa Demo', 'student@example.com', generate_password_hash('student123'), 'student',
                'Guru Demo', 'teacher@example.com', generate_password_hash('teacher123'), 'teacher',
                'Ahmad Rifaldi', 'ahmad@example.com', generate_password_hash('password123'), 'student',
                'Siti Nurhaliza', 'siti@example.com', generate_password_hash('password123'), 'student'
            ))

            # Get student IDs
            cursor.execute('SELECT id FROM users WHERE role = "student" ORDER BY id LIMIT 4')
            student_ids = [row['id'] for row in cursor.fetchall()]

            # Insert student profiles
            for student_id in student_ids:
                cursor.execute('''
                    INSERT INTO student_profiles (student_id, level, progress) 
                    VALUES (?, ?, ?)
                ''', (student_id, 'dasar', 0))

            # Insert materials
            cursor.execute('''
                INSERT INTO materials (title, description, level, content) VALUES
                (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?),
                (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?)
            ''', (
                'Penjumlahan Dasar', 'Belajar konsep penjumlahan dasar 1-20', 'dasar', 'Konten penjumlahan dasar',
                'Pengurangan Dasar', 'Belajar konsep pengurangan dasar', 'dasar', 'Konten pengurangan dasar',
                'Perkalian Dasar', 'Belajar konsep perkalian dasar', 'dasar', 'Konten perkalian dasar',
                'Penjumlahan Bersusun', 'Penjumlahan dengan bilangan lebih besar', 'menengah', 'Konten penjumlahan bersusun',
                'Pembagian Dasar', 'Belajar konsep pembagian dasar', 'menengah', 'Konten pembagian dasar',
                'Operasi Desimal', 'Operasi dengan bilangan desimal', 'mahir', 'Konten operasi desimal'
            ))

            # Insert pretest questions
            pretest_questions = [
                ('Berapa hasil dari 2 + 3?', '["5", "4", "6", "3"]', '5', 'Penjumlahan sederhana: 2 + 3 = 5'),
                ('Berapa hasil dari 10 - 4?', '["6", "5", "7", "8"]', '6', 'Pengurangan: 10 - 4 = 6'),
                ('Berapa hasil dari 3 × 4?', '["12", "11", "13", "10"]', '12', 'Perkalian: 3 × 4 = 12'),
                ('Berapa hasil dari 20 ÷ 5?', '["4", "5", "3", "6"]', '4', 'Pembagian: 20 ÷ 5 = 4'),
                ('Berapa hasil dari 15 + 8?', '["23", "22", "24", "20"]', '23', 'Penjumlahan: 15 + 8 = 23'),
                ('Berapa hasil dari 50 - 15?', '["35", "34", "36", "30"]', '35', 'Pengurangan: 50 - 15 = 35'),
                ('Berapa hasil dari 6 × 7?', '["42", "41", "43", "40"]', '42', 'Perkalian: 6 × 7 = 42'),
                ('Berapa hasil dari 100 ÷ 10?', '["10", "9", "11", "8"]', '10', 'Pembagian: 100 ÷ 10 = 10'),
                ('Berapa hasil dari 25 + 30?', '["55", "54", "56", "50"]', '55', 'Penjumlahan: 25 + 30 = 55'),
                ('Berapa hasil dari 99 - 45?', '["54", "53", "55", "50"]', '54', 'Pengurangan: 99 - 45 = 54')
            ]

            for question, options, correct, explanation in pretest_questions:
                cursor.execute('''
                    INSERT INTO pretest_questions (question, options, correct_answer, explanation)
                    VALUES (?, ?, ?, ?)
                ''', (question, options, correct, explanation))

            # Insert practice questions
            practice_questions = [
                # Material 1 (Penjumlahan Dasar) - Dasar level
                (1, 'Berapa 1 + 1?', '["2", "1", "3", "0"]', '2', 'Penjumlahan paling dasar', 'dasar'),
                (1, 'Berapa 5 + 5?', '["10", "9", "11", "8"]', '10', 'Lima tambah lima sama dengan sepuluh', 'dasar'),
                (1, 'Berapa 3 + 2?', '["5", "4", "6", "3"]', '5', 'Tiga tambah dua sama dengan lima', 'dasar'),
                (1, 'Berapa 7 + 3?', '["10", "9", "11", "8"]', '10', 'Tujuh tambah tiga sama dengan sepuluh', 'dasar'),
                (1, 'Berapa 4 + 6?', '["10", "9", "11", "8"]', '10', 'Empat tambah enam sama dengan sepuluh', 'dasar'),

                # Material 1 - Menengah level
                (1, 'Berapa 25 + 18?', '["43", "42", "44", "40"]', '43', 'Dua puluh lima tambah delapan belas', 'menengah'),
                (1, 'Berapa 34 + 27?', '["61", "60", "62", "59"]', '61', 'Tiga puluh empat tambah dua puluh tujuh', 'menengah'),
                (1, 'Berapa 45 + 36?', '["81", "80", "82", "79"]', '81', 'Empat puluh lima tambah tiga puluh enam', 'menengah'),
                (1, 'Berapa 52 + 48?', '["100", "99", "101", "98"]', '100', 'Lima puluh dua tambah empat puluh delapan', 'menengah'),
                (1, 'Berapa 63 + 37?', '["100", "99", "101", "98"]', '100', 'Enam puluh tiga tambah tiga puluh tujuh', 'menengah'),

                # Material 2 (Pengurangan) - Dasar level
                (2, 'Berapa 5 - 2?', '["3", "2", "4", "1"]', '3', 'Lima kurang dua sama dengan tiga', 'dasar'),
                (2, 'Berapa 10 - 3?', '["7", "6", "8", "5"]', '7', 'Sepuluh kurang tiga sama dengan tujuh', 'dasar'),
                (2, 'Berapa 8 - 4?', '["4", "3", "5", "2"]', '4', 'Delapan kurang empat sama dengan empat', 'dasar'),
                (2, 'Berapa 9 - 5?', '["4", "3", "5", "2"]', '4', 'Sembilan kurang lima sama dengan empat', 'dasar'),
                (2, 'Berapa 6 - 3?', '["3", "2", "4", "1"]', '3', 'Enam kurang tiga sama dengan tiga', 'dasar')
            ]

            for material_id, question, options, correct, explanation, level in practice_questions:
                cursor.execute('''
                    INSERT INTO practice_questions (material_id, question, options, correct_answer, explanation, level)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (material_id, question, options, correct, explanation, level))

        db.commit()
        db.close()