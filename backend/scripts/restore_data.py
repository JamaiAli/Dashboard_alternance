import asyncio
import os
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

# Modèles
from app.models.company import Company
from app.models.application import Application, ApplicationStatus, ApplicationType
from app.models.document import Document, DocumentType

# Configuration
DATABASE_URL = "postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm_db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def restore_from_uploads():
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print(f"Directory {uploads_dir} not found.")
        return

    files = os.listdir(uploads_dir)
    applications_to_restore = {}

    for file in files:
        if not file.endswith(".pdf"):
            continue
            
        parts = file.split("_", 2)
        if len(parts) >= 3:
            app_id_str, doc_type_str, version_name_with_ext = parts
            
            try:
                app_id = UUID(app_id_str)
            except ValueError:
                continue
                
            doc_type = DocumentType.CV if doc_type_str.upper() == "CV" else DocumentType.LM
            version_name = version_name_with_ext.rsplit(".", 1)[0]
            
            if app_id not in applications_to_restore:
                applications_to_restore[app_id] = {
                    "company_name": f"Entreprise {version_name.capitalize()} ({str(app_id)[:4]})",
                    "documents": []
                }
            
            applications_to_restore[app_id]["documents"].append({
                "type": doc_type,
                "version_name": version_name,
                "file_path": os.path.join(uploads_dir, file)
            })

    async with AsyncSessionLocal() as db:
        for app_id, data in applications_to_restore.items():
            # Check if app already exists
            existing_app = await db.get(Application, app_id)
            if existing_app:
                continue

            # Create Company
            company = Company(
                id=uuid4(),
                name=data["company_name"],
                sector="Inconnu",
                tech_stack=["À définir"]
            )
            db.add(company)
            await db.flush()

            # Create Application
            app = Application(
                id=app_id,
                company_id=company.id,
                status=ApplicationStatus.APPLIED,
                type=ApplicationType.ALTERNANCE,
                raw_description="Candidature restaurée à partir des documents uploadés."
            )
            db.add(app)
            
            # Create Documents
            for doc_data in data["documents"]:
                doc = Document(
                    application_id=app_id,
                    type=doc_data["type"],
                    version_name=doc_data["version_name"],
                    file_path=doc_data["file_path"]
                )
                db.add(doc)
                
        await db.commit()
        print(f"Restauration terminée : {len(applications_to_restore)} candidatures recréées.")

if __name__ == "__main__":
    asyncio.run(restore_from_uploads())
