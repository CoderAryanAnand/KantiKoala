"""
Learning/Theory routes for the curriculum-based learning feature.
Allows users to browse and study theory content by year, subject, and topic.
Using Database models defined in kkoala.models.
"""
from flask import Blueprint, render_template, session, jsonify, abort, request, flash, redirect, url_for
from ..utils import login_required
from ..models import CurriculumSubject, CurriculumTopic, CurriculumSubTopic
from ..extensions import db
from ..converters import docx_to_html, pdf_to_html, plastex_to_html

lernen_bp = Blueprint(
    "lernen", __name__, template_folder="../templates", static_folder="../static"
)


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
    # Get all topics for this year
    topics = CurriculumTopic.query.filter_by(year=year_id).all()
    
    # Group topics by subject
    subjects_map = {}
    
    for topic in topics:
        subj = topic.subject
        if subj.id not in subjects_map:
            subjects_map[subj.id] = {
                "id": str(subj.id),
                "name": subj.name,
                "icon": subj.icon,
                "color": subj.color,
                "topics": []
            }
        
        # Subtopics for this topic
        subtopics_list = []
        for sub in topic.subtopics:
            subtopics_list.append({
                "id": str(sub.id),
                "name": sub.name,
                "difficulty": sub.difficulty
            })

        subjects_map[subj.id]["topics"].append({
            "id": str(topic.id),
            "name": topic.name,
            "subtopics": subtopics_list
        })
    
    return jsonify(list(subjects_map.values()))


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
        
    years = [
        {"id": 1, "name": "1. Klasse", "description": "Grundlagenfächer"},
        {"id": 2, "name": "2. Klasse", "description": "Vertiefung"},
        {"id": 3, "name": "3. Klasse", "description": "Schwerpunktfächer"},
        {"id": 4, "name": "4. Klasse", "description": "Maturavorbereitung"}
    ]
    year_info = next((y for y in years if y["id"] == year_id), None)

    topics = CurriculumTopic.query.filter_by(year=year_id).all()
    subjects_map = {}
    for topic in topics:
        if topic.subject.id not in subjects_map:
            subjects_map[topic.subject.id] = {
                "id": str(topic.subject.id), 
                "name": topic.subject.name,
                "icon": topic.subject.icon,
                "color": topic.subject.color,
                "topics": [] 
            }
            
        subjects_map[topic.subject.id]["topics"].append(topic)

    subjects_list = list(subjects_map.values())

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
        
    years = [
        {"id": 1, "name": "1. Klasse"},
        {"id": 2, "name": "2. Klasse"},
        {"id": 3, "name": "3. Klasse"},
        {"id": 4, "name": "4. Klasse"}
    ]
    year = next((y for y in years if y["id"] == year_id), None)
    
    topics = CurriculumTopic.query.filter_by(subject_id=subject.id, year=year_id).all()
    
    subject_info = {
        "id": subject.id,
        "name": subject.name,
        "icon": subject.icon,
        "color": subject.color,
        "topics": []
    }
    
    for t in topics:
        subtopics = [{"id": str(s.id), "name": s.name, "difficulty": s.difficulty} for s in t.subtopics]
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
            if name:
                db.session.add(CurriculumSubject(name=name, color=color))
                db.session.commit()
                flash("Fach erstellt", "success")

        elif action == "add_topic":
            name = request.form.get("name")
            subject_id = request.form.get("subject_id")
            year = request.form.get("year")
            if name and subject_id:
                db.session.add(CurriculumTopic(name=name, subject_id=subject_id, year=year))
                db.session.commit()
                flash("Thema erstellt", "success")

        elif action == "add_subtopic":
            name = request.form.get("name")
            topic_id = request.form.get("topic_id")
            difficulty = request.form.get("difficulty")
            
            content_html = ""
            file = request.files.get("docx_file")
            
            if file:
                if file.filename.endswith('.docx'):
                    content_html = docx_to_html(file)
                elif file.filename.endswith('.tex'):
                    content_html = plastex_to_html(file, file.filename)
                elif file.filename.endswith('.pdf'):
                    content_html = pdf_to_html(file)

            if name and topic_id:
                db.session.add(CurriculumSubTopic(name=name, topic_id=topic_id, difficulty=difficulty, content_html=content_html))
                db.session.commit()
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
                    if file.filename.endswith('.docx'):
                        subtopic.content_html = docx_to_html(file)
                        flash("Inhalt und Datei aktualisiert (Word)", "success")
                    elif file.filename.endswith('.tex'):
                        subtopic.content_html = plastex_to_html(file, file.filename)
                        flash("Inhalt und Datei aktualisiert (LaTeX)", "success")
                    elif file.filename.endswith('.pdf'):
                        subtopic.content_html = pdf_to_html(file)
                        flash("Inhalt und Datei aktualisiert (PDF)", "success")
                    else:
                        flash("Ungültiges Dateiformat. Nur .docx, .tex oder .pdf", "error")
                else:
                    flash("Metadaten aktualisiert", "success")
                
                db.session.commit()
            else:
                flash("Fehler: Inhalt nicht gefunden", "error")
                
    subjects = CurriculumSubject.query.all()
    return render_template("lernen_manage.html", subjects=subjects)

