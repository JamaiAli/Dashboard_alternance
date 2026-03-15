from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.database import get_db
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse)
async def create_application(application: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    # Check for duplicate job_url
    if application.job_url:
        query = select(Application).where(Application.job_url == application.job_url)
        result = await db.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=409, 
                detail="Une candidature avec cette URL existe déjà."
            )

    db_application = Application(**application.model_dump())
    db.add(db_application)
    await db.commit()
    
    query = select(Application).options(selectinload(Application.company)).where(Application.id == db_application.id)
    result = await db.execute(query)
    return result.scalars().first()

@router.get("/check")
async def check_duplicate(url: str, db: AsyncSession = Depends(get_db)):
    query = select(Application).where(Application.job_url == url)
    result = await db.execute(query)
    exists = result.scalars().first() is not None
    return {"exists": exists}

@router.get("/", response_model=List[ApplicationResponse])
async def read_applications(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(Application).options(selectinload(Application.company)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{application_id}", response_model=ApplicationResponse)
async def read_application(application_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Application).options(selectinload(Application.company)).where(Application.id == application_id)
    result = await db.execute(query)
    db_application = result.scalars().first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(application_id: UUID, application: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Application).options(selectinload(Application.company)).where(Application.id == application_id)
    result = await db.execute(query)
    db_application = result.scalars().first()
    
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = application.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_application, key, value)
    
    await db.commit()
    await db.refresh(db_application)
    return db_application

@router.delete("/{application_id}")
async def delete_application(application_id: UUID, db: AsyncSession = Depends(get_db)):
    db_application = await db.get(Application, application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(db_application)
    await db.commit()
    return {"ok": True}
