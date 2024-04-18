from flask import Flask, render_template, request
import fitz  # PyMuPDF

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return 'No file uploaded', 400

    resume = request.files['resume']

    # Check if the file is not empty
    if resume.filename == '':
        return 'No file selected', 400

    # Check if the file has a supported extension (e.g., PDF)
    if not resume.filename.endswith(('.pdf', '.PDF')):
        return 'Unsupported file format', 400

    # Read the uploaded file content in binary mode
    pdf_content = resume.read()

    # Extract text from the resume PDF using PyMuPDF
    text = extract_text_from_pdf(pdf_content)

    # Process the extracted text to extract relevant information
    extracted_data = process_resume_text(text)

    # Render the resume.html template with the extracted data
    return render_template('resume.html', data=extracted_data)

def extract_text_from_pdf(pdf_content):
    """
    Extract text from a PDF byte stream using PyMuPDF.
    """
    text = ""
    with fitz.open(stream=pdf_content, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def process_resume_text(text):
    """
    Process extracted text to extract relevant information.
    For demonstration purposes, let's assume we extract a name and email.
    """
    name = "Smit"
    email = "john.doe@example.com"

    # Store the extracted data in a dictionary
    extracted_data = {
        'name': name,
        'email': email
        # Add other extracted fields as needed
    }
    return extracted_data

if __name__ == '__main__':
    app.run(port=5000, debug=True)
