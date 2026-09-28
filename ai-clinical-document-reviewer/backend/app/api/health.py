from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health check endpoint")
def health_check():
    """Health check endpoint to verify backend service operational status."""
    return {"status": "healthy"}
