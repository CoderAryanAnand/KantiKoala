import json
import re
from bs4 import BeautifulSoup

def parse_exercises_from_html(html_content):
    """
    Parses HTML content (e.g. from Mammoth) to find exercise tables.
    Removes the tables from the HTML and returns the extracted exercises + cleaned HTML.
    
    Returns:
        exercises (list): List of dicts with exercise data.
        cleaned_html (str): The HTML with exercise tables removed.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    exercises = []
    
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        if not rows:
            continue
            
        data = {}
        options = []
        is_exercise = False
        
        # Heuristic: Check for "Question" keyword in the first cells of rows
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
                
            # Get text from first column (key) and second column (value)
            key = cells[0].get_text(strip=True).lower()
            # For value, we might want inner HTML to preserve formatting? 
            # For now, plain text is safer for matching, simpler for MVP.
            value = cells[1].get_text(strip=True)
            
            if "question" in key or "frage" in key:
                is_exercise = True
                data['question'] = value
            elif "option" in key or "auswahl" in key:
                options.append(value)
            elif "answer" in key or "correct" in key or "lösung" in key or "antwort" in key:
                data['correct_answer'] = value
            elif "explanation" in key or "erklärung" in key:
                data['explanation'] = value
        
        if is_exercise and 'question' in data and 'correct_answer' in data:
            if options:
                data['type'] = 'multiple-choice'
                data['options'] = options
            else:
                data['type'] = 'text'
                data['options'] = []
            
            if 'explanation' not in data:
                data['explanation'] = None
                
            exercises.append(data)
            # Remove the table from the DOM so it doesn't show up in theory content
            table.decompose()
            
    return exercises, str(soup)

def parse_exercises_from_latex(latex_content):
    """
    Parses LaTeX content for \\begin{question}{type}{answer} blocks.
    Removes them from the content.
    
    Returns:
        exercises (list): List of extracted exercises.
        cleaned_content (str): LaTeX content with question blocks removed.
    """
    exercises = []
    
    # Regex pattern: \begin{question}{type}{answer} ... \end{question}
    # Using DOTALL for multiline matching
    pattern = r'\\begin\{question\}\{(.*?)\}\{(.*?)\}(.*?)\\end\{question\}'
    
    matches = re.finditer(pattern, latex_content, re.DOTALL)
    
    for match in matches:
        q_type_raw = match.group(1).strip().lower()
        answer = match.group(2).strip()
        body = match.group(3).strip()
        
        data = {
            'type': 'text',
            'correct_answer': answer,
            'options': [],
            'explanation': None,
            'question': ""
        }
        
        if 'choice' in q_type_raw or 'mc' in q_type_raw:
            data['type'] = 'multiple-choice'
        else:
            data['type'] = 'text'
            
        # Extract explanation if present: \explanation{...}
        expl_pattern = r'\\explanation\{(.*?)\}'
        expl_match = re.search(expl_pattern, body, re.DOTALL)
        if expl_match:
            data['explanation'] = expl_match.group(1).strip()
            # Remove explanation from body so it doesn't duplicate into question?
            body = re.sub(expl_pattern, '', body, flags=re.DOTALL).strip()
            
        if data['type'] == 'multiple-choice':
            # Split by \item
            # First segment is the question text
            parts = re.split(r'\\item', body)
            data['question'] = parts[0].strip()
            
            # The rest are options
            for opt in parts[1:]:
                clean_opt = opt.strip()
                if clean_opt:
                    data['options'].append(clean_opt)
        else:
            data['question'] = body
            
        exercises.append(data)
    
    cleaned_content = re.sub(pattern, '', latex_content, flags=re.DOTALL)
    
    return exercises, cleaned_content
