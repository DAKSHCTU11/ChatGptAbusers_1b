FROM --platform=linux/amd64 python:3.10

WORKDIR /app

# Copy the script and dependencies
COPY process_pdfs.py .
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Run the PDF processing script
CMD ["python", "process_pdfs.py"]
