from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Dict, Any

from api.core.config import settings
from api.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/texts", tags=["texts"])


@router.post("/")
async def upload(
    file: UploadFile = File(...),
):

    if not file.content_type or not file.content_type.startswith("text/"):
        raise HTTPException(
            status_code=400,
            detail="Only text files are allowed. Please upload a .txt file.",
        )

    if file.filename and not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="File must have .txt extension")

    try:
        # Read file content
        content = await file.read()

        # Decode as UTF-8 text
        text = content.decode("utf-8")

        logger.info(
            f"Successfully processed text file: {file.filename}, size: {len(content)} bytes"
        )

        return [
            {"word": "The", "start": 0.0, "end": 0.2, "line": 1},
            {"word": "quick", "start": 0.3, "end": 0.6, "line": 1},
            {"word": "brown", "start": 0.7, "end": 1.0, "line": 1},
            {"word": "fox", "start": 1.1, "end": 1.4, "line": 1},
            {"word": "jumped", "start": 1.5, "end": 1.9, "line": 1},
            {"word": "over", "start": 2.0, "end": 2.3, "line": 1},
            {"word": "the", "start": 2.4, "end": 2.6, "line": 1},
            {"word": "lazy", "start": 2.7, "end": 3.0, "line": 1},
            {"word": "dog.", "start": 3.1, "end": 3.5, "line": 1},
            {"word": "This", "start": 4.0, "end": 4.3, "line": 2},
            {"word": "is", "start": 4.4, "end": 4.6, "line": 2},
            {"word": "the", "start": 4.7, "end": 4.9, "line": 2},
            {"word": "second", "start": 5.0, "end": 5.4, "line": 2},
            {"word": "sentence", "start": 5.5, "end": 5.9, "line": 2},
            {"word": "in", "start": 6.0, "end": 6.2, "line": 2},
            {"word": "our", "start": 6.3, "end": 6.5, "line": 2},
            {"word": "sample", "start": 6.6, "end": 6.9, "line": 2},
            {"word": "text.", "start": 7.0, "end": 7.4, "line": 2},
            {"word": "Reading", "start": 8.0, "end": 8.4, "line": 3},
            {"word": "speed", "start": 8.5, "end": 8.8, "line": 3},
            {"word": "can", "start": 8.9, "end": 9.1, "line": 3},
            {"word": "vary", "start": 9.2, "end": 9.5, "line": 3},
            {"word": "depending", "start": 9.6, "end": 10.1, "line": 3},
            {"word": "on", "start": 10.2, "end": 10.4, "line": 3},
            {"word": "the", "start": 10.5, "end": 10.7, "line": 3},
            {"word": "complexity", "start": 10.8, "end": 11.4, "line": 3},
            {"word": "of", "start": 11.5, "end": 11.7, "line": 3},
            {"word": "the", "start": 11.8, "end": 12.0, "line": 3},
            {"word": "content.", "start": 12.1, "end": 12.6, "line": 3},
            {"word": "Each", "start": 13.0, "end": 13.3, "line": 4},
            {"word": "sentence", "start": 13.4, "end": 13.8, "line": 4},
            {"word": "will", "start": 13.9, "end": 14.1, "line": 4},
            {"word": "be", "start": 14.2, "end": 14.4, "line": 4},
            {"word": "highlighted", "start": 14.5, "end": 15.1, "line": 4},
            {"word": "for", "start": 15.2, "end": 15.4, "line": 4},
            {"word": "its", "start": 15.5, "end": 15.7, "line": 4},
            {"word": "entire", "start": 15.8, "end": 16.2, "line": 4},
            {"word": "duration.", "start": 16.3, "end": 18.8, "line": 4},
        ]

    except UnicodeDecodeError as e:
        logger.error(f"Failed to decode file {file.filename} as UTF-8: {str(e)}")
        raise HTTPException(
            status_code=400, detail="File must be valid UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while processing file"
        )
