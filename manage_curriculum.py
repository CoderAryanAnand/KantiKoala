import sys
import os
import json
import logging

# Ensure the script can see the kkoala package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kkoala import create_app
from kkoala.extensions import db
from kkoala.models import CurriculumSubject, CurriculumTopic, CurriculumSubTopic, Exercise
from kkoala.config import ProdConfig
from kkoala.consts import SEMESTER_TEMPLATES

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

app = create_app()

def reset_curriculum():
    """Deletes all curriculum data and repopulates it from curriculum_data.json."""
    
    json_path = os.path.join(app.root_path, "curriculum", "curriculum_data.json")
    if not os.path.exists(json_path):
        logging.error(f"Could not find curriculum_data.json at {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            return

    # Map target year (semester ID) to JSON key
    # Year 1 -> Semester 2 (id=2) -> matches JSON "1"
    # Year 2 -> Semester 4 (id=4) -> matches JSON "2"
    # Year 3 -> Semester 6 (id=6) -> matches JSON "3"
    # Year 4 -> Semester 8 (id=8) -> matches JSON "4"
    target_semesters = [2, 4, 6, 8]

    # Convert SEMESTER_TEMPLATES to a dict for easier lookup
    semester_templates_map = { t['id']: t['subjects'] for t in SEMESTER_TEMPLATES }

    with app.app_context():
        logging.info("--- Starting Curriculum Reset ---")
        
        # 1. Clear existing data
        logging.info("Clearing existing curriculum tables...")
        try:
            # Delete in order of dependencies (child first)
            Exercise.query.delete()
            CurriculumSubTopic.query.delete()
            CurriculumTopic.query.delete()
            CurriculumSubject.query.delete()
            db.session.commit()
            logging.info("Tables cleared.")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error clearing tables: {e}")
            return

        # 2. Repopulate
        logging.info("Seeding new data...")
        
        count_subjects = 0
        count_topics = 0
        count_subtopics = 0
        
        for sem_id in target_semesters:
            year_val = sem_id // 2 # 2->1, 4->2, 6->3, 8->4
            json_year_key = str(year_val)
            
            # Get list of subjects for this semester from CONSTS
            consts_subjects = semester_templates_map.get(sem_id, [])
            
            # Get JSON data for this "year" to enrich with topics
            json_subjects_data = data["subjects"].get(json_year_key, [])
            # Create a lookup for JSON data by subject name
            json_subj_map = { s["name"]: s for s in json_subjects_data }

            # Iterate through subjects defined in CONSTS
            for subj_name in consts_subjects:
                if subj_name == "Sport":
                    continue

                # Find matching data in JSON if available
                subj_data = json_subj_map.get(subj_name, {})
                
                # Create Subject
                subject = CurriculumSubject(
                    name=subj_name,
                    year=year_val, # Using actual year (1-4) instead of Semester ID
                    icon=subj_data.get("icon", "📖"),
                    color=subj_data.get("color", "#3B82F6")
                )
                db.session.add(subject)
                db.session.flush() # Get ID for children
                count_subjects += 1
                
                # Create Topics (only if found in JSON)
                topics = subj_data.get("topics", [])
                for topic_data in topics:
                    topic = CurriculumTopic(
                        name=topic_data["name"],
                        subject_id=subject.id,
                        year=year_val
                    )
                    db.session.add(topic)
                    db.session.flush()
                    count_topics += 1
                    
                    # Create Subtopics
                    subtopics = topic_data.get("subtopics", [])
                    for sub_data in subtopics:
                        subtopic = CurriculumSubTopic(
                            name=sub_data["name"],
                            topic_id=topic.id,
                            difficulty=sub_data.get("difficulty", "intermediate")
                        )
                        db.session.add(subtopic)
                        count_subtopics += 1
        
        try:
            db.session.commit()
            logging.info(f"Success! Created {count_subjects} subjects, {count_topics} topics, {count_subtopics} subtopics.")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error committing changes: {e}")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "reset":
            check = input("This will DELETE ALL curriculum data. Type 'yes' to confirm: ")
            if check.lower() == 'yes':
                reset_curriculum()
            else:
                print("Aborted.")
        else:
            print(f"Unknown command: {command}")
            print("Usage: python manage_curriculum.py reset")
    else:
        print("Usage: python manage_curriculum.py reset")

if __name__ == "__main__":
    main()
