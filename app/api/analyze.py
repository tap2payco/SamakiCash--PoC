from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models import FishCatchRequest
from app.agents.orchestrator import orchestrate_analysis

router = APIRouter()

@router.post("/analyze-catch")
async def analyze_catch(request: FishCatchRequest, background_tasks: BackgroundTasks):
    """
    Analyze a fisher's catch:
    - call Mistral for price analysis
    - call an AI/ML API for market insights
    - optionally call Nebius for image analysis
    - optionally generate a voice file via ElevenLabs
    - store the record in background
    Returns a safe, renderable analysis_summary plus detailed JSON pieces.
    """
    try:
        # Run the complete analysis workflow
        result = await orchestrate_analysis(request.dict())
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "Processing failed"))
        
        return result

    except Exception as e:
        # If something truly unexpected happens, return a 500 with error info
        print(f"[analyze_catch] Fatal error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
