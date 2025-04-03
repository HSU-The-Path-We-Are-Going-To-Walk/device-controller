from fastapi import APIRouter
from services.yolo_tracker import track_people

router = APIRouter()

@router.on_event("startup")
def start_tracking():
    track_people()