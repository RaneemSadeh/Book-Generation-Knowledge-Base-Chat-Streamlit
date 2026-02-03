from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from pathlib import Path
from docling.document_converter import DocumentConverter

app = FastAPI()

UPLOAD_DIR = Path("uploaded_files")
OUTPUT_DIR = Path("extracted_docs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.post("/extract/")
async def extract_document(file: UploadFile = File(...)):
    try:
        # Save upload file
        file_location = UPLOAD_DIR / file.filename
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Initialize converter (re-initializing per request is safe but maybe slow; 
        # for production, might want a singleton if model loading is heavy)
        converter = DocumentConverter()
        
        # Convert
        result = converter.convert(file_location)
        md_content = result.document.export_to_markdown()
        
        # Save markdown
        output_filename = f"{file_location.stem}.md"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        return {
            "filename": file.filename, 
            "status": "success", 
            "extracted_file": str(output_path),
            "extracted_content": md_content
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from app.consolidator import generate_summary

CONSOLIDATED_DIR = Path("consolidated_docs")
CONSOLIDATED_DIR.mkdir(exist_ok=True)

@app.post("/consolidate/")
async def consolidate_documents():
    try:
        # 1. Read all markdown files from extracted_docs
        md_files = list(OUTPUT_DIR.glob("*.md"))
        if not md_files:
            raise HTTPException(status_code=404, detail="No extracted documents found to consolidate.")
            
        combined_text = ""
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                combined_text += f"\n\n--- START OF FILE: {md_file.name} ---\n\n"
                combined_text += content
                combined_text += f"\n\n--- END OF FILE: {md_file.name} ---\n\n"
        
        # 2. Call Gemini Consolidator
        summary_md = generate_summary(combined_text)
        
        # 3. Save to consolidated_docs
        output_file = CONSOLIDATED_DIR / "base_context.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary_md)
            
        return {
            "status": "success",
            "message": "Consolidation complete.",
            "file": str(output_file),
            "content_preview": summary_md[:500]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- Chat Endpoint ---
from pydantic import BaseModel
from typing import Optional
from app.chat import chat_with_data
from app import history

class ChatRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.7

@app.post("/sessions/")
async def create_new_session():
    """Creates a new chat session."""
    try:
        session_id = history.create_session()
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/")
async def list_chat_sessions():
    """Lists all available sessions."""
    return history.list_sessions()

@app.get("/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Retrieves history for a specific session."""
    session = history.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/chat/{session_id}")
async def chat_endpoint(session_id: str, request: ChatRequest):
    try:
        # 1. Load the Base Context
        context_file = CONSOLIDATED_DIR / "base_context.md"
        
        if not context_file.exists():
            raise HTTPException(
                status_code=404, 
                detail="Base context not found. Please run /consolidate/ first."
            )
            
        with open(context_file, "r", encoding="utf-8") as f:
            context_content = f.read()
            
        # 2. Get Session History
        session_data = history.get_session(session_id)
        if not session_data:
            # Auto-create if not exists? No, let's be strict.
            raise HTTPException(status_code=404, detail="Session not found")
            
        previous_messages = session_data.get("messages", [])
            
        # 3. Call the chat function with history and temperature
        response_text = chat_with_data(
            user_query=request.prompt, 
            context_content=context_content, 
            history=previous_messages,
            temperature=request.temperature
        )
        
        # 4. Save the interaction to history
        history.save_message(session_id, "user", request.prompt)
        history.save_message(session_id, "assistant", response_text)
        
        return {
            "response": response_text
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
