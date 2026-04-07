from flask import Flask, jsonify, request, abort
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'courses.json'

# --- FONCTIONS D'AIDE (Helper Functions) ---

def load_courses():
    """Charge les cours depuis le fichier JSON ou crée une liste vide si le fichier n'existe pas."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_courses(courses):
    """Enregistre la liste des cours dans le fichier JSON."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=4)
    except IOError as e:
        print(f"Erreur d'écriture : {e}")

def get_next_id(courses):
    """Génère un ID incrémentiel simple."""
    if not courses:
        return 1
    return max(course['id'] for course in courses) + 1

# --- ROUTES API ---

@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    """Récupère tous les cours."""
    return jsonify(load_courses())

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Récupère un cours spécifique par son ID."""
    courses = load_courses()
    course = next((c for c in courses if c['id'] == course_id), None)
    if course is None:
        abort(404, description="Cours non trouvé.")
    return jsonify(course)

@app.route('/api/courses', methods=['POST'])
def create_course():
    """Ajoute un nouveau cours après validation."""
    if not request.json or not 'name' in request.json:
        abort(400, description="Le nom du cours est requis.")
    
    # Validation des statuts autorisés
    allowed_status = ["Non commencé", "En cours", "Terminé"]
    status = request.json.get('status', 'Non commencé')
    if status not in allowed_status:
        abort(400, description=f"Statut invalide. Choisissez parmi : {allowed_status}")

    courses = load_courses()
    new_course = {
        'id': get_next_id(courses),
        'name': request.json['name'],
        'description': request.json.get('description', ""),
        'target_date': request.json.get('target_date', ""),
        'status': status,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    courses.append(new_course)
    save_courses(courses)
    return jsonify(new_course), 201

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Met à jour les informations d'un cours existant."""
    courses = load_courses()
    course = next((c for c in courses if c['id'] == course_id), None)
    if course is None:
        abort(404, description="Cours non trouvé.")
    
    data = request.json
    course['name'] = data.get('name', course['name'])
    course['description'] = data.get('description', course['description'])
    course['target_date'] = data.get('target_date', course['target_date'])
    
    status = data.get('status', course['status'])
    if status in ["Non commencé", "En cours", "Terminé"]:
        course['status'] = status

    save_courses(courses)
    return jsonify(course)

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Supprime un cours."""
    courses = load_courses()
    new_courses = [c for c in courses if c['id'] != course_id]
    if len(new_courses) == len(courses):
        abort(404, description="Cours non trouvé.")
    save_courses(new_courses)
    return jsonify({'result': True}), 200

# --- BONUS : STATISTIQUES ---
@app.route('/api/courses/stats', methods=['GET'])
def get_stats():
    """Retourne les statistiques par statut."""
    courses = load_courses()
    stats = {
        "Total": len(courses),
        "Non commencé": len([c for c in courses if c['status'] == "Non commencé"]),
        "En cours": len([c for c in courses if c['status'] == "En cours"]),
        "Terminé": len([c for c in courses if c['status'] == "Terminé"])
    }
    return jsonify(stats)

if __name__ == '__main__':
    print("- CodeCraftHub API is starting...")
    app.run(debug=True, port=5000)