from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Dict, Any

from api.core.config import settings
from api.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/texts", tags=["texts"])


@router.post("/")
async def upload(
    file: UploadFile = File(...),
) -> Dict[str, Any]:

    if not file.content_type or not file.content_type.startswith("text/"):
        raise HTTPException(
            status_code=400, 
            detail="Only text files are allowed. Please upload a .txt file."
        )
    
    if file.filename and not file.filename.lower().endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="File must have .txt extension"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Decode as UTF-8 text
        text = content.decode('utf-8')
        
        logger.info(f"Successfully processed text file: {file.filename}, size: {len(content)} bytes")
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(content),
            "text": text
        }
        
    except UnicodeDecodeError as e:
        logger.error(f"Failed to decode file {file.filename} as UTF-8: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail="File must be valid UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while processing file"
        )
