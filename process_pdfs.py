import os
import json
import datetime
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util

# ------------------------------
# Section 1: Section Extraction
# ------------------------------

def base_outline(pdf_path):
    outline = []
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    size = span.get("size", 0)
                    if size > 17:
                        level = "H1"
                    elif size > 14:
                        level = "H2"
                    elif size > 12:
                        level = "H3"
                    else:
                        continue
                    if len(text) > 3:
                        outline.append({"level": level, "text": text, "page": page_num - 1})
    return outline

def extract_pages(pdf_path):
    sections = []
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        current_section = {"title": None, "body": "", "page": page_num}
        fallback_title = None

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = ""
                is_heading = False

                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    line_text += text + " "
                    font_size = span.get("size", 0)

                    if font_size >= 16:
                        is_heading = True

                line_text = line_text.strip()
                if not line_text:
                    continue

                if is_heading:
                    # Save previous section
                    if current_section["body"]:
                        sections.append({
                            "document": os.path.basename(pdf_path),
                            "page": current_section["page"],
                            "title": current_section["title"] or fallback_title or "Untitled",
                            "text": current_section["body"].strip()
                        })
                    # Start new section
                    current_section = {
                        "title": line_text,
                        "body": "",
                        "page": page_num
                    }
                    fallback_title = None  # reset fallback
                else:
                    # Save fallback title if none yet
                    if not fallback_title and len(line_text) > 15:
                        fallback_title = line_text
                    current_section["body"] += line_text + " "

        if current_section["body"]:
            sections.append({
                "document": os.path.basename(pdf_path),
                "page": current_section["page"],
                "title": current_section["title"] or fallback_title or "Untitled",
                "text": current_section["body"].strip()
            })

    return sections

def extract_outline(pdf_path):
    title = os.path.splitext(os.path.basename(pdf_path))[0]
    outline = base_outline(pdf_path)
    return title, outline

# ------------------------------
# Section 2: Main Pipeline
# ------------------------------

def main():
    input_json_path = "/app/input/challenge1b_input.json"
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    # Load input JSON
    with open(input_json_path, "r") as f:
        data = json.load(f)

    persona = data["persona"]["role"]
    job = data["job_to_be_done"]["task"]
    pdf_files = [doc["filename"] for doc in data["documents"]]
    pdf_paths = [os.path.join(input_dir, f) for f in pdf_files]

    all_sections = []

    for path in pdf_paths:
        all_sections.extend(extract_pages(path))

    # Step 3: Semantic Ranking
    query = f"{persona}. Task: {job}"
    model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
    query_emb = model.encode(query, convert_to_tensor=True)

    for sec in all_sections:
        full_text = sec["title"] + ". " + sec["text"]
        sec_emb = model.encode(full_text, convert_to_tensor=True)
        sec["score"] = util.pytorch_cos_sim(query_emb, sec_emb).item()

    ranked = sorted(all_sections, key=lambda x: x["score"], reverse=True)[:5]

    extracted_sections = []
    subsection_analysis = []

    for idx, sec in enumerate(ranked, start=1):
        extracted_sections.append({
            "document": sec["document"],
            "page_number": sec["page"],
            "section_title": sec["title"],
            "importance_rank": idx
        })
        subsection_analysis.append({
            "document": sec["document"],
            "page_number": sec["page"],
            "refined_text": sec["text"][:1000]  # limit text to 1000 chars for readability
        })

    # Step 4: Save Output JSON
    output = {
        "metadata": {
            "input_documents": pdf_files,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.utcnow().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(os.path.join(output_dir, "final_output.json"), "w") as f:
        json.dump(output, f, indent=2)

# ------------------------------
if __name__ == "__main__":
    main()


