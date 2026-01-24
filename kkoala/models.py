from .extensions import db
from datetime import datetime
import secrets

def generate_token():
    return secrets.token_urlsafe(12)

# -------------------------------
# User authentication and profile
# -------------------------------

class User(db.Model):
    """
    Stores user authentication and profile information.

    Attributes:
        id (int): Primary key.
        username (str): Unique username for login.
        password (str): Hashed password.
        email (str): Unique email address.
        events (relationship): All calendar events for the user.
        semesters (relationship): All semesters for the user (grades).
        settings (relationship): User's settings (one-to-one).
        todo_categories (relationship): User's to-do list categories.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Hashed password
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)

    # Relationships
    events = db.relationship(
        "Event", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    semesters = db.relationship(
        "Semester", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    settings = db.relationship(
        "Settings", backref="user", uselist=False, lazy=True, cascade="all, delete-orphan"
    )
    todo_categories = db.relationship(
        "ToDoCategory", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    citation_groups = db.relationship(
        "CitationGroup", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    flashcard_sets = db.relationship(
        "FlashcardSet", backref="user", lazy=True, cascade="all, delete-orphan"
    )

class PushSubscription(db.Model):
    """
    Stores Web Push subscriptions for users to receive notifications.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    endpoint = db.Column(db.String(500), nullable=False)
    p256dh = db.Column(db.String(200), nullable=False)
    auth = db.Column(db.String(200), nullable=False)

# -------------------------------
# User settings and priorities
# -------------------------------

class Settings(db.Model):
    """
    Stores user-specific scheduling and display preferences.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        learn_on_saturday (bool): Allow learning on Saturday.
        learn_on_sunday (bool): Allow learning on Sunday.
        preferred_learning_time (str): Preferred start time for learning blocks (HH:MM).
        study_block_color (str): Color for algorithm-generated study blocks.
        import_color (str): Color for imported events.
        dark_mode (str): User's dark mode preference.
        priority_settings (relationship): Priority rules for learning algorithm.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    learn_on_saturday = db.Column(db.Boolean, default=False)
    learn_on_sunday = db.Column(db.Boolean, default=False)
    preferred_learning_time = db.Column(db.String(20), default="18:00")
    study_block_color = db.Column(db.String(7), default="#0000FF")
    import_color = db.Column(db.String(7), default="#6C757D")
    dark_mode = db.Column(db.String(10), default="system")

    # Priority settings for learning algorithm
    priority_settings = db.relationship(
        "PrioritySetting", backref="settings", lazy=True, cascade="all, delete-orphan"
    )

class PrioritySetting(db.Model):
    """
    Stores user-specific rules for each exam priority level.

    Attributes:
        id (int): Primary key.
        settings_id (int): Foreign key to Settings.
        priority_level (int): Priority (e.g., 1, 2, 3).
        color (str): Color for exams of this priority.
        max_hours_per_day (float): Max learning hours per day.
        total_hours_to_learn (float): Total hours to schedule for this priority.
    """
    id = db.Column(db.Integer, primary_key=True)
    settings_id = db.Column(db.Integer, db.ForeignKey("settings.id"), nullable=False)
    priority_level = db.Column(db.Integer, nullable=False)  # e.g., 1, 2, 3
    color = db.Column(db.String(7), nullable=False)
    max_hours_per_day = db.Column(db.Float, nullable=False)
    total_hours_to_learn = db.Column(db.Float, nullable=False)

# -------------------------------
# Calendar events (agenda)
# -------------------------------

class Event(db.Model):
    """
    Stores calendar entries (classes, exams, study blocks).

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        title (str): Event title.
        start (str): Start datetime (ISO format).
        end (str): End datetime (ISO format).
        color (str): Display color.
        priority (int): 0 for study blocks, >0 for user events/exams.
        recurrence (str): Recurrence pattern.
        recurrence_id (str): ID for recurring events.
        all_day (bool): All-day event flag.
        locked (bool): True if user-created (not deleted by algorithm).
        exam_id (int): Links a study block to its parent exam.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", onupdate="CASCADE"), nullable=False
    )
    title = db.Column(db.String(500), nullable=False)
    start = db.Column(db.String(50), nullable=False)  # ISO format datetime
    end = db.Column(db.String(50), nullable=True)     # ISO format datetime
    color = db.Column(db.String(7), nullable=False)
    priority = db.Column(db.Integer, nullable=False)  # 0: study block, >0: exam/event
    recurrence = db.Column(db.String(50), nullable=True)
    recurrence_id = db.Column(db.String(50), nullable=True)
    all_day = db.Column(db.Boolean, nullable=False, default=False)
    locked = db.Column(db.Boolean, default=True)      # True: user-created, False: algorithm
    exam_id = db.Column(db.Integer, nullable=True)    # Link to parent exam

# -------------------------------
# Grades (Noten) feature
# -------------------------------

class Semester(db.Model):
    """
    Stores academic semesters for the grades feature.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        name (str): Semester name.
        is_current (bool): Whether this is the user's current active semester.
        subjects (relationship): All subjects in this semester.
    
    Note:
        Only one semester per user should have is_current=True at a time.
        This is enforced at the application level (see routes/grades.py set_current_semester).
        A database-level partial unique index could provide additional safety but
        has limited cross-database compatibility (especially with SQLite).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_current = db.Column(db.Boolean, nullable=False, default=False)

    # Subjects in this semester
    subjects = db.relationship(
        "Subject", backref="semester", lazy=True, cascade="all, delete-orphan"
    )

class Subject(db.Model):
    """
    Stores subjects within a semester.

    Attributes:
        id (int): Primary key.
        semester_id (int): Foreign key to Semester.
        name (str): Subject name.
        counts_towards_average (bool): Whether subject counts for average.
        display_order (int): Order in which to display the subject (lower first).
        grades (relationship): All grades for this subject.
    """
    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey("semester.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    counts_towards_average = db.Column(db.Boolean, nullable=False, default=True)
    display_order = db.Column(db.Integer, nullable=False, default=0)

    # Grades for this subject
    grades = db.relationship(
        "Grade", backref="subject", lazy=True, cascade="all, delete-orphan"
    )

class Grade(db.Model):
    """
    Stores individual grades for subjects.

    Attributes:
        id (int): Primary key.
        subject_id (int): Foreign key to Subject.
        name (str): Grade name (e.g., 'Midterm Exam').
        value (float): Grade value.
        weight (float): Weight of the grade.
        counts (bool): Whether grade is included in calculation.
    """
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    counts = db.Column(db.Boolean, nullable=False, default=True)

# -------------------------------
# ToDo list feature
# -------------------------------

class ToDoCategory(db.Model):
    """
    Stores user-specific to-do list categories.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        name (str): Category name.
        items (relationship): All to-do items in this category.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # To-do items in this category
    items = db.relationship(
        "ToDoItem",
        backref="category",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="ToDoItem.position"
    )

class ToDoItem(db.Model):
    """
    Stores individual to-do list items.

    Attributes:
        id (int): Primary key.
        category_id (int): Foreign key to ToDoCategory.
        description (str): Description of the to-do item.
        completed (bool): Completion status.
    """
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("to_do_category.id"), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)

# -------------------------------
# Citation Generator feature
# -------------------------------

class CitationGroup(db.Model):
    """
    Stores citation groups for organizing citations.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        name (str): Group name.
        citations (relationship): All citations in this group.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)

    # Citations in this group
    citations = db.relationship(
        "Citation", backref="group", lazy=True, cascade="all, delete-orphan"
    )


class Citation(db.Model):
    """
    Stores individual citations within a group.

    Attributes:
        id (int): Primary key.
        group_id (int): Foreign key to CitationGroup.
        source_type (str): Type of source (book, website, article, etc.).
        style (str): Citation style (APA, MLA, Chicago, etc.).
        data (str): JSON string with source details (author, title, year, etc.).
        formatted_citation (str): The generated formatted citation text.
    """
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("citation_group.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = db.Column(db.String(50), nullable=False)  # book, website, article, etc.
    style = db.Column(db.String(50), nullable=False)  # APA, MLA, Chicago, etc.
    data = db.Column(db.Text, nullable=False)  # JSON string with source details
    formatted_citation = db.Column(db.Text, nullable=True)


# -------------------------------
# Flashcards
# -------------------------------

class FlashcardSet(db.Model):
    """
    Represents a set of flashcards.
    """
    is_public = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(32), unique=True, nullable=False, default=generate_token)
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
    # starred is deprecated in favor of UserFlashcardStar, but kept for migration/compatibility if needed
    starred = db.Column(db.Boolean, default=False)

class UserFlashcardStar(db.Model):
    """
    Tracks which user has starred which flashcard.
    """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcard.id', ondelete='CASCADE'), primary_key=True)

# -------------------------------
# Curriculum and Learning Content
# -------------------------------

class CurriculumSubject(db.Model):
    """
    Represents a school subject (e.g., Math, German).
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False, default=1) # Subject belongs to a specific year
    icon = db.Column(db.String(10), default="📖")
    color = db.Column(db.String(20), default="#3B82F6")
    topics = db.relationship("CurriculumTopic", backref="subject", lazy=True, cascade="all, delete-orphan")

class CurriculumTopic(db.Model):
    """
    Represents a main topic within a subject (e.g., Algebra).
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('curriculum_subject.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False) # 1, 2, 3, 4
    subtopics = db.relationship("CurriculumSubTopic", backref="topic", lazy=True, cascade="all, delete-orphan")

class CurriculumSubTopic(db.Model):
    """
    Represents a specific learning module/subtopic (e.g., Quadratic Equations).
    Storage for the actual theory content.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('curriculum_topic.id'), nullable=False)
    difficulty = db.Column(db.String(20), default="intermediate")
    content_html = db.Column(db.Text, nullable=True) # HTML content from uploaded file
    estimated_time = db.Column(db.String(50), default="45 Minuten")
    
    # Exercises related to this subtopic
    exercises = db.relationship("Exercise", backref="subtopic", lazy=True, cascade="all, delete-orphan")


class Exercise(db.Model):
    """
    Represents a structured exercise for a subtopic.
    Can be multiple choice, text input, or true/false.
    """
    id = db.Column(db.Integer, primary_key=True)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('curriculum_sub_topic.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'multiple-choice', 'text', 'true-false'
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True) # JSON string for MC options (or pipe separated)
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)

    @property
    def options_list(self):
        import json
        if self.options:
            try:
                return json.loads(self.options)
            except:
                return []
        return []


