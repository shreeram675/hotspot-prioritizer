from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy.future import select
import uuid
from database import get_db, AsyncSessionLocal
from models import StoredImage

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload an image to database and return its URL"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read content
        content = await file.read()
        
        # Create DB record
        image_id = str(uuid.uuid4())
        
        db_image = StoredImage(
            id=image_id,
            filename=file.filename,
            content_type=file.content_type,
            data=content
        )
        
        db.add(db_image)
        await db.commit()
        
        # Return URL
        image_url = f"/upload/image/{image_id}"
        
        return {
            "image_url": image_url,
            "filename": file.filename,
            "id": image_id
        }
    
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/image/{image_id}")
async def get_image(image_id: str):
    """Serve image from database"""
    # Create new session since this might be called directly
    # Note: In async fastapi with async sqlalchemy, we usually need 'await'
    # But for a simple select we can use the async session context
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(StoredImage).where(StoredImage.id == image_id))
        image = result.scalars().first()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
            
        return Response(content=image.data, media_type=image.content_type)
