# Import Flask modules for routing, session management, and request/response handling
from flask import Blueprint, session, current_app, jsonify, request
from datetime import datetime
import os

# Import application models and utilities
from ..models import Subject, Grade, User, Semester
from ..utils import login_required, csrf_protect
from ..extensions import db, limiter

# Define the blueprint for grades-related API routes
grades_bp = Blueprint(
    "grades", __name__, template_folder="../templates", static_folder="../static"
)

# Apply rate limit to all grades API routes (60 requests per minute)
@grades_bp.before_request
@limiter.limit("60 per minute")
def limit_grades_api():
    pass


# --- Constants for default semester/subject setup ---
# Templates available for users to import when creating a semester
SEMESTER_TEMPLATES = [
    {
        "id": 1,
        "name": "1. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Wirtschaft und Recht", "Geschichte"]
    },
    {
        "id": 2,
        "name": "2. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Wirtschaft und Recht", "Geschichte"]
    },
    {
        "id": 3,
        "name": "3. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Wirtschaft und Recht", "Geschichte"]
    },
    {
        "id": 4,
        "name": "4. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Wirtschaft und Recht", "Geschichte"]
    },
    {
        "id": 5,
        "name": "5. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Sport", "Englisch", "Französisch", "Geschichte"]
    },
    {
        "id": 6,
        "name": "6. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Sport", "Englisch", "Französisch", "Geschichte"]
    },
    {
        "id": 7,
        "name": "7. Semester",
        "subjects": ["Deutsch", "Mathematik", "Sport", "Physik", "Englisch", "Französisch", "Geschichte"]
    },
    {
        "id": 8,
        "name": "8. Semester",
        "subjects": ["Deutsch", "Mathematik", "Sport", "Physik", "Englisch", "Französisch", "Geschichte"]
    }
]


# --- Helper Functions for Calculations ---

def round_to_half(grade):
    """Round a grade to the nearest 0.5."""
    return round(grade * 2) / 2


def calculate_plus_points(rounded_grade):
    """Calculate plus points based on rounded grade (Swiss grading system)."""
    if rounded_grade >= 4.0:
        return rounded_grade - 4.0
    else:
        return 2 * (rounded_grade - 4.0)


def calculate_subject_average(subject):
    """
    Calculate the weighted average for a subject.
    
    Returns:
        dict: Contains 'average' (float or None if no grades) and 'has_grades' (bool)
    """
    total_weighted = 0.0
    total_weight = 0.0
    
    for grade in subject.grades:
        if grade.counts:
            total_weighted += grade.value * grade.weight
            total_weight += grade.weight
    
    if total_weight > 0:
        return {
            "average": round(total_weighted / total_weight, 2),
            "has_grades": True
        }
    return {"average": None, "has_grades": False}


def calculate_semester_average(semester):
    """
    Calculate the average and plus points for a semester.
    
    Returns:
        dict: Contains 'average', 'plus_points', and 'subject_count'
    """
    total_avg = 0.0
    subject_count = 0
    total_plus_points = 0.0
    
    for subject in semester.subjects:
        if subject.counts_towards_average:
            subj_calc = calculate_subject_average(subject)
            if subj_calc["has_grades"] and subj_calc["average"] is not None:
                avg_value = subj_calc["average"]
                total_avg += avg_value
                subject_count += 1
                total_plus_points += calculate_plus_points(round_to_half(avg_value))
    
    return {
        "average": round(total_avg / subject_count, 2) if subject_count > 0 else 0,
        "plus_points": round(total_plus_points, 1),
        "subject_count": subject_count
    }


def calculate_dream_grade(subject, wished_avg, next_weight):
    """
    Calculate the grade needed to achieve a desired average.
    
    Args:
        subject: Subject model instance
        wished_avg: Target average (1.0 - 6.0)
        next_weight: Weight of the next grade
    
    Returns:
        dict: Contains 'needed_grade', 'possible' (bool), 'message'
    """
    current_total = 0.0
    current_weight_sum = 0.0
    
    for grade in subject.grades:
        if grade.counts:
            current_total += grade.value * grade.weight
            current_weight_sum += grade.weight
    
    needed_grade = ((wished_avg * (current_weight_sum + next_weight)) - current_total) / next_weight
    
    result = {
        "needed_grade": round(needed_grade, 2),
        "current_total": current_total,
        "current_weight_sum": current_weight_sum
    }
    
    if needed_grade > 6:
        result["possible"] = False
        result["message"] = "Unmöglich"
    elif needed_grade < 1:
        result["possible"] = True
        result["message"] = "Jede Note"
    else:
        result["possible"] = True
        result["message"] = None
    
    return result


def serialize_semester(semester):
    """Serialize a semester with all its subjects, grades, and calculated averages."""
    sem_calc = calculate_semester_average(semester)
    
    subjects_data = []
    # Sort subjects by display_order to maintain user-defined order
    sorted_subjects = sorted(semester.subjects, key=lambda s: s.display_order)
    for subject in sorted_subjects:
        subj_calc = calculate_subject_average(subject)
        subjects_data.append({
            "id": subject.id,
            "name": subject.name,
            "counts_average": subject.counts_towards_average,
            "display_order": subject.display_order,
            "average": subj_calc["average"],
            "has_grades": subj_calc["has_grades"],
            "grades": [
                {
                    "id": grade.id,
                    "name": grade.name,
                    "value": grade.value,
                    "weight": grade.weight,
                    "counts": grade.counts,
                }
                for grade in subject.grades
            ]
        })
    
    return {
        "id": semester.id,
        "name": semester.name,
        "is_current": semester.is_current,
        "subjects": subjects_data,
        "average": sem_calc["average"],
        "plus_points": sem_calc["plus_points"],
        "subject_count": sem_calc["subject_count"]
    }


# --- API Endpoints ---

@grades_bp.route("/", methods=["GET"])
@login_required
def get_all_semesters(user):
    """
    Get all semesters with subjects, grades, and calculated averages.
    Current semester is sorted first, then by ID descending (newest first).
    
    Returns:
        JSON: List of serialized semesters with all data and calculations
    """
    semesters = Semester.query.filter_by(user_id=user.id).order_by(
        Semester.is_current.desc(),  # Current semester first
        Semester.id.desc()  # Then newest first
    ).all()
    return jsonify([serialize_semester(sem) for sem in semesters])


@grades_bp.route("/current", methods=["GET"])
@login_required
def get_current_semester(user):
    """
    Get the current semester with subjects, grades, and calculated averages.
    Used by dashboard to display current semester grades.
    
    Returns:
        JSON: Serialized current semester, or null if none set
    """
    semester = Semester.query.filter_by(user_id=user.id, is_current=True).first()
    if not semester:
        return jsonify(None)
    return jsonify(serialize_semester(semester))


@grades_bp.route("/constants", methods=["GET"])
@login_required
def get_constants(user):
    """
    Get semester templates for client-side use.
    
    Returns:
        JSON: List of available semester templates with subjects
    """
    return jsonify({
        "templates": SEMESTER_TEMPLATES
    })


# --- Semester CRUD ---

@grades_bp.route("/semester", methods=["POST"])
@csrf_protect
@login_required
def create_semester(user):
    """
    Create a new semester with optional template subjects.
    No limit on number of semesters a user can create.
    
    Payload:
        {
            "name": "Mein Semester",  // Required: user-defined name
            "template_id": 1,         // Optional: template ID to import subjects from
            "set_as_current": false   // Optional: set as current semester
        }
    
    Returns:
        JSON: The created semester with all data
    """
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "").strip()
    template_id = payload.get("template_id")
    set_as_current = payload.get("set_as_current", False)
    
    if not name or not isinstance(name, str) or len(name) > 100:
        return jsonify({"error": "Semester name is required (max 100 characters)"}), 400
    
    try:
        # If setting as current, unset any existing current semester
        if set_as_current:
            Semester.query.filter_by(user_id=user.id, is_current=True).update({"is_current": False})
        
        new_semester = Semester(user_id=user.id, name=name, is_current=bool(set_as_current))
        db.session.add(new_semester)
        db.session.flush()
        
        # Add subjects from template if template_id is provided
        if template_id is not None:
            template = next((t for t in SEMESTER_TEMPLATES if t["id"] == template_id), None)
            if template:
                for subj_name in template["subjects"]:
                    counts = subj_name.lower() != "sport"
                    new_subject = Subject(
                        semester_id=new_semester.id,
                        name=subj_name,
                        counts_towards_average=counts
                    )
                    db.session.add(new_subject)
        
        db.session.commit()
        return jsonify(serialize_semester(new_semester)), 201
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Failed to create semester")
        return jsonify({"error": "Failed to create semester"}), 500


@grades_bp.route("/semester/<int:semester_id>", methods=["PUT"])
@csrf_protect
@login_required
def update_semester(user, semester_id):
    """
    Update a semester's name and/or current status.
    
    Payload:
        { 
            "name": "New Semester Name",
            "is_current": true  // Optional: set as current semester
        }
    
    Returns:
        JSON: Updated semester data
    """
    semester = Semester.query.filter_by(id=semester_id, user_id=user.id).first()
    if not semester:
        return jsonify({"error": "Semester not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    is_current = payload.get("is_current")
    
    if name is not None:
        if not isinstance(name, str) or len(name) > 100:
            return jsonify({"error": "Invalid semester name"}), 400
        semester.name = name
    
    if is_current is not None:
        if is_current:
            # Unset any existing current semester for this user
            Semester.query.filter_by(user_id=user.id, is_current=True).update({"is_current": False})
            semester.is_current = True
        else:
            semester.is_current = False
    
    try:
        db.session.commit()
        return jsonify(serialize_semester(semester))
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update semester"}), 500


@grades_bp.route("/semester/<int:semester_id>/set-current", methods=["POST"])
@csrf_protect
@login_required
def set_current_semester(user, semester_id):
    """
    Set a semester as the current semester.
    Only one semester can be current at a time.
    
    Returns:
        JSON: Updated semester data
    """
    semester = Semester.query.filter_by(id=semester_id, user_id=user.id).first()
    if not semester:
        return jsonify({"error": "Semester not found"}), 404
    
    try:
        # Unset any existing current semester
        Semester.query.filter_by(user_id=user.id, is_current=True).update({"is_current": False})
        # Set the new current semester
        semester.is_current = True
        db.session.commit()
        return jsonify(serialize_semester(semester))
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to set current semester"}), 500


@grades_bp.route("/semester/<int:semester_id>", methods=["DELETE"])
@csrf_protect
@login_required
def delete_semester(user, semester_id):
    """
    Delete a semester and all its subjects/grades.
    
    Returns:
        JSON: Status message
    """
    semester = Semester.query.filter_by(id=semester_id, user_id=user.id).first()
    if not semester:
        return jsonify({"error": "Semester not found"}), 404
    
    try:
        db.session.delete(semester)
        db.session.commit()
        return jsonify({"status": "deleted", "id": semester_id})
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete semester"}), 500


# --- Subject CRUD ---

@grades_bp.route("/semester/<int:semester_id>/subject", methods=["POST"])
@csrf_protect
@login_required
def create_subject(user, semester_id):
    """
    Create a new subject in a semester.
    
    Payload:
        {
            "name": "Mathematik",
            "counts_average": true
        }
    
    Returns:
        JSON: The created subject with calculated average
    """
    semester = Semester.query.filter_by(id=semester_id, user_id=user.id).first()
    if not semester:
        return jsonify({"error": "Semester not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "Neues Fach")
    counts_average = payload.get("counts_average", True)
    
    if not isinstance(name, str) or len(name) > 100:
        return jsonify({"error": "Invalid subject name"}), 400
    
    try:
        new_subject = Subject(
            semester_id=semester_id,
            name=name,
            counts_towards_average=bool(counts_average)
        )
        db.session.add(new_subject)
        db.session.commit()
        
        subj_calc = calculate_subject_average(new_subject)
        return jsonify({
            "id": new_subject.id,
            "name": new_subject.name,
            "counts_average": new_subject.counts_towards_average,
            "average": subj_calc["average"],
            "has_grades": subj_calc["has_grades"],
            "grades": [],
            "semester_stats": calculate_semester_average(semester)
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create subject"}), 500


@grades_bp.route("/subject/<int:subject_id>", methods=["PUT"])
@csrf_protect
@login_required
def update_subject(user, subject_id):
    """
    Update a subject's name and/or counts_average setting.
    
    Payload:
        {
            "name": "Physik",
            "counts_average": true
        }
    
    Returns:
        JSON: Updated subject with recalculated averages
    """
    subject = Subject.query.join(Semester).filter(
        Subject.id == subject_id,
        Semester.user_id == user.id
    ).first()
    
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    
    if "name" in payload:
        if not isinstance(payload["name"], str) or len(payload["name"]) > 100:
            return jsonify({"error": "Invalid subject name"}), 400
        subject.name = payload["name"]
    
    if "counts_average" in payload:
        subject.counts_towards_average = bool(payload["counts_average"])
    
    try:
        db.session.commit()
        subj_calc = calculate_subject_average(subject)
        return jsonify({
            "id": subject.id,
            "name": subject.name,
            "counts_average": subject.counts_towards_average,
            "average": subj_calc["average"],
            "has_grades": subj_calc["has_grades"],
            "semester_stats": calculate_semester_average(subject.semester)
        })
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update subject"}), 500


@grades_bp.route("/subject/<int:subject_id>", methods=["DELETE"])
@csrf_protect
@login_required
def delete_subject(user, subject_id):
    """
    Delete a subject and all its grades.
    
    Returns:
        JSON: Status and updated semester stats
    """
    subject = Subject.query.join(Semester).filter(
        Subject.id == subject_id,
        Semester.user_id == user.id
    ).first()
    
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    
    semester = subject.semester
    
    try:
        db.session.delete(subject)
        db.session.commit()
        return jsonify({
            "status": "deleted",
            "id": subject_id,
            "semester_stats": calculate_semester_average(semester)
        })
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete subject"}), 500


@grades_bp.route("/semester/<int:semester_id>/subjects/order", methods=["PUT"])
@csrf_protect
@login_required
def update_subject_order(user, semester_id):
    """
    Update the display order of subjects in a semester.
    
    Payload:
        {
            "order": [3, 1, 2]  // Array of subject IDs in desired order
        }
    
    Returns:
        JSON: Status message
    """
    semester = Semester.query.filter_by(id=semester_id, user_id=user.id).first()
    if not semester:
        return jsonify({"error": "Semester not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    order = payload.get("order", [])
    
    if not isinstance(order, list):
        return jsonify({"error": "Order must be an array of subject IDs"}), 400
    
    try:
        # Get all subjects in this semester
        subjects = {s.id: s for s in semester.subjects}
        
        # Update display_order based on position in the array
        for position, subject_id in enumerate(order):
            if subject_id in subjects:
                subjects[subject_id].display_order = position
        
        db.session.commit()
        return jsonify({"status": "ok"})
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update subject order"}), 500


# --- Grade CRUD ---

@grades_bp.route("/subject/<int:subject_id>/grade", methods=["POST"])
@csrf_protect
@login_required
def create_grade(user, subject_id):
    """
    Create a new grade in a subject.
    
    Payload:
        {
            "name": "Prüfung 1",
            "value": 5.5,
            "weight": 1.0,
            "counts": true
        }
    
    Returns:
        JSON: Created grade with updated averages
    """
    subject = Subject.query.join(Semester).filter(
        Subject.id == subject_id,
        Semester.user_id == user.id
    ).first()
    
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    
    name = payload.get("name", "")
    try:
        value = float(payload.get("value", 0))
        weight = float(payload.get("weight", 1.0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid value or weight"}), 400
    
    counts = bool(payload.get("counts", True))
    
    # Validate grade value (Swiss system: 1-6)
    if value < 1.0 or value > 6.0:
        return jsonify({"error": "Grade value must be between 1.0 and 6.0"}), 400
    
    if weight <= 0:
        return jsonify({"error": "Weight must be positive"}), 400
    
    if not isinstance(name, str) or len(name) > 100:
        return jsonify({"error": "Invalid grade name"}), 400
    
    try:
        new_grade = Grade(
            subject_id=subject_id,
            name=name,
            value=value,
            weight=weight,
            counts=counts
        )
        db.session.add(new_grade)
        db.session.commit()
        
        subj_calc = calculate_subject_average(subject)
        return jsonify({
            "id": new_grade.id,
            "name": new_grade.name,
            "value": new_grade.value,
            "weight": new_grade.weight,
            "counts": new_grade.counts,
            "subject_average": subj_calc["average"],
            "semester_stats": calculate_semester_average(subject.semester)
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create grade"}), 500


@grades_bp.route("/grade/<int:grade_id>", methods=["PUT"])
@csrf_protect
@login_required
def update_grade(user, grade_id):
    """
    Update a grade's properties.
    
    Payload:
        {
            "name": "Prüfung 1",
            "value": 5.5,
            "weight": 1.0,
            "counts": true
        }
    
    Returns:
        JSON: Updated grade with recalculated averages
    """
    grade = Grade.query.join(Subject).join(Semester).filter(
        Grade.id == grade_id,
        Semester.user_id == user.id
    ).first()
    
    if not grade:
        return jsonify({"error": "Grade not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    
    if "name" in payload:
        if not isinstance(payload["name"], str) or len(payload["name"]) > 100:
            return jsonify({"error": "Invalid grade name"}), 400
        grade.name = payload["name"]
    
    if "value" in payload:
        try:
            value = float(payload["value"])
            if value < 1.0 or value > 6.0:
                return jsonify({"error": "Grade value must be between 1.0 and 6.0"}), 400
            grade.value = value
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid value"}), 400
    
    if "weight" in payload:
        try:
            weight = float(payload["weight"])
            if weight <= 0:
                return jsonify({"error": "Weight must be positive"}), 400
            grade.weight = weight
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid weight"}), 400
    
    if "counts" in payload:
        grade.counts = bool(payload["counts"])
    
    try:
        db.session.commit()
        subject = grade.subject
        subj_calc = calculate_subject_average(subject)
        return jsonify({
            "id": grade.id,
            "name": grade.name,
            "value": grade.value,
            "weight": grade.weight,
            "counts": grade.counts,
            "subject_average": subj_calc["average"],
            "semester_stats": calculate_semester_average(subject.semester)
        })
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update grade"}), 500


@grades_bp.route("/grade/<int:grade_id>", methods=["DELETE"])
@csrf_protect
@login_required
def delete_grade(user, grade_id):
    """
    Delete a grade.
    
    Returns:
        JSON: Status with updated averages
    """
    grade = Grade.query.join(Subject).join(Semester).filter(
        Grade.id == grade_id,
        Semester.user_id == user.id
    ).first()
    
    if not grade:
        return jsonify({"error": "Grade not found"}), 404
    
    subject = grade.subject
    semester = subject.semester
    
    try:
        db.session.delete(grade)
        db.session.commit()
        
        subj_calc = calculate_subject_average(subject)
        return jsonify({
            "status": "deleted",
            "id": grade_id,
            "subject_average": subj_calc["average"],
            "semester_stats": calculate_semester_average(semester)
        })
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete grade"}), 500


# --- Calculation Endpoints ---

@grades_bp.route("/subject/<int:subject_id>/dream-grade", methods=["POST"])
@csrf_protect
@login_required
def calculate_dream_grade_endpoint(user, subject_id):
    """
    Calculate the grade needed to achieve a desired average.
    
    Payload:
        {
            "wished_average": 5.0,
            "next_weight": 1.0
        }
    
    Returns:
        JSON: Needed grade and feasibility info
    """
    subject = Subject.query.join(Semester).filter(
        Subject.id == subject_id,
        Semester.user_id == user.id
    ).first()
    
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    
    try:
        wished_avg = float(payload.get("wished_average", 0))
        next_weight = float(payload.get("next_weight", 1.0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input values"}), 400
    
    if wished_avg < 1.0 or wished_avg > 6.0:
        return jsonify({"error": "Wished average must be between 1.0 and 6.0"}), 400
    
    if next_weight <= 0:
        return jsonify({"error": "Weight must be positive"}), 400
    
    result = calculate_dream_grade(subject, wished_avg, next_weight)
    return jsonify(result)


@grades_bp.route("/reorder-subjects", methods=["POST"])
@csrf_protect
@login_required
def reorder_subjects(user):
    """
    Reorder subjects within a semester (for drag-and-drop functionality).
    
    Payload:
        {
            "semester_id": 1,
            "subject_ids": [3, 1, 2]  // New order of subject IDs
        }
    
    Returns:
        JSON: Status message
    """
    payload = request.get_json(silent=True) or {}
    semester_id = payload.get("semester_id")
    subject_ids = payload.get("subject_ids", [])
    
    if not semester_id or not isinstance(subject_ids, list):
        return jsonify({"error": "Invalid payload"}), 400
    
    semester = Semester.query.filter_by(id=semester_id, user_id=user.id).first()
    if not semester:
        return jsonify({"error": "Semester not found"}), 404
    
    # Note: The current model doesn't have an order field.
    # This would need a migration to add an 'order' column to Subject.
    # For now, we'll just return success as the frontend handles ordering visually.
    return jsonify({"status": "ok"})
