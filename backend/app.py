import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from database import init_db, get_db
from ai_model import determineLevel, generateAdaptiveContent, detectError

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# CORS Configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

# Initialize database
init_db(app)

# ========================================
# AUTHENTICATION ROUTES
# ========================================

@app.route('/api/login', methods=['POST'])
def login():
    """
    Login endpoint for both students and teachers
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({'error': 'Email, password, dan role harus diisi'}), 400

    try:
        db = get_db()
        
        # Query user by email and role
        user = db.execute(
            'SELECT id, name, email, password, role FROM users WHERE email = ? AND role = ?',
            (email, role)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Email atau password salah'}), 401

        # Create JWT token
        access_token = create_access_token(
            identity=user['id'],
            additional_claims={'role': role}
        )

        return jsonify({
            'token': access_token,
            'user_id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan pada server'}), 500


@app.route('/api/register', methods=['POST'])
def register():
    """
    Register endpoint for new users
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if not name or not email or not password:
        return jsonify({'error': 'Nama, email, dan password harus diisi'}), 400

    try:
        db = get_db()
        
        # Check if email already exists
        existing_user = db.execute(
            'SELECT id FROM users WHERE email = ?',
            (email,)
        ).fetchone()

        if existing_user:
            return jsonify({'error': 'Email sudah terdaftar'}), 409

        # Hash password
        hashed_password = generate_password_hash(password)

        # Insert new user
        db.execute(
            'INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)',
            (name, email, hashed_password, role, datetime.now())
        )
        db.commit()

        return jsonify({'message': 'Registrasi berhasil'}), 201

    except Exception as e:
        print(f"Register error: {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan pada server'}), 500


# ========================================
# PRETEST ROUTES
# ========================================

@app.route('/api/pretest/questions', methods=['GET'])
def get_pretest_questions():
    """
    Get pre-test questions
    """
    try:
        db = get_db()
        questions = db.execute(
            'SELECT id, question, options, correct_answer, explanation FROM pretest_questions ORDER BY id'
        ).fetchall()

        result = []
        for q in questions:
            import json
            result.append({
                'id': q['id'],
                'question': q['question'],
                'options': json.loads(q['options']),
                'correct_answer': q['correct_answer'],
                'explanation': q['explanation']
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"Get pretest questions error: {str(e)}")
        return jsonify({'error': 'Gagal memuat pertanyaan pre-test'}), 500


@app.route('/api/pretest/submit', methods=['POST'])
@jwt_required()
def submit_pretest():
    """
    Submit pre-test answers and determine student level
    """
    data = request.get_json()
    student_id = data.get('student_id')
    answers = data.get('answers', {})

    try:
        db = get_db()
        
        # Get all pretest questions
        questions = db.execute(
            'SELECT id, correct_answer FROM pretest_questions'
        ).fetchall()

        # Calculate score
        correct_count = 0
        for i, question in enumerate(questions):
            user_answer = answers.get(str(i))
            if user_answer == question['correct_answer']:
                correct_count += 1

        score = int((correct_count / len(questions)) * 100) if questions else 0

        # Determine level based on score
        level = determineLevel(score)

        # Update student profile
        db.execute(
            'UPDATE student_profiles SET level = ?, pretest_score = ?, pretest_completed = ?, updated_at = ? WHERE student_id = ?',
            (level, score, 1, datetime.now(), student_id)
        )
        db.commit()

        return jsonify({
            'score': score,
            'level': level,
            'correct': correct_count,
            'total': len(questions)
        }), 200

    except Exception as e:
        print(f"Submit pretest error: {str(e)}")
        return jsonify({'error': 'Gagal mengirim jawaban pre-test'}), 500


# ========================================
# MATERIALS ROUTES
# ========================================

@app.route('/api/materials', methods=['GET'])
def get_materials():
    """
    Get learning materials based on student level
    """
    level = request.args.get('level', 'dasar')

    try:
        db = get_db()
        materials = db.execute(
            'SELECT id, title, description, level, content FROM materials WHERE level = ? ORDER BY id',
            (level,)
        ).fetchall()

        result = []
        for m in materials:
            result.append({
                'id': m['id'],
                'title': m['title'],
                'description': m['description'],
                'level': m['level'],
                'content': m['content']
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"Get materials error: {str(e)}")
        return jsonify({'error': 'Gagal memuat materi'}), 500


# ========================================
# PRACTICE ROUTES
# ========================================

@app.route('/api/practice/questions', methods=['GET'])
def get_practice_questions():
    """
    Get practice questions based on material and student level
    """
    material_id = request.args.get('material')
    student_id = request.args.get('student')

    try:
        db = get_db()
        
        # Get student profile for level
        student = db.execute(
            'SELECT level FROM student_profiles WHERE student_id = ?',
            (student_id,)
        ).fetchone()

        level = student['level'] if student else 'dasar'

        # Get practice questions
        questions = db.execute(
            'SELECT id, question, options, correct_answer, explanation FROM practice_questions WHERE material_id = ? AND level = ? ORDER BY id LIMIT 5',
            (material_id, level)
        ).fetchall()

        result = []
        for q in questions:
            import json
            result.append({
                'id': q['id'],
                'question': q['question'],
                'options': json.loads(q['options']),
                'correct_answer': q['correct_answer'],
                'explanation': q['explanation']
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"Get practice questions error: {str(e)}")
        return jsonify({'error': 'Gagal memuat soal latihan'}), 500


@app.route('/api/practice/submit', methods=['POST'])
@jwt_required()
def submit_practice():
    """
    Submit practice answers and track progress
    """
    data = request.get_json()
    student_id = data.get('student_id')
    material_id = data.get('material_id')
    answers = data.get('answers', {})
    correct_count = data.get('correct_count', 0)
    total_count = data.get('total_count', 0)

    try:
        db = get_db()
        
        # Calculate score
        score = int((correct_count / total_count) * 100) if total_count > 0 else 0

        # Save practice result
        db.execute(
            'INSERT INTO practice_results (student_id, material_id, score, completed_at) VALUES (?, ?, ?, ?)',
            (student_id, material_id, score, datetime.now())
        )

        # Update student progress
        total_materials = db.execute('SELECT COUNT(*) as count FROM materials').fetchone()['count']
        completed_materials = db.execute(
            'SELECT COUNT(DISTINCT material_id) as count FROM practice_results WHERE student_id = ?',
            (student_id,)
        ).fetchone()['count']

        progress = int((completed_materials / total_materials) * 100) if total_materials > 0 else 0
        
        db.execute(
            'UPDATE student_profiles SET progress = ?, updated_at = ? WHERE student_id = ?',
            (progress, datetime.now(), student_id)
        )
        db.commit()

        return jsonify({
            'score': score,
            'correct': correct_count,
            'total': total_count,
            'progress': progress
        }), 200

    except Exception as e:
        print(f"Submit practice error: {str(e)}")
        return jsonify({'error': 'Gagal mengirim jawaban latihan'}), 500


# ========================================
# STUDENT PROFILE ROUTES
# ========================================

@app.route('/api/student/<student_id>/profile', methods=['GET'])
@jwt_required()
def get_student_profile(student_id):
    """
    Get student profile and progress
    """
    try:
        db = get_db()
        
        # Get user info
        user = db.execute(
            'SELECT id, name, email FROM users WHERE id = ?',
            (student_id,)
        ).fetchone()

        # Get student profile
        profile = db.execute(
            'SELECT level, pretest_score, progress FROM student_profiles WHERE student_id = ?',
            (student_id,)
        ).fetchone()

        if not user:
            return jsonify({'error': 'Siswa tidak ditemukan'}), 404

        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'level': profile['level'] if profile else 'dasar',
            'score': profile['pretest_score'] if profile else 0,
            'progress': profile['progress'] if profile else 0
        }), 200

    except Exception as e:
        print(f"Get student profile error: {str(e)}")
        return jsonify({'error': 'Gagal memuat profil siswa'}), 500


# ========================================
# TEACHER DASHBOARD ROUTES
# ========================================

@app.route('/api/teacher/<teacher_id>/dashboard', methods=['GET'])
@jwt_required()
def get_teacher_dashboard(teacher_id):
    """
    Get teacher dashboard data
    """
    try:
        db = get_db()
        
        # Get teacher info
        teacher = db.execute(
            'SELECT name FROM users WHERE id = ?',
            (teacher_id,)
        ).fetchone()

        # Get statistics
        total_students = db.execute('SELECT COUNT(*) as count FROM student_profiles').fetchone()['count']
        pretest_done = db.execute('SELECT COUNT(*) as count FROM student_profiles WHERE pretest_completed = 1').fetchone()['count']
        
        avg_score_result = db.execute('SELECT AVG(pretest_score) as avg FROM student_profiles WHERE pretest_completed = 1').fetchone()
        avg_score = int(avg_score_result['avg']) if avg_score_result['avg'] else 0
        
        avg_progress_result = db.execute('SELECT AVG(progress) as avg FROM student_profiles').fetchone()
        avg_progress = int(avg_progress_result['avg']) if avg_progress_result['avg'] else 0

        return jsonify({
            'teacher_name': teacher['name'] if teacher else 'Guru',
            'total_students': total_students,
            'pretest_done': pretest_done,
            'avg_score': avg_score,
            'avg_progress': avg_progress
        }), 200

    except Exception as e:
        print(f"Get teacher dashboard error: {str(e)}")
        return jsonify({'error': 'Gagal memuat dashboard guru'}), 500


@app.route('/api/students', methods=['GET'])
def get_all_students():
    """
    Get all students with their profiles
    """
    try:
        db = get_db()
        
        students = db.execute(
            '''SELECT u.id, u.name, u.email, sp.level, sp.pretest_score, sp.progress, sp.pretest_completed
               FROM users u
               LEFT JOIN student_profiles sp ON u.id = sp.student_id
               WHERE u.role = 'student'
               ORDER BY u.name'''
        ).fetchall()

        result = []
        for s in students:
            status = 'belum_pretest' if not s['pretest_completed'] else 'learning'
            result.append({
                'id': s['id'],
                'name': s['name'],
                'email': s['email'],
                'level': s['level'] or 'belum_ditentukan',
                'score': s['pretest_score'] or 0,
                'progress': s['progress'] or 0,
                'status': status
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"Get all students error: {str(e)}")
        return jsonify({'error': 'Gagal memuat data siswa'}), 500


# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ========================================
# HEALTH CHECK
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)