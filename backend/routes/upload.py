import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.cognee_service import CogneeService
from services.transcribing import AudioTranscriber
from services.scraper import WebScraper
from db.supabase import SupabaseDB

router = APIRouter()

# Temporary upload folder
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...), user_id: str = Form("default-user")):
    """
    POST /upload/pdf
    
    TODO IMPLEMENTATION STEPS:
    1. Validate that the file is a PDF (check content_type or extension).
    2. Save the file to the local `uploads/` directory.
    3. Call `CogneeService.ingest_text` or `CogneeService.ingest_file` to process the document.
    4. Log the document details (filename, path, size) in Supabase via `SupabaseDB.log_document`.
    5. Log a timeline event in Supabase: "Uploaded PDF [filename]".
    6. Return a success response with the status and parsed message.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Cognee ingestion placeholder
        # CogneeService.ingest_pdf(file_path, user_id)
        
        # Supabase logging placeholders
        # SupabaseDB.log_document(user_id, file.filename, file_path, "PDF", os.path.getsize(file_path))
        # SupabaseDB.add_timeline_event(user_id, f"Uploaded {file.filename}", "PDF", f"Ingested PDF into cognitive memory")
        
        return {
            "status": "success",
            "message": f"PDF {file.filename} uploaded and processed successfully",
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def upload_image(file: UploadFile = File(...), user_id: str = Form("default-user")):
    """
    POST /upload/image
    
    TODO IMPLEMENTATION STEPS:
    1. Validate that the file is an image.
    2. Save the file to the `uploads/` directory.
    3. (Optional) Run OCR on the image to extract text, or pass image description to Cognee.
    4. Ingest text/image data into Cognee memory space.
    5. Log the metadata and save a timeline event: "Uploaded Image [filename]".
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # TODO: Implement OCR / Image description logic here
        extracted_text = f"Image upload: {file.filename}"
        
        # Ingest memory
        # CogneeService.ingest_text(extracted_text, user_id)
        
        # Log to Supabase
        # SupabaseDB.log_document(user_id, file.filename, file_path, "Image", os.path.getsize(file_path))
        # SupabaseDB.add_timeline_event(user_id, f"Uploaded Image {file.filename}", "Image", "Processed image memory")
        
        return {
            "status": "success",
            "message": f"Image {file.filename} processed successfully",
            "extracted_text": extracted_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio")
async def upload_audio(file: UploadFile = File(...), user_id: str = Form("default-user")):
    """
    POST /upload/audio
    
    TODO IMPLEMENTATION STEPS:
    1. Save the audio file (.mp3, .wav, etc.) to the `uploads/` directory.
    2. Call `AudioTranscriber.transcribe_audio(file_path)` to get text transcripts.
    3. Ingest the transcribed text into Cognee memory.
    4. Log the document details and insert a timeline event: "Transcribed meeting recording".
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Transcribe audio using Whisper or Gemini API
        # transcript = AudioTranscriber.transcribe_audio(file_path)
        transcript = "Sample audio transcript: This meeting discussed next steps for project development."
        
        # Ingest memory
        # CogneeService.ingest_text(transcript, user_id)
        
        # Log to Supabase
        # SupabaseDB.log_document(user_id, file.filename, file_path, "Audio", os.path.getsize(file_path))
        # SupabaseDB.add_timeline_event(user_id, f"Transcribed Audio {file.filename}", "Audio", "Ingested meeting notes")
        
        return {
            "status": "success",
            "message": f"Audio {file.filename} transcribed and ingested",
            "transcript": transcript
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/url")
async def upload_url(url: str = Form(...), user_id: str = Form("default-user")):
    """
    POST /upload/url
    
    TODO IMPLEMENTATION STEPS:
    1. Fetch the webpage using requests.
    2. Call `WebScraper.scrape(url)` using BeautifulSoup to scrape article body text.
    3. Ingest the parsed text contents into Cognee cognitive memory.
    4. Log the URL details in database documents.
    5. Log a timeline event: "Bookmarked Web Page".
    """
    try:
        # Scrape web content
        # page_content = WebScraper.scrape(url)
        page_content = f"Scraped content from webpage: {url}"
        
        # Ingest into Cognee
        # CogneeService.ingest_text(page_content, user_id)
        
        # Log to Supabase
        # SupabaseDB.log_document(user_id, url, url, "URL", len(page_content))
        # SupabaseDB.add_timeline_event(user_id, f"Saved URL: {url}", "URL", "Bookmarked content details stored")
        
        return {
            "status": "success",
            "message": f"URL {url} scraped and ingested successfully",
            "scraped_snippet": page_content[:150]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
