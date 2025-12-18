from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from ..models import ToDoCategory, FlashcardSet, Flashcard
from ..extensions import db
from ..utils import login_required
import json
import io
import csv

tools_bp = Blueprint(
    "tools", __name__, template_folder="../templates", static_folder="../static"
)


@tools_bp.route("/")
@login_required
def tools_index(user):
    """
    Tools index route: Displays the main tools page with available tools.

    Args:
        user: The authenticated user object.

    Returns:
        str: Rendered HTML template ('tools.html').
    """
    return render_template("tools.html")


@tools_bp.route("/lerntimer")
@login_required
def lerntimer(user):
    """
    Pomodoro timer route: Renders the lerntimer page.

    Args:
        user: The authenticated user object.

    Returns:
        str: Rendered HTML template ('tools_lerntimer.html').
    """
    return render_template("tools_lerntimer.html")


@tools_bp.route("/zitierungsgenerator")
@login_required
def citation_generator(user):
    """
    Citation generator route: Renders the citation generator tool page.

    Args:
        user: The authenticated user object.

    Returns:
        str: Rendered HTML template ('tools_citation.html').
    """
    return render_template("tools_citation.html")


@tools_bp.route("/lernkarten")
@login_required
def flashcards(user):
    """
    Flashcards index: Lists all flashcard sets for the user.
    """
    sets = FlashcardSet.query.filter_by(user_id=user.id).order_by(FlashcardSet.created_at.desc()).all()
    return render_template("tools_flashcards.html", sets=sets)

@tools_bp.route("/lernkarten/create", methods=["POST"])
@login_required
def create_flashcard_set(user):
    data = request.json
    title = data.get("title")
    description = data.get("description")
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
        
    new_set = FlashcardSet(user_id=user.id, title=title, description=description)
    db.session.add(new_set)
    db.session.commit()
    
    return jsonify({"id": new_set.id, "message": "Set created successfully"})

@tools_bp.route("/lernkarten/<int:set_id>")
@login_required
def view_flashcard_set(user, set_id):
    card_set = FlashcardSet.query.filter_by(id=set_id, user_id=user.id).first_or_404()
    # Sort cards by rank
    cards = sorted(card_set.cards, key=lambda x: x.rank)
    return render_template("tools_flashcards_view.html", card_set=card_set, cards=cards)

@tools_bp.route("/lernkarten/<int:set_id>/update", methods=["POST"])
@login_required
def update_flashcard_set(user, set_id):
    card_set = FlashcardSet.query.filter_by(id=set_id, user_id=user.id).first_or_404()
    data = request.json
    
    # Update set details
    if "title" in data:
        card_set.title = data["title"]
    if "description" in data:
        card_set.description = data["description"]
        
    # Update cards
    if "cards" in data:
        # Remove existing cards (simple approach for now)
        Flashcard.query.filter_by(set_id=set_id).delete()
        
        for i, card_data in enumerate(data["cards"]):
            new_card = Flashcard(
                set_id=set_id,
                term=card_data["term"],
                definition=card_data["definition"],
                rank=i,
                starred=card_data.get("starred", False)
            )
            db.session.add(new_card)
            
    db.session.commit()
    return jsonify({"message": "Set updated successfully"})

@tools_bp.route("/lernkarten/<int:set_id>/delete", methods=["DELETE"])
@login_required
def delete_flashcard_set(user, set_id):
    card_set = FlashcardSet.query.filter_by(id=set_id, user_id=user.id).first_or_404()
    db.session.delete(card_set)
    db.session.commit()
    return jsonify({"message": "Set deleted successfully"})

@tools_bp.route("/lernkarten/import", methods=["POST"])
@login_required
def import_flashcard_set(user):
    # Handle File Upload (JSON)
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        try:
            content = json.load(file)
            title = content.get("title", "Imported Set")
            description = content.get("description", "")
            cards = content.get("cards", [])
            
            new_set = FlashcardSet(user_id=user.id, title=title, description=description)
            db.session.add(new_set)
            db.session.flush() # Get ID
            
            for i, card in enumerate(cards):
                new_card = Flashcard(
                    set_id=new_set.id,
                    term=card.get("term", ""),
                    definition=card.get("definition", ""),
                    rank=i
                )
                db.session.add(new_card)
                
            db.session.commit()
            return jsonify({"message": "Set imported successfully", "id": new_set.id})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Handle Text Import (Smart Parsing like app.py)
    elif request.is_json:
        data = request.json
        title = data.get("title")
        text_content = data.get("content")
        
        if not title or not text_content:
             return jsonify({"error": "Title and content are required"}), 400
             
        cards = []
        try:
            # Parse the input text (Term, Definition)
            lines = text_content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                term = None
                definition = None

                # 1. Handle quoted terms: e.g., "Term, with comma", Definition
                if line.startswith('"'):
                    # Find the closing quote of the term
                    end_quote_index = line.find('"', 1)
                    
                    # Check if a comma follows the closing quote
                    if end_quote_index > 0 and end_quote_index + 1 < len(line) and line[end_quote_index + 1] == ',':
                        # Term is everything inside the quotes (excluding the quotes)
                        term = line[1:end_quote_index].strip()
                        # Definition is everything after the comma (and space)
                        definition = line[end_quote_index + 2:].strip()
                    
                # 2. Handle non-quoted terms (simple split)
                if not term and ',' in line:
                    # split only on first comma
                    parts = line.split(',', 1)
                    term = parts[0].strip()
                    definition = parts[1].strip()
                
                # Final clean up and append
                if term and definition:
                    # Clean up definition: remove surrounding quotes if they exist
                    if definition.startswith('"') and definition.endswith('"'):
                        definition = definition[1:-1].strip()
                        
                    cards.append({'term': term, 'definition': definition})

        except Exception as e:
            return jsonify({"error": f"Error parsing text: {str(e)}"}), 400
        
        if not cards:
            return jsonify({"error": "No valid cards found"}), 400
            
        # Create set
        new_set = FlashcardSet(user_id=user.id, title=title, description="Imported from text")
        db.session.add(new_set)
        db.session.flush()
        
        for i, card in enumerate(cards):
            new_card = Flashcard(
                set_id=new_set.id,
                term=card["term"],
                definition=card["definition"],
                rank=i
            )
            db.session.add(new_card)
        
        db.session.commit()
        return jsonify({"message": "Set imported successfully", "id": new_set.id})

    else:
        return jsonify({"error": "Invalid request"}), 400

@tools_bp.route("/lernkarten/<int:set_id>/export")
@login_required
def export_flashcard_set(user, set_id):
    card_set = FlashcardSet.query.filter_by(id=set_id, user_id=user.id).first_or_404()
    
    data = {
        "title": card_set.title,
        "description": card_set.description,
        "cards": [{"term": c.term, "definition": c.definition, "starred": c.starred} for c in card_set.cards]
    }
    
    # Return as a downloadable JSON file
    return jsonify(data)


@tools_bp.route("/todo")
@login_required
def todo_index(user):
    """
    To-Do List route: Displays the user's to-do categories and items.

    Args:
        user: The authenticated user object.

    Returns:
        str: Rendered HTML template ('todo.html').
    """
    categories = ToDoCategory.query.filter_by(user_id=user.id).all()
    return render_template("todo.html", categories=categories)

