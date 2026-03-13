from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("/", response_model=CompanyResponse)
async def create_company(company: CompanyCreate, db: AsyncSession = Depends(get_db)):
    db_company = Company(**company.model_dump())
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company

@router.get("/", response_model=List[CompanyResponse])
async def read_companies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(Company).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{company_id}", response_model=CompanyResponse)
async def read_company(company_id: UUID, db: AsyncSession = Depends(get_db)):
    db_company = await db.get(Company, company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: UUID, company: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    db_company = await db.get(Company, company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = company.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)
    
    await db.commit()
    await db.refresh(db_company)
    return db_company

@router.delete("/{company_id}")
async def delete_company(company_id: UUID, db: AsyncSession = Depends(get_db)):
    db_company = await db.get(Company, company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    await db.delete(db_company)
    await db.commit()
    return {"ok": True}
