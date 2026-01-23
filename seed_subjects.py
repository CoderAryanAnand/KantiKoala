import json
import os
from wsgi import application as app
from kkoala.extensions import db
from kkoala.models import CurriculumSubject

def seed_subjects():
    with app.app_context():
        print("Seeding subjects from JSON (skipping existing ones)...")
        
        json_path = os.path.join(app.root_path, "curriculum", "curriculum_data.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find curriculum_data.json at {json_path}")
            return

        count_added = 0
        
        if "subjects" in data:
            for year_str, subjects_list in data["subjects"].items():
                year_id = int(year_str)
                
                for subj_data in subjects_list:
                    # Skip Sport as in reset_curriculum
                    if subj_data["name"] == "Sport":
                        continue
                    
                    # Check if subject exists
                    existing = CurriculumSubject.query.filter_by(
                        year=year_id, 
                        name=subj_data["name"]
                    ).first()
                    
                    if not existing:
                        subject = CurriculumSubject(
                            name=subj_data["name"],
                            year=year_id,
                            icon=subj_data.get("icon", "📖"),
                            color=subj_data.get("color", "#3B82F6")
                        )
                        db.session.add(subject)
                        count_added += 1
                        print(f"Added: {subj_data['name']} (Year {year_id})")
                    else:
                        # Optional: Update icon/color if changed? 
                        # For now, just skip to preserve potential user edits or stability.
                        pass
        
        db.session.commit()
        print(f"Finished. Added {count_added} new subjects.")

if __name__ == "__main__":
    seed_subjects()
