import json
import os
from kkoala.extensions import db
from kkoala.models import CurriculumSubject, CurriculumTopic, CurriculumSubTopic, Exercise
from wsgi import application as app

def reset_curriculum():
    with app.app_context():
        print("Clearing existing curriculum data...")
        
        # Delete in order of dependencies (child first)
        Exercise.query.delete()
        CurriculumSubTopic.query.delete()
        CurriculumTopic.query.delete()
        CurriculumSubject.query.delete()
        
        db.session.commit()
        print("Curriculum tables cleared.")
        
        # Load data from JSON
        # app.root_path points to the package root (kkoala)
        json_path = os.path.join(app.root_path, "curriculum", "curriculum_data.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find curriculum_data.json at {json_path}")
            return

        print("Seeding subjects, topics, and subtopics from JSON...")
        
        count_subjects = 0
        count_topics = 0
        count_subtopics = 0
        
        # Iterate over subjects grouped by year ID in the JSON
        if "subjects" in data:
            for year_str, subjects_list in data["subjects"].items():
                year_id = int(year_str)
                
                for subj_data in subjects_list:
                    # Skip Sport in the learning curriculum (database), but keep it in consts.py for grades
                    if subj_data["name"] == "Sport":
                        continue
                        
                    # 1. Create Subject
                    subject = CurriculumSubject(
                        name=subj_data["name"],
                        year=year_id,
                        icon=subj_data.get("icon", "📖"),
                        color=subj_data.get("color", "#3B82F6")
                    )
                    db.session.add(subject)
                    db.session.flush() # Flush to get ID
                    count_subjects += 1
                    
                    # 2. Create Topics
                    if "topics" in subj_data:
                        for topic_data in subj_data["topics"]:
                            topic = CurriculumTopic(
                                name=topic_data["name"],
                                subject_id=subject.id,
                                year=year_id
                            )
                            db.session.add(topic)
                            db.session.flush()
                            count_topics += 1
                            
                            # 3. Create Subtopics
                            if "subtopics" in topic_data:
                                for sub_data in topic_data["subtopics"]:
                                    subtopic = CurriculumSubTopic(
                                        name=sub_data["name"],
                                        topic_id=topic.id,
                                        difficulty=sub_data.get("difficulty", "intermediate")
                                    )
                                    db.session.add(subtopic)
                                    count_subtopics += 1
        
        db.session.commit()
        print(f"Successfully created {count_subjects} subjects, {count_topics} topics, and {count_subtopics} subtopics.")

if __name__ == "__main__":
    reset_curriculum()
