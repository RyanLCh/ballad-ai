from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Dict, Any

from api.core.config import settings
from api.core.logging import get_logger
from api.src.texts.service import TextService


logger = get_logger(__name__)

router = APIRouter(prefix="/texts", tags=["texts"])

def get_text_service():
    return TextService()

@router.post("/process")
async def process_text_file(
    file: UploadFile = File(...), 
    text_service: TextService = Depends(get_text_service)
) -> Dict[str, Any]:
    """
    Process a text file for music generation:
    1. Validate file type and size
    2. Extract text content
    3. Clean and chunkify text
    4. Generate music prompts
    """
    try:
        # Validate file type
        if not file.content_type or file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Only text files are allowed. Received: {file.content_type}"
            )
        
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file provided"
            )
        
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Decode text content
        try:
            text_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = file_content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to decode text file. Please ensure it's a valid text file."
                )
        
        # Process the text
        result = text_service.process_text(text_content, file.filename)
        
        logger.info(f"Successfully processed text file: {file.filename}")
        
        return {
            "success": True,
            "message": f"Successfully processed {file.filename}",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for the texts service"""
    return {
        "status": "ok",
        "service": "texts",
        "settings": {
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024*1024),
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "allowed_file_types": settings.ALLOWED_FILE_TYPES
        }
    }