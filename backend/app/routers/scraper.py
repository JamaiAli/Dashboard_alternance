from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.scraping_service import ScrapingService

router = APIRouter(prefix="/scraper", tags=["scraper"])

class ScrapeRequest(BaseModel):
    url: str

class ScrapeResponse(BaseModel):
    url: str
    raw_text: str

@router.post("/", response_model=ScrapeResponse)
async def scrape_job_offer(request: ScrapeRequest):
    text = ScrapingService.extract_text_from_url(request.url)
    if text.startswith("Error extracting"):
        raise HTTPException(status_code=400, detail=text)
    return ScrapeResponse(url=request.url, raw_text=text)
