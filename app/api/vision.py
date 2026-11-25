import os
import tempfile
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.database.models import Ticket, TicketMessage
from app.security import get_current_user, require_ticket_access
from app.services.vision_service import analyze_image_async

router = APIRouter(prefix="/api/v1/vision", tags=["Computer Vision"])
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


@router.post("/tickets/{ticket_id}/analyze")
async def analyze_ticket_image(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    require_ticket_access(ticket, user)

    max_bytes = settings.MAX_VISION_UPLOAD_MB * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if not content or len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Image must be between 1 byte and {settings.MAX_VISION_UPLOAD_MB} MB.",
        )

    try:
        with Image.open(BytesIO(content)) as image:
            image_format = image.format
            if image_format not in SUPPORTED_FORMATS:
                raise HTTPException(status_code=415, detail="Upload a JPEG, PNG or WebP image.")
            image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid or safe image.")

    suffix = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[image_format]
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(content)
            temp_path = temp.name

        result = await analyze_image_async(temp_path)
        evidence_text = result["visual_description"]
        db.add(TicketMessage(
            ticket_id=ticket.id,
            customer_id=ticket.customer_id,
            sender_type="customer",
            message=f"Visual evidence (Mirage): {evidence_text}",
        ))
        db.commit()
        return {"ticket_id": ticket.id, **result}
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail="Vision analysis failed. Check backend logs.") from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
