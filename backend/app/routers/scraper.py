from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.scraping_service import ScrapingService

router = APIRouter(prefix="/scraper", tags=["scraper"])


class ScrapeRequest(BaseModel):
    url: str


class ScrapeResponse(BaseModel):
    url: str
    raw_text: str
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    contract_type: Optional[str] = None
    sector: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    description: Optional[str] = None
    benefits: Optional[str] = None


@router.post("/", response_model=ScrapeResponse)
async def scrape_job_offer(request: ScrapeRequest):
    data = ScrapingService.extract_structured_data(request.url)

    if data["raw_text"].startswith("Error extracting"):
        raise HTTPException(status_code=400, detail=data["raw_text"])

    return ScrapeResponse(
        url=request.url,
        raw_text=data["raw_text"],
        company_name=data.get("company_name"),
        job_title=data.get("job_title"),
        contract_type=data.get("contract_type"),
        sector=data.get("sector"),
        location=data.get("location"),
        salary=data.get("salary"),
        description=data.get("description"),
        benefits=data.get("benefits"),
    )
