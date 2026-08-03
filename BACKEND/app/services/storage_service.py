import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.core.config import settings


class StorageService:
    """
    Storage service abstraction for handling file uploads.
    Supports local storage for development and can be extended for cloud storage.
    """
    
    # Local storage configuration
    LOCAL_STORAGE_PATH = Path("BACKEND/uploads/vehicles")
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @classmethod
    def validate_file(cls, file: UploadFile) -> None:
        """Validate uploaded file type and size"""
        # Check file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size (read first chunk to estimate)
        # Note: For precise size checking, you'd need to read the entire file
        # This is a basic check - production should use middleware for size limits
    
    @classmethod
    def generate_filename(cls, original_filename: str) -> str:
        """Generate a unique filename while preserving extension"""
        file_extension = original_filename.split(".")[-1].lower()
        unique_id = str(uuid.uuid4())
        return f"vehicle_{unique_id}.{file_extension}"
    
    @classmethod
    def save_local(cls, file: UploadFile, filename: Optional[str] = None) -> str:
        """
        Save file to local storage.
        Returns the relative URL path for database storage.
        """
        # Ensure directory exists
        cls.LOCAL_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            filename = cls.generate_filename(file.filename)
        
        # Save file
        file_path = cls.LOCAL_STORAGE_PATH / filename
        
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Return URL path (relative to uploads directory)
        return f"/uploads/vehicles/{filename}"
    
    @classmethod
    def delete_local(cls, file_url: str) -> bool:
        """Delete file from local storage"""
        try:
            # Extract filename from URL
            filename = file_url.split("/")[-1]
            file_path = cls.LOCAL_STORAGE_PATH / filename
            
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    @classmethod
    def get_file_url(cls, relative_path: str) -> str:
        """
        Get full URL for a file.
        In development, this returns a local path.
        In production, this would return CDN/cloud storage URL.
        """
        # For local development
        return relative_path
    
    @classmethod
    def upload_vehicle_image(
        cls,
        file: UploadFile,
        vehicle_id: Optional[int] = None
    ) -> str:
        """
        Upload a vehicle image and return the URL.
        """
        cls.validate_file(file)
        
        # Generate filename with vehicle_id if available
        if vehicle_id:
            ext = file.filename.split(".")[-1].lower()
            filename = f"vehicle_{vehicle_id}_{uuid.uuid4().hex[:8]}.{ext}"
        else:
            filename = cls.generate_filename(file.filename)
        
        # Save and return URL
        relative_url = cls.save_local(file, filename)
        return cls.get_file_url(relative_url)
    
    @classmethod
    def delete_vehicle_image(cls, image_url: str) -> bool:
        """Delete a vehicle image"""
        return cls.delete_local(image_url)


# Singleton instance
storage_service = StorageService()
