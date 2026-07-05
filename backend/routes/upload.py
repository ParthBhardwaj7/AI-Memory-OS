import os
import shutil
import base64
import openai
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
    Saves PDF locally, indexes it in Cognee, and updates Supabase documents and timeline tables.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    doc_record = None
    try:
        # 1. Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Log initial "processing" record to Supabase
        file_size = os.path.getsize(file_path)
        doc_record = SupabaseDB.log_document(user_id, file.filename, file_path, "PDF", file_size)
        
        # 3. Index PDF in Cognee Cloud
        success = await CogneeService.ingest_file(file_path, user_id)
        
        if not success:
            raise Exception("Cognee failed to cognify PDF file.")
            
        # 4. Update status to completed and create timeline log
        if doc_record:
            SupabaseDB.update_document_status(doc_record["id"], "completed")
            
        SupabaseDB.add_timeline_event(
            user_id=user_id,
            title=f"Uploaded {file.filename}",
            category="PDF",
            description=f"Ingested document '{file.filename}' ({file_size} bytes) successfully into cognitive graph."
        )
        
        return {
            "status": "success",
            "message": f"PDF {file.filename} uploaded and processed successfully",
            "filename": file.filename
        }
    except Exception as e:
        if doc_record:
            SupabaseDB.update_document_status(doc_record["id"], "failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def upload_image(file: UploadFile = File(...), user_id: str = Form("default-user")):
    """
    POST /upload/image
    Uses OpenRouter Vision to perform OCR, ingests text to Cognee, and records logs in Supabase.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    doc_record = None
    try:
        # 1. Save image locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(file_path)
        doc_record = SupabaseDB.log_document(user_id, file.filename, file_path, "Image", file_size)

        # 2. Extract text from image via base64 LLM vision API (glowing cloud OCR)
        extracted_text = ""
        api_key = os.environ.get("LLM_API_KEY")
        if api_key:
            try:
                with open(file_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Check for image type extensions
                mime_type = "image/png" if file.filename.endswith(".png") else "image/jpeg"
                
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                
                # We use google/gemini-2.5-flash as default since it handles multimodal vision excellently
                response = client.chat.completions.create(
                    model="google/gemini-2.5-flash",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Extract all readable text, words, and context from this screenshot/image. Do not describe the image, only output the extracted text verbatim. If no text exists, return an empty string."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]
                )
                extracted_text = response.choices[0].message.content.strip()
            except Exception as ocr_err:
                print(f"Cloud OCR failed, using fallback filename text: {ocr_err}")
        
        if not extracted_text:
            extracted_text = f"Image memory upload: {file.filename} (OCR text empty)"

        # 3. Index text in Cognee
        await CogneeService.ingest_text(extracted_text, user_id)
        
        # 4. Save metadata
        if doc_record:
            SupabaseDB.update_document_status(doc_record["id"], "completed")
            
        # Log to memories table
        SupabaseDB.log_memory(user_id, extracted_text, doc_record.get("id") if doc_record else None, "Image")
        
        SupabaseDB.add_timeline_event(
            user_id=user_id,
            title=f"Uploaded Image {file.filename}",
            category="Image",
            description=f"Processed image memory. Extracted text: {extracted_text[:100]}..."
        )
        
        return {
            "status": "success",
            "message": f"Image {file.filename} processed successfully",
            "extracted_text": extracted_text
        }
    except Exception as e:
        if doc_record:
            SupabaseDB.update_document_status(doc_record["id"], "failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio")
async def upload_audio(file: UploadFile = File(...), user_id: str = Form("default-user")):
    """
    POST /upload/audio
    Transcribes audio speech-to-text, indexes transcript in Cognee, and updates Supabase.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    doc_record = None
    try:
        # 1. Save audio locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(file_path)
        doc_record = SupabaseDB.log_document(user_id, file.filename, file_path, "Audio", file_size)

        # 2. Transcribe speech to text
        transcript = AudioTranscriber.transcribe_audio(file_path)

        # 3. Index text in Cognee
        await CogneeService.ingest_text(transcript, user_id)
        
        # 4. Save metadata
        if doc_record:
            SupabaseDB.update_document_status(doc_record["id"], "completed")
            
        # Log to memories table
        SupabaseDB.log_memory(user_id, transcript, doc_record.get("id") if doc_record else None, "Audio")
        
        SupabaseDB.add_timeline_event(
            user_id=user_id,
            title=f"Transcribed Audio {file.filename}",
            category="Audio",
            description=f"Ingested speech recording notes. Transcript: {transcript[:100]}..."
        )
        
        return {
            "status": "success",
            "message": f"Audio {file.filename} transcribed and ingested",
            "transcript": transcript
        }
    except Exception as e:
        if doc_record:
            SupabaseDB.update_document_status(doc_record["id"], "failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/url")
async def upload_url(url: str = Form(...), user_id: str = Form("default-user")):
    """
    POST /upload/url
    Scrapes website text, indexes it in Cognee, and updates Supabase.
    """
    doc_record = None
    try:
        # 1. Log initial "processing" record
        doc_record = SupabaseDB.log_document(user_id, url, url, "URL", 0)

        # 2. Scrape website body content
        scraped_text = WebScraper.scrape(url)
        if scraped_text.startswith("Failed") or scraped_text.startswith("Error"):
            raise Exception(scraped_text)

        # 3. Index parsed text in Cognee
        await CogneeService.ingest_text(scraped_text, user_id)
        
        # 4. Save metadata
        if doc_record:
            # Update size to matched text length and change status to completed
            SupabaseDB.update_document_status(doc_record["id"], "completed")
            
        # Log to memories table
        SupabaseDB.log_memory(user_id, scraped_text, doc_record.get("id") if doc_record else None, "URL")
        
        SupabaseDB.add_timeline_event(
            user_id=user_id,
            title=f"Bookmarked URL",
            category="URL",
            description=f"Scraped and indexed webpage: {url[:60]}... Extracted {len(scraped_text)} characters."
        )
        
        return {
            "status": "success",
            "message": f"URL {url} scraped and ingested successfully",
            "scraped_snippet": scraped_text[:150]
        }
    except Exception as e:
        if doc_record:
            SupabaseDB.update_document_status(doc_record["id"], "failed")
        raise HTTPException(status_code=500, detail=str(e))
