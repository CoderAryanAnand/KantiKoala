"""
Learning/Theory routes for the curriculum-based learning feature.
Allows users to browse and study theory content by year, subject, and topic.
Using Database models defined in kkoala.models.
"""
from flask import Blueprint, render_template, session, jsonify, abort, request, flash, redirect, url_for
import json
from io import BytesIO
from ..utils import login_required
from ..models import CurriculumSubject, CurriculumTopic, CurriculumSubTopic, Exercise, User
from ..extensions import db
from ..converters import docx_to_html, pdf_to_html, plastex_to_html
from ..parsers import parse_exercises_from_html, parse_exercises_from_latex
from ..consts import YEAR_SUBJECT_TEMPLATES

lernen_bp = Blueprint(
    "lernen", __name__, template_folder="../templates", static_folder="../static"
)


@lernen_bp.before_request
def restrict_lernen_access():
    """
    Restrict access to the Lernen blueprint to admins and teachers.
    """
    username = session.get("username")
    if not username:
        if request.path.startswith("/lernen/api"):
            return jsonify({"error": "Unauthorized"}), 401
        flash("Bitte loggen Sie sich ein, um auf den Lernbereich zuzugreifen.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=username).first()
    if not user or not (user.is_admin or user.is_teacher):
        if request.path.startswith("/lernen/api"):
            return jsonify({"error": "Forbidden"}), 403
        return redirect(url_for("main.index"))


@lernen_bp.route("/")
def lernen_index():
    """
    Main learning page - shows year selection.
    """
    years = [
        {"id": 1, "name": "1. Klasse", "description": "Grundlagenfächer und Einführung ins Gymnasium"},
        {"id": 2, "name": "2. Klasse", "description": "Vertiefung der Grundlagen"},
        {"id": 3, "name": "3. Klasse", "description": "Schwerpunktfächer und Spezialisierung"},
        {"id": 4, "name": "4. Klasse", "description": "Maturavorbereitung"}
    ]
    return render_template(
        "lernen.html",
        years=years,
        logged_in="username" in session
    )

@lernen_bp.route("/api/subjects/<int:year_id>")
def get_subjects(year_id):
    """
    API endpoint to get subjects for a specific year.
    Returns JSON list of subjects with their topics.
    """
    subjects = CurriculumSubject.query.filter_by(year=year_id).all()
    
    subjects_list = []
    
    for subj in subjects:
        topics_list = []
        for topic in subj.topics:
            subtopics_list = []
            for sub in topic.subtopics:
                subtopics_list.append({
                    "id": str(sub.id),
                    "name": sub.name,
                    "difficulty": sub.difficulty
                })
            topics_list.append({
                "id": str(topic.id),
                "name": topic.name,
                "subtopics": subtopics_list
            })
            
        subjects_list.append({
            "id": str(subj.id),
            "name": subj.name,
            "icon": subj.icon,
            "color": subj.color,
            "topics": topics_list
        })
    
    return jsonify(subjects_list)


@lernen_bp.route("/api/theory/<subtopic_id>")
def get_theory(subtopic_id):
    """
    API endpoint to get theory content for a specific subtopic.
    """
    try:
        sid = int(subtopic_id)
        subtopic = CurriculumSubTopic.query.get(sid)
    except ValueError:
        return jsonify({"error": "Invalid ID"}), 404
        
    if not subtopic:
        return jsonify({"error": "Not found"}), 404
    
    return jsonify({
        "title": subtopic.name,
        "subject": subtopic.topic.subject.name,
        "year": subtopic.topic.year,
        "difficulty": subtopic.difficulty,
        "estimated_time": subtopic.estimated_time,
        "content": {
            "introduction": "", 
            "sections": [
                {
                    "title": "Inhalt",
                    "content": subtopic.content_html or "Kein Inhalt verfügbar."
                }
            ],
            "key_points": [],
            "examples": [],
            "exercises": []
        }
    })

@lernen_bp.route("/<int:year_id>")
def lernen_year(year_id):
    if year_id < 1 or year_id > 4:
        abort(404)
        
    # Check if subjects exist for this year
    subjects_count = CurriculumSubject.query.filter_by(year=year_id).count()
    if subjects_count == 0:
        # Populate defaults
        default_names = YEAR_SUBJECT_TEMPLATES.get(year_id, [])
        for name in default_names:
            db.session.add(CurriculumSubject(name=name, year=year_id))
        if default_names:
            db.session.commit()

    years = [
        {"id": 1, "name": "1. Klasse", "description": "Grundlagenfächer"},
        {"id": 2, "name": "2. Klasse", "description": "Vertiefung"},
        {"id": 3, "name": "3. Klasse", "description": "Schwerpunktfächer"},
        {"id": 4, "name": "4. Klasse", "description": "Maturavorbereitung"}
    ]
    year_info = next((y for y in years if y["id"] == year_id), None)

    subjects = CurriculumSubject.query.filter_by(year=year_id).all()
    subjects_list = []
    
    for subj in subjects:
        subjects_list.append({
            "id": subj.id,
            "name": subj.name,
            "icon": subj.icon,
            "color": subj.color,
            "topics": subj.topics
        })

    return render_template(
        "lernen_year.html",
        year=year_info,
        subjects=subjects_list,
        logged_in="username" in session
    )

@lernen_bp.route("/<int:year_id>/<subject_id>")
def lernen_subject(year_id, subject_id):
    try:
        sid = int(subject_id)
        subject = CurriculumSubject.query.get(sid)
    except ValueError:
        # Legacy support for string IDs is deprecated.
        abort(404)
        
    if not subject:
        abort(404)

    # Ensure the subject belongs to the requested year
    if subject.year != year_id:
        return redirect(url_for('lernen.lernen_subject', year_id=subject.year, subject_id=subject.id))
        
    years = [
        {"id": 1, "name": "1. Klasse"},
        {"id": 2, "name": "2. Klasse"},
        {"id": 3, "name": "3. Klasse"},
        {"id": 4, "name": "4. Klasse"}
    ]
    year = next((y for y in years if y["id"] == year_id), None)
    
    # Fetch topics sorted by name
    topics = CurriculumTopic.query.filter_by(subject_id=subject.id).order_by(CurriculumTopic.name).all()
    
    subject_info = {
        "id": subject.id,
        "name": subject.name,
        "icon": subject.icon,
        "color": subject.color,
        "topics": []
    }
    
    for t in topics:
        # Sort subtopics by name or ID
        sorted_subtopics = sorted(t.subtopics, key=lambda x: x.name)
        subtopics = [{"id": str(s.id), "name": s.name, "difficulty": s.difficulty} for s in sorted_subtopics]
        
        subject_info["topics"].append({
            "id": str(t.id),
            "name": t.name,
            "subtopics": subtopics
        })

    return render_template(
        "lernen_subject.html",
        year=year,
        subject=subject_info,
        logged_in="username" in session
    )

@lernen_bp.route("/<int:year_id>/<subject_id>/<subtopic_id>")
def lernen_topic(year_id, subject_id, subtopic_id):
    try:
        stid = int(subtopic_id)
        subtopic = CurriculumSubTopic.query.get(stid)
    except ValueError:
        abort(404)
        
    if not subtopic:
        abort(404)
        
    content_data = {
        "introduction": "", 
        "sections": [
            {
                "title": "Lerninhalt",
                "content": subtopic.content_html or "Kein Inhalt verfügbar."
            }
        ],
        "key_points": [],
        "html_content": subtopic.content_html 
    }
    
    # Add exercises
    exercises_list = []
    if subtopic.exercises:
        for ex in subtopic.exercises:
            exercises_list.append({
                "type": ex.type,
                "question": ex.question,
                "answer": ex.correct_answer,
                "explanation": ex.explanation,
                "options": ex.options_list
            })
    content_data['exercises'] = exercises_list
    
    # Wrap in 'content' key to match template structure (content.content.sections)
    content = {
        "content": content_data 
    }
    
    topic_info = {
        "id": str(subtopic.id),
        "name": subtopic.name,
        "difficulty": subtopic.difficulty,
        "parent_topic": subtopic.topic.name
    }
    
    subject_db = subtopic.topic.subject
    subject_info = {
        "id": subject_db.id,
        "name": subject_db.name,
        "color": subject_db.color
    }
    
    years = [
        {"id": 1, "name": "1. Klasse"},
        {"id": 2, "name": "2. Klasse"},
        {"id": 3, "name": "3. Klasse"},
        {"id": 4, "name": "4. Klasse"}
    ]
    year = next((y for y in years if y["id"] == year_id), None)

    return render_template(
        "lernen_theory.html",
        year=year,
        subject=subject_info,
        topic=topic_info,
        content=content,
        logged_in="username" in session
    )

@lernen_bp.route("/manage", methods=["GET", "POST"])
@login_required
def manage(user):
    if not (user.is_teacher or user.is_admin):
        flash("Nur Lehrpersonen haben Zugriff auf diesen Bereich.", "error")
        return redirect(url_for("lernen.lernen_index"))

    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_subject":
            name = request.form.get("name")
            color = request.form.get("color")
            year = request.form.get("year")
            if name and year:
                db.session.add(CurriculumSubject(name=name, color=color, year=year))
                db.session.commit()
                flash("Fach erstellt", "success")
            elif not year:
                flash("Jahrgang fehlt", "error")

        elif action == "add_topic":
            name = request.form.get("name")
            subject_id = request.form.get("subject_id")
            # Year is now inherited from the subject
            
            if name and subject_id:
                subject = CurriculumSubject.query.get(subject_id)
                if subject:
                    db.session.add(CurriculumTopic(name=name, subject_id=subject_id, year=subject.year))
                    db.session.commit()
                    flash("Thema erstellt", "success")
                else:
                    flash("Fehler: Fach nicht gefunden", "error")

        elif action == "add_subtopic":
            name = request.form.get("name")
            topic_id = request.form.get("topic_id")
            difficulty = request.form.get("difficulty")
            
            content_html = ""
            file = request.files.get("docx_file")
            exercises_data = []
            
            if file:
                if file.filename.endswith('.docx'):
                    # Convert to HTML, then parse for exercises
                    raw_html = docx_to_html(file)
                    exercises_data, content_html = parse_exercises_from_html(raw_html)
                elif file.filename.endswith('.tex'):
                    # Read raw content to parse exercises
                    file.stream.seek(0)
                    raw_latex = file.stream.read().decode('utf-8', errors='ignore')
                    
                    exercises_data, cleaned_latex = parse_exercises_from_latex(raw_latex)
                    
                    # Create a stream from cleaned latex for conversion
                    cleaned_stream = BytesIO(cleaned_latex.encode('utf-8'))
                    content_html = plastex_to_html(cleaned_stream, file.filename)
                elif file.filename.endswith('.pdf'):
                    content_html = pdf_to_html(file)

            if name and topic_id:
                subtopic = CurriculumSubTopic(name=name, topic_id=topic_id, difficulty=difficulty, content_html=content_html)
                db.session.add(subtopic)
                db.session.commit()
                
                # Add extracted exercises
                for ex in exercises_data:
                    new_ex = Exercise(
                        subtopic_id=subtopic.id,
                        type=ex['type'],
                        question=ex['question'],
                        options=json.dumps(ex['options']) if ex['options'] else None,
                        correct_answer=ex['correct_answer'],
                        explanation=ex['explanation']
                    )
                    db.session.add(new_ex)

                if exercises_data:
                    db.session.commit()
                    flash(f"Lerninhalt und {len(exercises_data)} Übungen erstellt", "success")
                else:
                    flash("Lerninhalt erstellt", "success")
            else:
                 flash("Fehler: Name und Thema erforderlich", "error")

        elif action == "delete_subject":
            subject_id = request.form.get("subject_id")
            subject = CurriculumSubject.query.get(subject_id)
            if subject:
                db.session.delete(subject)
                db.session.commit()
                flash(f"Fach '{subject.name}' gelöscht", "success")

        elif action == "delete_topic":
            topic_id = request.form.get("topic_id")
            topic = CurriculumTopic.query.get(topic_id)
            if topic:
                db.session.delete(topic)
                db.session.commit()
                flash(f"Thema '{topic.name}' gelöscht", "success")

        elif action == "delete_subtopic":
            subtopic_id = request.form.get("subtopic_id")
            subtopic = CurriculumSubTopic.query.get(subtopic_id)
            if subtopic:
                db.session.delete(subtopic)
                db.session.commit()
                flash(f"Inhalt '{subtopic.name}' gelöscht", "success")

        elif action == "edit_subject":
            subject_id = request.form.get("subject_id")
            subject = CurriculumSubject.query.get(subject_id)
            if subject:
                if request.form.get("name"):
                    subject.name = request.form.get("name")
                if request.form.get("color"):
                    subject.color = request.form.get("color")
                db.session.commit()
                flash(f"Fach '{subject.name}' aktualisiert", "success")

        elif action == "edit_topic":
            topic_id = request.form.get("topic_id")
            topic = CurriculumTopic.query.get(topic_id)
            if topic:
                 if request.form.get("name"):
                    topic.name = request.form.get("name")
                 db.session.commit()
                 flash(f"Thema '{topic.name}' aktualisiert", "success")

        elif action == "edit_subtopic":
            subtopic_id = request.form.get("subtopic_id")
            subtopic = CurriculumSubTopic.query.get(subtopic_id)
            if subtopic:
                # Update metadata
                if request.form.get("name"):
                    subtopic.name = request.form.get("name")
                if request.form.get("difficulty"):
                    subtopic.difficulty = request.form.get("difficulty")
                
                # Update content file if provided
                file = request.files.get("docx_file")
                if file and file.filename:
                    exercises_data = []
                    
                    # Clear existing exercises when replacing content
                    for old_ex in subtopic.exercises:
                        db.session.delete(old_ex)

                    if file.filename.endswith('.docx'):
                        raw_html = docx_to_html(file)
                        exercises_data, subtopic.content_html = parse_exercises_from_html(raw_html)
                        flash(f"Inhalt und {len(exercises_data)} Übungen aktualisiert (Word)", "success")
                    elif file.filename.endswith('.tex'):
                        file.stream.seek(0)
                        raw_latex = file.stream.read().decode('utf-8', errors='ignore')
                        exercises_data, cleaned_latex = parse_exercises_from_latex(raw_latex)
                        
                        cleaned_stream = BytesIO(cleaned_latex.encode('utf-8'))
                        subtopic.content_html = plastex_to_html(cleaned_stream, file.filename)
                        flash(f"Inhalt und {len(exercises_data)} Übungen aktualisiert (LaTeX)", "success")
                    elif file.filename.endswith('.pdf'):
                        subtopic.content_html = pdf_to_html(file)
                        flash("Inhalt und Datei aktualisiert (PDF)", "success")
                    else:
                        flash("Ungültiges Dateiformat. Nur .docx, .tex oder .pdf", "error")
                    
                    # Add extracted exercises
                    for ex in exercises_data:
                        new_ex = Exercise(
                            subtopic_id=subtopic.id,
                            type=ex['type'],
                            question=ex['question'],
                            options=json.dumps(ex['options']) if ex['options'] else None,
                            correct_answer=ex['correct_answer'],
                            explanation=ex['explanation']
                        )
                        db.session.add(new_ex)
                else:
                    flash("Metadaten aktualisiert", "success")
                
                db.session.commit()
            else:
                flash("Fehler: Inhalt nicht gefunden", "error")
                
    subjects = CurriculumSubject.query.all()
    return render_template("lernen_manage.html", subjects=subjects)

