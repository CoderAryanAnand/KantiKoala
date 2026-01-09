"""
Learning/Theory routes for the curriculum-based learning feature.
Allows users to browse and study theory content by year, subject, and topic.
Using Database models defined in kkoala.models.
"""
from flask import Blueprint, render_template, session, jsonify, abort, request, flash, redirect, url_for
import os
import mammoth
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexGroupNode, LatexCharsNode, LatexMathNode

from ..utils import login_required
from ..models import CurriculumSubject, CurriculumTopic, CurriculumSubTopic
from ..extensions import db

lernen_bp = Blueprint(
    "lernen", __name__, template_folder="../templates", static_folder="../static"
)



def latex_to_html(latex_content):
    """
    Parses LaTeX content and converts it to HTML using pylatexenc.
    Preserves math for KaTeX and basic structure (sections, lists).
    Simple conversion without TikZ support.
    """
    try:
        # Normalize
        if isinstance(latex_content, bytes):
            latex_content = latex_content.decode('utf-8', errors='ignore')
            
        # Extract body content if document environment exists
        if '\\begin{document}' in latex_content:
            latex_content = latex_content.split('\\begin{document}')[1]
            if '\\end{document}' in latex_content:
                latex_content = latex_content.split('\\end{document}')[0]
                
        walker = LatexWalker(latex_content)
        nodes, _, _ = walker.get_latex_nodes()
        
        def process_nodes(nodelist):
            res = ""
            for node in nodelist:
                if isinstance(node, LatexCharsNode):
                    res += node.chars
                    
                elif isinstance(node, LatexMacroNode):
                    if node.macroname in ['section', 'section*']:
                        title = process_nodes(node.nodeargs[0].nodelist) if node.nodeargs else ""
                        res += f"<h2>{title}</h2>"
                    elif node.macroname in ['subsection', 'subsection*']:
                        title = process_nodes(node.nodeargs[0].nodelist) if node.nodeargs else ""
                        res += f"<h3>{title}</h3>"
                    elif node.macroname in ['subsubsection', 'subsubsection*']:
                        title = process_nodes(node.nodeargs[0].nodelist) if node.nodeargs else ""
                        res += f"<h4>{title}</h4>"
                    elif node.macroname == 'textbf':
                        text = process_nodes(node.nodeargs[0].nodelist) if node.nodeargs else ""
                        res += f"<strong>{text}</strong>"
                    elif node.macroname == 'textit':
                        text = process_nodes(node.nodeargs[0].nodelist) if node.nodeargs else ""
                        res += f"<em>{text}</em>"
                    elif node.macroname == 'underline':
                        text = process_nodes(node.nodeargs[0].nodelist) if node.nodeargs else ""
                        res += f"<u>{text}</u>"
                    elif node.macroname == 'item':
                        pass 
                    else:
                        if node.nodeargs:
                            for arg in node.nodeargs:
                                if arg and arg.nodelist:
                                    res += process_nodes(arg.nodelist)
                                    
                elif isinstance(node, LatexEnvironmentNode):
                    if node.environmentname == 'itemize':
                        items_html = ""
                        curr_item = []
                        for child in node.nodelist:
                            if isinstance(child, LatexMacroNode) and child.macroname == 'item':
                                if curr_item:
                                    items_html += f"<li>{process_nodes(curr_item)}</li>"
                                curr_item = []
                            else:
                                curr_item.append(child)
                        if curr_item:
                             items_html += f"<li>{process_nodes(curr_item)}</li>"
                        res += f"<ul>{items_html}</ul>"
                        
                    elif node.environmentname == 'enumerate':
                        items_html = ""
                        curr_item = []
                        for child in node.nodelist:
                            if isinstance(child, LatexMacroNode) and child.macroname == 'item':
                                if curr_item:
                                    items_html += f"<li>{process_nodes(curr_item)}</li>"
                                curr_item = []
                            else:
                                curr_item.append(child)
                        if curr_item:
                             items_html += f"<li>{process_nodes(curr_item)}</li>"
                        res += f"<ol>{items_html}</ol>"
                        
                    elif node.environmentname in ['equation', 'align', 'gather', 'equation*', 'align*', 'gather*']:
                         content = node.latex_verbatim()
                         res += f"$${content}$$"
                    
                    elif node.environmentname == 'center':
                        content = process_nodes(node.nodelist)
                        res += f"<div style='text-align:center'>{content}</div>"
                    
                    # Ignore TikZ and other complex environments or treat as text if needed
                    elif node.environmentname in ['tikzpicture', 'axis']:
                        res += f"<div class='text-zinc-500 italic'>[Grafik nicht unterstützt]</div>"

                    else:
                        res += process_nodes(node.nodelist)
                        
                elif isinstance(node, LatexGroupNode):
                    res += process_nodes(node.nodelist)
                    
                elif isinstance(node, LatexMathNode):
                    math_content = node.latex_verbatim()
                    if math_content.startswith('$') and math_content.endswith('$'):
                        if math_content.startswith('$$'):
                            res += f"$${math_content[2:-2]}$$"
                        else:
                            res += f"${math_content[1:-1]}$"
                    elif math_content.startswith(r'\('):
                         res += f"${math_content[2:-2]}$"
                    elif math_content.startswith(r'\['):
                         res += f"$${math_content[2:-2]}$$"
                    else:
                        res += f"${math_content}$"
                        
            return res

        raw_html = process_nodes(nodes)
        
        # Post-processing paragraphs
        final_html = ""
        parts = raw_html.split('\n\n')
        for p in parts:
            p = p.strip()
            if not p: continue
            if any(p.startswith(tag) for tag in ['<h', '<ul', '<ol', '<div', '$$']):
                final_html += p + "\n"
            else:
                final_html += f"<p>{p}</p>\n"
                
        return final_html


    except Exception as e:
        print(f"Error converting latex: {e}")
        return "<p class='text-red-500'>Fehler bei der Konvertierung der LaTeX-Datei.</p>"


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
        # If legacy string IDs are used, try to find by name? Or abort.
        # Import script mapped name->ID.
        # But if the user clicks a link from OLD cache, it might involve strings like "mathematik_1".
        # We can implement a fallback lookup if needed, but better to break and fix.
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
                    result = mammoth.convert_to_html(file)
                    content_html = result.value
                elif file.filename.endswith('.tex'):
                    # Convert LaTeX to styled HTML using pylatexenc (Word-like look)
                    raw_content = file.read()
                    content_html = latex_to_html(raw_content)

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
                        result = mammoth.convert_to_html(file)
                        subtopic.content_html = result.value
                        flash("Inhalt und Datei aktualisiert", "success")
                    elif file.filename.endswith('.tex'):
                        raw_content = file.read()
                        subtopic.content_html = latex_to_html(raw_content)
                        flash("Inhalt und Datei aktualisiert", "success")
                    else:
                        flash("Ungültiges Dateiformat. Nur .docx oder .tex", "error")
                else:
                    flash("Metadaten aktualisiert", "success")
                
                db.session.commit()
            else:
                flash("Fehler: Inhalt nicht gefunden", "error")
                
    subjects = CurriculumSubject.query.all()
    return render_template("lernen_manage.html", subjects=subjects)

