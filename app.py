import os
import json
import json_repair
import uuid
import base64
import requests
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from dotenv import load_dotenv

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents

# Load environment variables
load_dotenv(override=True)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Constants and Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, 'generated_pdfs')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

AI_MODEL = os.getenv('AI_MODEL', 'google/gemini-2.5-pro')

def fetch_pexels_image(query):
    pexels_key = os.getenv('PEXELS_API_KEY', '')
    if not pexels_key:
        print("Warning: Pexels API key not set. Skipping image fetch.")
        return None
        
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": pexels_key}
    params = {"query": query + " electronic hardware white background", "per_page": 1, "orientation": "landscape"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('photos') and len(data['photos']) > 0:
            img_url = data['photos'][0]['src']['medium']
            img_response = requests.get(img_url)
            
            filename = f"pexels_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(ASSETS_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            return filepath
    except Exception as e:
        print(f"Error fetching image from Pexels for query '{query}': {e}")
    return None

def fetch_mermaid_flowchart(mermaid_code):
    try:
        # Mermaid.ink requires base64 encoded graph definition
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        url = f"https://mermaid.ink/img/{encoded}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        filename = f"flowchart_{uuid.uuid4().hex}.png"
        filepath = os.path.join(ASSETS_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath
    except Exception as e:
        print(f"Error generating flowchart: {e}")
    return None

def generate_report_data(topic, requirements):
    openrouter_key = os.getenv('OPENROUTER_API_KEY', '')
    print(f"DEBUG KEY: {openrouter_key[:10]}...{openrouter_key[-5:]}", flush=True)
    if not openrouter_key:
        raise ValueError("OpenRouter API key is missing in .env")
    prompt = f"""
    You are an expert engineering professor. Generate a comprehensive, professional engineering project report based on the following:
    Topic: {topic}
    Requirements: {requirements}

    You MUST output the result in STRICT JSON format with NO markdown wrapping (no ```json ... ```, just the raw object).
    
    The JSON MUST have exactly this structure:
    {{
      "project_title": "Full project title here",
      "sections": [
        {{ "title": "1. Cover Page", "type": "cover", "author": "Student Name", "guide": "Professor Name", "institution": "University Name" }},
        {{ "title": "2. Certificate Page", "type": "certificate" }},
        {{ "title": "3. Abstract", "type": "standard", "content": "Abstract text here...", "subheadings": [] }},
        {{ "title": "4. Complete Product Idea", "type": "standard", "subheadings": [ {{"title": "Product Vision & Overview", "text": "Explain the full product concept from a user perspective...", "image_query": "product prototype"}} ] }},
        {{ "title": "5. Components Required", "type": "components_table", "components": [ {{"sno": "1", "name": "ESP32", "qty": "1", "desc": "Main controller", "image_query": "ESP32 board"}} ] }},
        {{ "title": "6. Sensor & Hardware Breakdown", "type": "standard", "subheadings": [ {{"title": "Sensor 1 (e.g. DHT11)", "text": "Detailed explanation of sensor...", "image_query": "DHT11 sensor"}}, {{"title": "Sensor 2", "text": "Detailed explanation...", "image_query": "sensor module"}} ] }},
        {{ "title": "7. Software Description", "type": "standard", "subheadings": [...] }},
        {{ "title": "8. System Workflow & Working Principle", "type": "standard", "subheadings": [ {{"title": "Step-by-Step Workflow", "text": "Explain the operational flow...", "image_query": "engineering process"}} ] }},
        {{ "title": "9. Circuit Diagram", "type": "standard", "subheadings": [ {{"title": "9.1 Wiring details", "text": "...", "image_query": "breadboard circuit wiring"}} ] }},
        {{ "title": "10. Flowchart", "type": "flowchart", "mermaid_code": "graph TD;\\nA[Start]-->B[Read Sensors];\\nB-->C{{Threshold met?}};\\nC-->|Yes|D[Turn on Relay];\\nC-->|No|B;\\nD-->E[End];" }},
        {{ "title": "11. Results", "type": "standard", "subheadings": [...] }},
        {{ "title": "12. Advantages", "type": "standard", "subheadings": [...] }},
        {{ "title": "13. Applications", "type": "standard", "subheadings": [...] }},
        {{ "title": "14. Future Scope", "type": "standard", "subheadings": [...] }},
        {{ "title": "15. Conclusion", "type": "standard", "subheadings": [...] }},
        {{ "title": "16. References", "type": "standard", "subheadings": [ {{"title": "Links", "text": "1. link... 2. link...", "image_query": ""}} ] }},
        {{ "title": "17. Final Connection Guide", "type": "standard", "subheadings": [ {{"title": "Pin Mapping", "text": "...", "image_query": ""}} ] }}
      ]
    }}
    
    IMPORTANT RULES:
    1. Be highly technical, use engineering terminology, real formulas, and accurate descriptions.
    2. Write extensively: Main section 'content' MUST be around 1000 characters. Subheading 'text' MUST be around 600 characters.
    3. EVERY subheading and EVERY component in the table MUST have an 'image_query' (short 2-3 words) to display an image.
    4. For Section 6, explicitly list EVERY sensor/major component as its own subheading.
    5. Ensure the JSON is valid and escaped correctly.
    """

    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Engineering Report Generator"
    }
    
    payload = {
        "model": AI_MODEL,
        "max_tokens": 8000,
        "messages": [
            {"role": "system", "content": "You are a JSON-generating bot for engineering reports. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    models_to_try = [
        AI_MODEL,
        "openrouter/free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "google/gemma-2-27b-it:free"
    ]
    
    response_data = None
    last_error = None
    
    for model_name in models_to_try:
        payload["model"] = model_name
        print(f"Attempting generation with model: {model_name}...", flush=True)
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            
            res_json = r.json()
            choices = res_json.get('choices', [])
            if not choices:
                raise ValueError("OpenRouter API returned an empty choices list.")
            
            message = choices[0].get('message', {})
            response_text = message.get('content')
            if not response_text:
                raise ValueError("AI model returned empty message content.")
                
            response_text = response_text.strip()
            
            # Strip markdown if the AI mistakenly included it
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'^```\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            # Extract JSON object if there is surrounding conversational text
            match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if match:
                response_text = match.group(1)
                
            # Use json_repair to automatically fix minor syntax errors like missing commas or quotes
            data = json_repair.loads(response_text)
            # Handle potential double-serialization
            if isinstance(data, str):
                data = json_repair.loads(data)
            if not isinstance(data, dict):
                raise ValueError("AI response did not resolve to a JSON dictionary object.")
                
            response_data = data
            print(f"Successfully generated and parsed content with {model_name}!", flush=True)
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}. Trying next fallback...", flush=True)
            last_error = e
            
    if not response_data:
        raise RuntimeError(f"All AI models failed to generate content. Last error: {last_error}")
        
    return response_data


class ReportFooterTemplate(PageTemplate):
    def __init__(self, id, project_title):
        self.project_title = project_title
        frames = [Frame(inch, inch, A4[0] - 2*inch, A4[1] - 2*inch, id='normal')]
        super().__init__(id, frames=frames)

    def beforeDrawPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        # Full page outer border
        canvas.setStrokeColor(colors.HexColor('#1e293b')) # Slate 800
        canvas.setLineWidth(1)
        # Draw rectangle at 0.4 inch margin
        canvas.rect(0.4*inch, 0.4*inch, A4[0] - 0.8*inch, A4[1] - 0.8*inch)
        
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(0.5)
        # Header line
        canvas.line(inch, A4[1] - 0.7*inch, A4[0] - inch, A4[1] - 0.7*inch)
        
        # Footer line
        canvas.line(inch, 0.7*inch, A4[0] - inch, 0.7*inch)
        
        # Footer text
        date_str = datetime.now().strftime("%Y-%m-%d")
        canvas.drawString(inch, 0.5*inch, f"Project: {self.project_title[:50]}...")
        canvas.drawRightString(A4[0] - inch, 0.5*inch, f"Date: {date_str} | Page {doc.page}")
        
        canvas.restoreState()


def prefetch_images(report_data):
    queries = set()
    for section in report_data.get('sections', []):
        stype = section.get('type', 'standard')
        if stype == 'components_table':
            for comp in section.get('components', []):
                q = comp.get('image_query')
                if not q or not q.strip():
                    q = comp.get('name', 'electronic component')
                if q:
                    queries.add(q.strip())
        elif stype == 'flowchart':
            pass
        elif stype not in ['cover', 'certificate']:
            for sub in section.get('subheadings', []):
                q = sub.get('image_query')
                if not q or not q.strip():
                    q = sub.get('title', '')
                if q and q.lower() not in ["links", "references", "abstract"]:
                    queries.add(q.strip())
                    
    image_map = {}
    if not queries:
        return image_map
        
    print(f"Prefetching {len(queries)} images in parallel...", flush=True)
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_query = {executor.submit(fetch_pexels_image, q): q for q in queries}
        for future in future_to_query:
            q = future_to_query[future]
            try:
                path = future.result()
                if path:
                    image_map[q] = path
            except Exception as e:
                print(f"Error prefetching image for query '{q}': {e}", flush=True)
                
    return image_map


def build_pdf(report_data, filepath):
    doc = BaseDocTemplate(filepath, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    doc.addPageTemplates([ReportFooterTemplate('Normal', report_data.get('project_title', 'Engineering Report'))])
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(name='CoverTitle', parent=styles['Heading1'], fontSize=28, spaceAfter=30, alignment=1, textColor=colors.HexColor('#1e293b')))
    styles.add(ParagraphStyle(name='CoverSub', parent=styles['Normal'], fontSize=16, spaceAfter=20, alignment=1))
    styles.add(ParagraphStyle(name='MainHeading', parent=styles['Heading1'], fontSize=18, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor('#0f172a'), keepWithNext=True))
    styles.add(ParagraphStyle(name='SubHeading', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor('#334155'), keepWithNext=True))
    styles.add(ParagraphStyle(name='BodyTextCustom', parent=styles['BodyText'], fontSize=11, leading=16, spaceAfter=12, alignment=4)) # Justified
    styles.add(ParagraphStyle(name='TableText', parent=styles['Normal'], fontSize=10, leading=14, alignment=0)) # Left aligned for tables
    styles.add(ParagraphStyle(name='TableTextCenter', parent=styles['Normal'], fontSize=10, leading=14, alignment=1)) # Center aligned for tables
    
    def sanitize_text(text):
        if not text: return ""
        text = str(text)
        replacements = {
            '—': '-', '–': '-', '•': '-', '“': '"', '”': '"', '‘': "'", '’': "'", 
            '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
            '\u2022': '-', '\u25a0': '-', '\u25cf': '-'
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        # Fallback for any other non-ascii character that reportlab helvetica might struggle with
        return text.encode('ascii', 'ignore').decode('ascii')

    image_map = prefetch_images(report_data)
    story = []
    
    for section in report_data.get('sections', []):
        stype = section.get('type', 'standard')
        
        if stype == 'cover':
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph("ENGINEERING PROJECT REPORT", styles['CoverTitle']))
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph(sanitize_text(report_data.get('project_title', 'Project Title')).upper(), styles['CoverTitle']))
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph(sanitize_text(f"Submitted By: {section.get('author', 'Student')}"), styles['CoverSub']))
            story.append(Paragraph(sanitize_text(f"Guided By: {section.get('guide', 'Professor')}"), styles['CoverSub']))
            story.append(Paragraph(sanitize_text(f"{section.get('institution', 'University')}"), styles['CoverSub']))
            story.append(PageBreak())
            
        elif stype == 'certificate':
            story.append(Paragraph(sanitize_text(section.get('title', 'Certificate')), styles['MainHeading']))
            story.append(Spacer(1, 1*inch))
            cert_text = f"This is to certify that the project entitled '{report_data.get('project_title', '')}' is a bonafide record of work carried out successfully for the engineering curriculum."
            story.append(Paragraph(sanitize_text(cert_text), styles['BodyTextCustom']))
            story.append(Spacer(1, 3*inch))
            story.append(Paragraph("Signature of Guide                                      Signature of HOD", styles['BodyTextCustom']))
            story.append(PageBreak())
            
        elif stype == 'components_table':
            story.append(Paragraph(sanitize_text(section.get('title', 'Components Required')), styles['MainHeading']))
            
            table_data = [['S.No', 'Component', 'Qty', 'Description', 'Image']]
            for comp in section.get('components', []):
                image_query = comp.get('image_query')
                if not image_query or not image_query.strip():
                    image_query = comp.get('name', 'electronic component')
                image_query = image_query.strip() if image_query else ""
                
                img_path = image_map.get(image_query)
                # Use a slightly smaller image to prevent overlap in the column, and preserve aspect ratio if possible
                img_flowable = Image(img_path, width=1.2*inch, height=0.8*inch, kind='proportional') if img_path else ""
                
                name_clean = sanitize_text(comp.get('name', ''))
                desc_clean = sanitize_text(comp.get('desc', ''))
                
                table_data.append([
                    comp.get('sno', ''),
                    Paragraph(name_clean, styles['TableTextCenter']),
                    comp.get('qty', ''),
                    Paragraph(desc_clean, styles['TableText']),
                    img_flowable
                ])
                
            t = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 0.5*inch, 2*inch, 1.7*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('ALIGN', (3,1), (3,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('WORDWRAP', (0,0), (-1,-1), True)
            ]))
            story.append(t)
            story.append(PageBreak())
            
        elif stype == 'flowchart':
            story.append(Paragraph(sanitize_text(section.get('title', 'Flowchart')), styles['MainHeading']))
            mermaid = section.get('mermaid_code', '')
            if mermaid:
                img_path = fetch_mermaid_flowchart(mermaid)
                if img_path:
                    # scale down if too large
                    img = Image(img_path, kind='proportional')
                    img.drawHeight = 4*inch
                    img.drawWidth = 5*inch
                    img.hAlign = 'CENTER'
                    story.append(img)
                else:
                    story.append(Paragraph("Flowchart generation failed.", styles['BodyTextCustom']))
            story.append(PageBreak())
            
        else: # standard
            section_story = [Paragraph(sanitize_text(section.get('title', 'Section')), styles['MainHeading'])]
            
            if section.get('content'):
                section_story.append(Paragraph(sanitize_text(section.get('content', '')), styles['BodyTextCustom']))
                
            for i, sub in enumerate(section.get('subheadings', [])):
                section_story.append(Paragraph(sanitize_text(sub.get('title', '')), styles['SubHeading']))
                
                # AI models sometimes use 'content' or 'description' instead of 'text'
                sub_text = sub.get('text', sub.get('content', sub.get('description', '')))
                if sub_text:
                    section_story.append(Paragraph(sanitize_text(sub_text), styles['BodyTextCustom']))
                
                # Fetch and add image if queried (or use subheading title as fallback)
                image_query = sub.get('image_query')
                if not image_query or not image_query.strip():
                    image_query = sub.get('title', '')
                image_query = image_query.strip() if image_query else ""
                
                # We skip references or links page images as they are text links
                if image_query and image_query.lower() not in ["links", "references", "abstract"]:
                    img_path = image_map.get(image_query)
                    if img_path:
                        img = Image(img_path, width=4*inch, height=2.5*inch, kind='proportional')
                        img.hAlign = 'CENTER'
                        section_story.append(Spacer(1, 10))
                        section_story.append(img)
                        section_story.append(Paragraph(sanitize_text(f"Figure: {sub.get('title', 'Component')}"), ParagraphStyle(name='caption', parent=styles['Normal'], alignment=1, fontSize=9, textColor=colors.grey)))
                        section_story.append(Spacer(1, 10))
            
            story.extend(section_story)
            story.append(Spacer(1, 0.5*inch))
            
    doc.build(story)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    if request.is_json:
        data = request.json
        topic = data.get('topic')
        requirements = data.get('requirements', '')
    else:
        topic = request.form.get('topic')
        requirements = request.form.get('requirements', '')
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
        
    try:
        print(f"Generating report for: {topic}")
        # 1. Fetch JSON structured content from OpenRouter
        report_data = generate_report_data(topic, requirements)
        
        # 2. Build PDF Document
        # Create a safe filename from the topic
        topic_safe = re.sub(r'[^a-zA-Z0-9_\- ]', '', topic).strip()
        topic_safe = topic_safe.replace(' ', '_')[:60]
        if not topic_safe:
            topic_safe = "Engineering_Report"
            
        filename = f"{topic_safe}.pdf"
        filepath = os.path.join(PDF_DIR, filename)
        
        build_pdf(report_data, filepath)
        
        pdf_url = url_for('download_pdf', filename=filename)
        view_url = url_for('view_pdf', filename=filename)
        return jsonify({"success": True, "pdf_url": pdf_url, "view_url": view_url})
        
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>')
def download_pdf(filename):
    return send_from_directory(PDF_DIR, filename, as_attachment=True, download_name=filename, mimetype='application/pdf')

@app.route('/view/<filename>')
def view_pdf(filename):
    return send_from_directory(PDF_DIR, filename, mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
