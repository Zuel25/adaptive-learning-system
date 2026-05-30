# AI Model for Adaptive Learning System

def determineLevel(score):
    """
    Determine student level based on pre-test score
    
    Args:
        score (int): Pre-test score (0-100)
    
    Returns:
        str: Level ('dasar', 'menengah', 'mahir')
    """
    if score < 50:
        return 'dasar'
    elif score < 75:
        return 'menengah'
    else:
        return 'mahir'


def generateAdaptiveContent(student_level, topic):
    """
    Generate adaptive learning content based on student level
    
    Args:
        student_level (str): Student's current level
        topic (str): Learning topic
    
    Returns:
        dict: Adaptive content
    """
    content_templates = {
        'dasar': {
            'complexity': 'simple',
            'examples': 3,
            'explanation_detail': 'detailed',
            'visual_aids': True
        },
        'menengah': {
            'complexity': 'moderate',
            'examples': 5,
            'explanation_detail': 'balanced',
            'visual_aids': True
        },
        'mahir': {
            'complexity': 'advanced',
            'examples': 7,
            'explanation_detail': 'concise',
            'visual_aids': False
        }
    }
    
    return content_templates.get(student_level, content_templates['dasar'])


def detectError(answer, correct_answer, topic):
    """
    Detect common errors and provide targeted feedback
    
    Args:
        answer: Student's answer
        correct_answer: Correct answer
        topic: Learning topic
    
    Returns:
        dict: Error information and feedback
    """
    common_errors = {
        'addition': {
            'carry_over': 'Pastikan Anda memperhitungkan angka yang dibawa ke kolom berikutnya',
            'alignment': 'Sejajarkan angka dengan benar sebelum menghitung',
            'place_value': 'Perhatikan nilai tempat (satuan, puluhan, ratusan)'
        },
        'subtraction': {
            'borrow': 'Anda perlu meminjam dari kolom berikutnya',
            'minuend_subtrahend': 'Pastikan bilangan yang dikurangi berada di atas',
            'negative_result': 'Hasil tidak boleh negatif dalam konteks ini'
        },
        'multiplication': {
            'missing_steps': 'Jangan lupa langkah perkalian bertingkat',
            'zeros': 'Jangan lupa menambahkan nol untuk perkalian puluhan',
            'alignment': 'Sejajarkan hasil perkalian dengan benar'
        },
        'division': {
            'remainder': 'Perhatikan sisa pembagian',
            'quotient': 'Hasil bagi mungkin kurang satu',
            'division_by_zero': 'Tidak bisa membagi dengan nol'
        }
    }
    
    # Simple error detection
    if answer == correct_answer:
        return {
            'is_correct': True,
            'feedback': 'Benar! Jawaban Anda sempurna.',
            'suggestions': []
        }
    else:
        return {
            'is_correct': False,
            'feedback': f'Jawaban Anda salah. Jawaban yang benar adalah {correct_answer}',
            'suggestions': common_errors.get(topic, {}).get('general', 'Coba kembali dengan lebih hati-hati')
        }


def calculateAdaptiveDifficulty(student_performance):
    """
    Calculate next difficulty level based on student performance
    
    Args:
        student_performance (dict): Performance metrics
    
    Returns:
        str: Difficulty adjustment ('increase', 'maintain', 'decrease')
    """
    recent_scores = student_performance.get('recent_scores', [])
    
    if not recent_scores:
        return 'maintain'
    
    avg_recent = sum(recent_scores[-5:]) / len(recent_scores[-5:])
    
    if avg_recent >= 80:
        return 'increase'
    elif avg_recent >= 50:
        return 'maintain'
    else:
        return 'decrease'


def getRecommendedNextTopic(current_topic, student_level):
    """
    Get recommended next topic based on current topic and level
    
    Args:
        current_topic (str): Current learning topic
        student_level (str): Student's level
    
    Returns:
        str: Recommended next topic
    """
    topic_sequences = {
        'dasar': [
            'Penjumlahan Dasar',
            'Pengurangan Dasar',
            'Perkalian Dasar',
            'Pembagian Dasar'
        ],
        'menengah': [
            'Penjumlahan Bersusun',
            'Pengurangan Bersusun',
            'Perkalian Bersusun',
            'Pembagian Bersusun'
        ],
        'mahir': [
            'Operasi Desimal',
            'Operasi Pecahan',
            'Operasi Campuran',
            'Soal Cerita Kompleks'
        ]
    }
    
    sequence = topic_sequences.get(student_level, [])
    if current_topic in sequence:
        idx = sequence.index(current_topic)
        if idx + 1 < len(sequence):
            return sequence[idx + 1]
    
    return sequence[0] if sequence else 'Penjumlahan Dasar'


def analyzeStudentProgress(student_data):
    """
    Analyze overall student progress and learning patterns
    
    Args:
        student_data (dict): Student's learning data
    
    Returns:
        dict: Progress analysis
    """
    completed_materials = student_data.get('completed_materials', [])
    scores = student_data.get('scores', [])
    time_spent = student_data.get('time_spent', [])
    
    if not scores:
        return {
            'overall_progress': 0,
            'learning_rate': 'N/A',
            'strength': 'Belum ada data',
            'weakness': 'Belum ada data',
            'recommendation': 'Mulai dengan latihan soal dasar'
        }
    
    avg_score = sum(scores) / len(scores)
    
    # Simple trend analysis
    if len(scores) >= 2:
        trend = scores[-1] - scores[0]
    else:
        trend = 0
    
    return {
        'overall_progress': len(completed_materials),
        'average_score': int(avg_score),
        'learning_rate': 'Cepat' if trend > 10 else 'Stabil' if trend >= -10 else 'Perlu Perbaikan',
        'strength': 'Topik dengan skor tertinggi',
        'weakness': 'Topik dengan skor terendah',
        'recommendation': 'Fokus pada topik yang masih lemah dan tingkatkan pemahaman'
    }