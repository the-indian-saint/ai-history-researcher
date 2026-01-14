from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...services.tts_service import tts_service
from ...services.image_service import image_service

router = APIRouter()

class AudioRequest(BaseModel):
    text: str

class ImageRequest(BaseModel):
    prompt: str

class GenerationResponse(BaseModel):
    url: str

@router.post("/audio", response_model=GenerationResponse)
async def generate_audio_endpoint(request: AudioRequest):
    """Generate audio from text."""
    try:
        url = await tts_service.generate_audio(request.text)
        return GenerationResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image", response_model=GenerationResponse)
async def generate_image_endpoint(request: ImageRequest):
    """Generate historical image from prompt."""
    try:
        url = await image_service.generate_image(request.prompt)
        return GenerationResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
