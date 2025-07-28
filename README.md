# Adobe Hackathon Challenge 1B – Persona-Aware PDF Section Extractor (Dockerized)

This repository contains the Dockerized solution for **Challenge 1B** of the Adobe India Hackathon. It processes PDFs in a persona-driven manner, extracts the most relevant sections based on a provided persona + job-to-be-done, and outputs structured JSON files for each input PDF.

---

## 📁 Directory Structure

Adobe_Hack_ChatGPT_Abusers-1/
├── process_pdfs.py # Main Python script for Challenge 1B
├── requirements.txt # Python dependencies
├── Dockerfile # Docker configuration
├── collection2/
│ ├── PDFs/ # Input PDFs (mounted to /app/input)
│ └── challenge1b_input.json # Input persona/job config file
├── output/ # Output folder for generated JSONs (mounted to /app/output)

yaml
Copy
Edit

---

## 🐳 Docker Build Instructions

Make sure Docker is installed and running.

**Build the Docker image**:

```bash
docker build --platform linux/amd64 -t mysolution1b:123abc .
🚀 Run the Container
Run the container using:

bash
Copy
Edit
docker run --rm \
  -v $(pwd)/collection2/PDFs:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  mysolution1b:123abc
✅ This will automatically process all PDFs in /app/input and create one JSON file per PDF in /app/output.

❗ The HuggingFace model (distiluse-base-multilingual-cased-v2) will require internet access on the first run unless pre-cached.

🧠 Features
🧾 Extracts semantic content from PDFs using:

PyMuPDF

pdfplumber

pdf2image + pytesseract (for OCR)

💬 Multilingual embedding with sentence-transformers

🧠 Computes relevance scores using cosine similarity

🎯 Persona- and job-driven filtering for maximum relevance

🧪 Structured output per file

🧪 Sample Output Format
Each PDF generates a file like filename.json in /app/output, structured as:

json
Copy
Edit
{
  "input_pdf": "sample.pdf",
  "persona": "Hiring Manager",
  "job_to_be_done": "Understand the candidate’s career journey",
  "sections": [
    {
      "page": 2,
      "text": "John has worked at Google for 5 years...",
      "score": 0.92
    },
    ...
  ]
}
🛠 Dependencies
Installed via requirements.txt:

sentence-transformers

transformers

PyMuPDF

pdfplumber

pdf2image

pytesseract

langdetect

pandas

nltk

spacy

networkx

deep-translator

jsonlines

paddleocr

