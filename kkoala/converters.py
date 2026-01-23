"""
This module handles file format conversions for the application.
It supports converting DOCX, PDF, and LaTeX files into HTML.
"""
import os
import shutil
import uuid
import subprocess
import base64
import sys
import tempfile
import mammoth
import fitz  # PyMuPDF

def docx_to_html(file_stream):
    """
    Converts a .docx file stream to HTML using Mammoth.
    """
    try:
        result = mammoth.convert_to_html(file_stream)
        return result.value
    except Exception as e:
        return f"<p class='text-red-500'>Fehler bei der Konvertierung der Word-Datei: {e}</p>"

def pdf_to_html(file_stream):
    """
    Parses PDF content and converts it to HTML.
    Extracts text blocks and images (as base64), preserving basic structure.
    """
    try:
        # Read the file stream into bytes
        file_stream.seek(0)
        file_bytes = file_stream.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        html_content = ""
        
        for page in doc:
            # get_text("dict") returns blocks of content (text or image)
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block['type'] == 0: # Text Block
                    # Iterate through lines and spans to reconstruct text with basic styling
                    p_content = ""
                    for line in block['lines']:
                        line_content = ""
                        for span in line['spans']:
                            text = span['text']
                            # Basic font checks (flags)
                            # bit 0: superscript, bit 1: italic, bit 4: bold
                            flags = span['flags']
                            prefix = ""
                            suffix = ""
                            
                            if flags & 2**4: # Bold
                                prefix += "<strong>"
                                suffix = "</strong>" + suffix
                            if flags & 2**1: # Italic
                                prefix += "<em>"
                                suffix = "</em>" + suffix
                                
                            line_content += f"{prefix}{text}{suffix} "
                        p_content += line_content.strip() + " "
                    
                    if p_content.strip():
                        html_content += f"<p class='mb-2'>{p_content}</p>\n"
                        
                elif block['type'] == 1: # Image Block
                    image_bytes = block['image']
                    ext = block['ext']
                    b64_img = base64.b64encode(image_bytes).decode('utf-8')
                    html_content += f'<div class="my-4"><img src="data:image/{ext};base64,{b64_img}" class="max-w-full h-auto rounded shadow-sm mx-auto" /></div>\n'
        
        doc.close()
        return html_content
    except Exception as e:
        return f"<p class='text-red-500'>Fehler bei der Konvertierung der PDF-Datei: {e}</p>"

def plastex_to_html(file_stream, filename):
    """
    Converts a LaTeX file stream to HTML using plasTeX via subprocess.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Sanitize filename
        safe_filename = filename.replace(" ", "_").replace("..", "")
        tex_path = os.path.join(temp_dir, safe_filename)
        
        try:
            # Save uploaded file
            file_stream.seek(0)
            with open(tex_path, 'wb') as f:
                f.write(file_stream.read())
                
            # Determine plastex executable
            plastex_exe = shutil.which('plastex')
            if not plastex_exe:
                # Fallback to Scripts dir of current python 
                scripts_dir = os.path.dirname(sys.executable)
                candidate = os.path.join(scripts_dir, 'plastex.exe')
                if os.path.exists(candidate):
                    plastex_exe = candidate
                else:
                    candidate = os.path.join(scripts_dir, 'plastex')
                    if os.path.exists(candidate):
                        plastex_exe = candidate
            
            if not plastex_exe:
                 # Last ditch: just try 'plastex' and hope
                 plastex_exe = 'plastex'

            # Run plasTeX
            cmd = [
                plastex_exe,
                '--renderer=HTML5',
                '--split-level=0',
                '--dir=.',
                safe_filename
            ]
            
            # Run process
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir)
            
            # Read the generated index.html
            index_path = os.path.join(temp_dir, 'index.html')
            
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Extract body
                import re
                if '<body>' in html_content:
                    html_content = html_content.split('<body>')[1].split('</body>')[0]
                
                # Fix links: replace 'index.html#...' with '#...'
                html_content = html_content.replace('href="index.html#', 'href="#')
                
                # Remove \label{...} from the content (usually inside equations where plasTeX leaves it)
                html_content = re.sub(r'\\label\{[^}]+\}', '', html_content)

                # Handle Images: Find <img> src="image.png" and replace with base64
                img_tags = re.findall(r'<img[^>]+src="([^">]+)"', html_content)
                for img_file in img_tags:
                    img_full_path = os.path.join(temp_dir, img_file)
                    if os.path.exists(img_full_path):
                        with open(img_full_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                            # Guess mime type
                            ext = img_file.split('.')[-1]
                            mime = f"image/{ext}"
                            if ext == 'svg': mime = 'image/svg+xml'
                            
                            html_content = html_content.replace(img_file, f"data:{mime};base64,{encoded_string}")
                            
                return html_content
            else:
                return f"<p class='text-red-500'>Fehler: plasTeX hat keine Ausgabe erzeugt. <br>Log: {result.stderr[:200]}...</p>"

        except Exception as e:
            return f"<p class='text-red-500'>Systemfehler bei der Konvertierung: {str(e)}</p>"
