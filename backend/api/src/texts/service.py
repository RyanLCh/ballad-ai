import uuid
from supabase import AsyncClient, create_async_client
from api.core.config import settings
from api.core.logging import get_logger

logger = get_logger(__name__)

class TextService:
    def __init__(self):
        self.supabase: AsyncClient = create_async_client(
            settings.DATABASE_URL, settings.SUPABASE_KEY
        )
        self.bucket = "texts"

    async def upload(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "application/pdf",
    ) -> dict:
        try:
            file_path = f"{uuid.uuid4().hex}_{filename}"
            
            response = await self.supabase.storage.from_(self.bucket).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": content_type},
            )

            logger.info(f"RESPONSE {response}")

            if response.status_code != 200:
                raise Exception(f"Upload failed: {response.json()}")

            public_url = await self.supabase.storage.from_(self.bucket).get_public_url(file_path)
            
            logger.info(f"Uploaded file: {file_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading file to Supabase: {str(e)}")
            raise