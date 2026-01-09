import json
import os
from kkoala import create_app, db
from kkoala.models import CurriculumSubject, CurriculumTopic, CurriculumSubTopic
# from bs4 import BeautifulSoup
# import markdown

# Fix path to config if needed, or pass object directly
# Assuming running from root, config is kkoala.config
app = create_app(config_class="kkoala.config.DevConfig")

def load_json(filename):
    path = os.path.join('kkoala', 'curriculum', filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_data():
    with app.app_context():
        # Check if data exists
        if CurriculumSubject.query.first():
            print("Data already exists. Skipping import.")
            return

        print("Importing curriculum...")
        curr_data = load_json('curriculum_data.json')
        theory_data = load_json('theory_content.json')

        # Map subjects by ID to avoid duplicates across years if any (though structure separates them)
        # Structure: "subjects": { "1": [...], "2": [...] }
        
        subjects_data = curr_data.get('subjects', {})
        
        # We need to flatten this. One subject "Mathematics" can appear in Year 1, 2, 3, 4.
        # But usually in DB normalization, "Mathematics" is one Subject, and it has Topics in specific Years.
        # My model: CurriculumTopic has year. CurriculumSubject does NOT.
        
        # So I should create unique Subjects first.
        unique_subjects = {} # name -> db_obj

        for year_str, subjects_list in subjects_data.items():
            year = int(year_str)
            for subj in subjects_list:
                s_name = subj['name']
                if s_name not in unique_subjects:
                    new_subj = CurriculumSubject(
                        name=s_name,
                        icon=subj.get('icon', '📖'),
                        color=subj.get('color', '#3B82F6')
                    )
                    db.session.add(new_subj)
                    db.session.flush() # get ID
                    unique_subjects[s_name] = new_subj
                
                db_subj = unique_subjects[s_name]
                
                # Topics
                for topic in subj.get('topics', []):
                    new_topic = CurriculumTopic(
                        name=topic['name'],
                        subject_id=db_subj.id,
                        year=year
                    )
                    db.session.add(new_topic)
                    db.session.flush()
                    
                    # Subtopics
                    for sub in topic.get('subtopics', []):
                        sub_id = sub['id']
                        # Look up theory content
                        content_entry = theory_data.get(sub_id)
                        content_html = ""
                        
                        if content_entry:
                            # Convert JSON content structure to HTML
                            # content is usually { "introduction": "...", "sections": [...] }
                            # I will store a simple HTML representation
                            
                            intro = content_entry.get('content', {}).get('introduction', '')
                            sections = content_entry.get('content', {}).get('sections', [])
                            
                            html_parts = [f"<p>{intro}</p>"] if intro else []
                            for sec in sections:
                                title = sec.get('title', '')
                                body = sec.get('content', '')
                                # Convert latex $...$ to something else? Or keep as is.
                                html_parts.append(f"<h3>{title}</h3>")
                                # convert newlines to <br> or wrap in p
                                body_html = body.replace('\n', '<br>')
                                html_parts.append(f"<div>{body_html}</div>")
                                
                            content_html = "".join(html_parts)
                        
                        new_sub = CurriculumSubTopic(
                            name=sub['name'],
                            topic_id=new_topic.id,
                            difficulty=sub.get('difficulty', 'intermediate'),
                            content_html=content_html
                        )
                        db.session.add(new_sub)

        db.session.commit()
        print("Import completed.")

if __name__ == "__main__":
    import_data()
