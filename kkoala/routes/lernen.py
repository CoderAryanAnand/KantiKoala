"""
Learning/Theory routes for the curriculum-based learning feature.
Allows users to browse and study theory content by year, subject, and topic.
"""
from flask import Blueprint, render_template, session, jsonify, abort
import os
import json

from ..utils import login_required

lernen_bp = Blueprint(
    "lernen", __name__, template_folder="../templates", static_folder="../static"
)

# Load curriculum data
def load_curriculum():
    """Load the curriculum structure from JSON file."""
    curriculum_path = os.path.join(
        os.path.dirname(__file__), "..", "curriculum", "curriculum_data.json"
    )
    try:
        with open(curriculum_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"years": [], "subjects": {}}


def load_theory_content():
    """Load all theory content from JSON file."""
    content_path = os.path.join(
        os.path.dirname(__file__), "..", "curriculum", "theory_content.json"
    )
    try:
        with open(content_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


@lernen_bp.route("/")
def lernen_index():
    """
    Main learning page - shows year selection.
    """
    curriculum = load_curriculum()
    return render_template(
        "lernen.html",
        years=curriculum.get("years", []),
        logged_in="username" in session
    )


@lernen_bp.route("/api/subjects/<int:year_id>")
def get_subjects(year_id):
    """
    API endpoint to get subjects for a specific year.
    
    Args:
        year_id: The year (1-4)
    
    Returns:
        JSON list of subjects with their topics
    """
    curriculum = load_curriculum()
    subjects = curriculum.get("subjects", {}).get(str(year_id), [])
    return jsonify(subjects)


@lernen_bp.route("/api/theory/<topic_id>")
def get_theory(topic_id):
    """
    API endpoint to get theory content for a specific topic.
    
    Args:
        topic_id: The unique topic identifier
    
    Returns:
        JSON with the full theory content
    """
    theory = load_theory_content()
    content = theory.get(topic_id)
    
    if content:
        return jsonify(content)
    else:
        # Return a placeholder if content doesn't exist yet
        return jsonify({
            "title": topic_id.replace("_", " ").title(),
            "subject": "Unbekannt",
            "year": 1,
            "difficulty": "basic",
            "estimated_time": "30 Minuten",
            "content": {
                "introduction": "Dieser Inhalt wird noch erstellt. Schau bald wieder vorbei!",
                "sections": [
                    {
                        "title": "In Bearbeitung",
                        "content": "Die Theorie zu diesem Thema wird gerade von unserem Team erstellt. Wir arbeiten daran, dir bald hochwertige Lerninhalte zur Verfügung zu stellen.\n\nIn der Zwischenzeit kannst du:\n- Andere verfügbare Themen durchstöbern\n- Deine Notizen aus dem Unterricht nutzen\n- Bei Fragen deine Lehrperson kontaktieren"
                    }
                ],
                "key_points": ["Inhalt folgt"],
                "examples": [],
                "exercises": []
            }
        })


@lernen_bp.route("/<int:year_id>")
def lernen_year(year_id):
    """
    Learning page for a specific year - shows subject selection.
    """
    if year_id < 1 or year_id > 4:
        abort(404)
    
    curriculum = load_curriculum()
    years = curriculum.get("years", [])
    year = next((y for y in years if y["id"] == year_id), None)
    
    if not year:
        abort(404)
    
    subjects = curriculum.get("subjects", {}).get(str(year_id), [])
    
    return render_template(
        "lernen_year.html",
        year=year,
        subjects=subjects,
        logged_in="username" in session
    )


@lernen_bp.route("/<int:year_id>/<subject_id>")
def lernen_subject(year_id, subject_id):
    """
    Learning page for a specific subject - shows topic selection.
    """
    if year_id < 1 or year_id > 4:
        abort(404)
    
    curriculum = load_curriculum()
    subjects = curriculum.get("subjects", {}).get(str(year_id), [])
    subject = next((s for s in subjects if s["id"] == subject_id), None)
    
    if not subject:
        abort(404)
    
    years = curriculum.get("years", [])
    year = next((y for y in years if y["id"] == year_id), None)
    
    return render_template(
        "lernen_subject.html",
        year=year,
        subject=subject,
        logged_in="username" in session
    )


@lernen_bp.route("/<int:year_id>/<subject_id>/<topic_id>")
def lernen_topic(year_id, subject_id, topic_id):
    """
    Full theory page for a specific topic.
    """
    if year_id < 1 or year_id > 4:
        abort(404)
    
    curriculum = load_curriculum()
    subjects = curriculum.get("subjects", {}).get(str(year_id), [])
    subject = next((s for s in subjects if s["id"] == subject_id), None)
    
    if not subject:
        abort(404)
    
    # Find the topic in the subject's topics
    topic_info = None
    for topic_group in subject.get("topics", []):
        for subtopic in topic_group.get("subtopics", []):
            if subtopic["id"] == topic_id:
                topic_info = subtopic
                topic_info["parent_topic"] = topic_group["name"]
                break
        if topic_info:
            break
    
    if not topic_info:
        abort(404)
    
    # Load theory content
    theory = load_theory_content()
    content = theory.get(topic_id, {})
    
    years = curriculum.get("years", [])
    year = next((y for y in years if y["id"] == year_id), None)
    
    return render_template(
        "lernen_theory.html",
        year=year,
        subject=subject,
        topic=topic_info,
        content=content,
        logged_in="username" in session
    )
