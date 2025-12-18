
# -------------------------------
# Flashcards
# -------------------------------

class FlashcardSet(db.Model):
    """
    Represents a set of flashcards.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to cards
    cards = db.relationship(
        "Flashcard", backref="set", lazy=True, cascade="all, delete-orphan"
    )

class Flashcard(db.Model):
    """
    Represents a single flashcard within a set.
    """
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey("flashcard_set.id"), nullable=False)
    term = db.Column(db.Text, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    rank = db.Column(db.Integer, default=0)  # For ordering
