import os
import uuid

from fastapi import UploadFile, HTTPException


UPLOAD_DIR = "uploads"


def save_image(image: UploadFile) -> str:
    # Make sure uploads folder exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Validate image type
    if not image.content_type:
        raise HTTPException(
            status_code=400,
            detail="Invalid image"
        )

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    # Get file extension
    extension = os.path.splitext(image.filename)[1].lower()

    # Generate unique filename
    filename = f"{uuid.uuid4()}{extension}"

    # Full file path
    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    # Save image
    with open(file_path, "wb") as buffer:
        buffer.write(image.file.read())

    return file_path