import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Optional


class ScrapingService:

    @staticmethod
    def extract_text_from_url(url: str) -> str:
        """Extracts raw text content from the given URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text(separator=' ', strip=True)
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            return cleaned_text
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    @staticmethod
    def extract_structured_data(url: str) -> dict:
        """
        Extracts structured job data from a URL.
        Returns a dict with: raw_text, company_name, job_title, contract_type, sector.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Extract structured data from JSON-LD (schema.org) ---
            company_name = None
            job_title = None
            sector = None

            for script_tag in soup.find_all("script", type="application/ld+json"):
                try:
                    ld_data = json.loads(script_tag.string)
                    items = ld_data if isinstance(ld_data, list) else [ld_data]
                    for item in items:
                        if item.get("@type") == "JobPosting":
                            job_title = job_title or item.get("title")
                            sector = sector or item.get("industry")
                            hiring_org = item.get("hiringOrganization")
                            if isinstance(hiring_org, dict):
                                company_name = company_name or hiring_org.get("name")
                            elif isinstance(hiring_org, str):
                                company_name = company_name or hiring_org
                except (json.JSONDecodeError, TypeError):
                    continue

            # --- Fallback: meta tags ---
            if not job_title:
                og_title = soup.find("meta", property="og:title")
                if og_title and og_title.get("content"):
                    job_title = og_title["content"]

            if not job_title:
                title_tag = soup.find("title")
                if title_tag:
                    job_title = title_tag.get_text(strip=True)

            if not company_name:
                og_site = soup.find("meta", property="og:site_name")
                if og_site and og_site.get("content"):
                    # og:site_name is often the platform name (Indeed, LinkedIn), not the company
                    # Only use it as a last resort
                    pass

            # --- Fallback: look for company name in common HTML patterns ---
            if not company_name:
                for selector in [
                    '[data-company-name]',
                    '.company-name', '.companyName', '.employer-name',
                    '[class*="company"]', '[class*="employer"]',
                ]:
                    el = soup.select_one(selector)
                    if el:
                        text = el.get_text(strip=True)
                        if text and len(text) < 100:
                            company_name = text
                            break

            # --- Try to extract company name from title patterns ---
            if not company_name and job_title:
                # Common patterns: "Job Title - Company Name" or "Job Title | Company Name" or "Job Title chez Company"
                for sep in [' - ', ' | ', ' chez ', ' at ', ' — ', ' · ']:
                    if sep in job_title:
                        parts = job_title.split(sep)
                        if len(parts) >= 2:
                            candidate = parts[-1].strip()
                            # Filter out platform names
                            platforms = ['indeed', 'linkedin', 'welcome to the jungle', 'glassdoor',
                                         'monster', 'hellowork', 'apec', 'pôle emploi', 'pole emploi',
                                         'france travail', 'meteojob', 'cadremploi', 'jobteaser']
                            if candidate.lower() not in platforms and len(candidate) < 80:
                                company_name = candidate
                                # Clean the job title too
                                job_title = sep.join(parts[:-1]).strip()
                            break

            # --- Extract raw text ---
            for script in soup(["script", "style"]):
                script.extract()
            raw_text = soup.get_text(separator=' ', strip=True)
            raw_text = re.sub(r'\s+', ' ', raw_text).strip()

            # --- Detect contract type from text ---
            contract_type = ScrapingService._detect_contract_type(raw_text)

            # --- Detect sector from text ---
            if not sector:
                sector = ScrapingService._detect_sector(raw_text)

            return {
                "raw_text": raw_text,
                "company_name": company_name,
                "job_title": job_title,
                "contract_type": contract_type,
                "sector": sector,
            }

        except Exception as e:
            return {
                "raw_text": f"Error extracting text: {str(e)}",
                "company_name": None,
                "job_title": None,
                "contract_type": None,
                "sector": None,
            }

    @staticmethod
    def _detect_contract_type(text: str) -> Optional[str]:
        """Detect if the job is 'Alternance' or 'Stage' from text content."""
        text_lower = text.lower()

        alternance_keywords = ['alternance', 'contrat d\'apprentissage', 'apprentissage',
                               'contrat de professionnalisation', 'professionnalisation']
        stage_keywords = ['stage', 'stagiaire', 'internship', 'intern']

        has_alternance = any(kw in text_lower for kw in alternance_keywords)
        has_stage = any(kw in text_lower for kw in stage_keywords)

        if has_alternance and not has_stage:
            return "Alternance"
        elif has_stage and not has_alternance:
            return "Stage"
        elif has_alternance and has_stage:
            # Count occurrences to decide
            alt_count = sum(text_lower.count(kw) for kw in alternance_keywords)
            stg_count = sum(text_lower.count(kw) for kw in stage_keywords)
            return "Alternance" if alt_count >= stg_count else "Stage"

        return None

    @staticmethod
    def _detect_sector(text: str) -> Optional[str]:
        """Try to detect the sector/industry from common keywords."""
        text_lower = text.lower()

        sector_map = {
            "Tech / IT": ['développement', 'développeur', 'informatique', 'logiciel', 'software',
                          'devops', 'cloud', 'cybersécurité', 'data', 'intelligence artificielle',
                          'machine learning', 'fullstack', 'frontend', 'backend', 'web'],
            "Finance": ['finance', 'banque', 'bancaire', 'assurance', 'comptabilité', 'audit'],
            "Consulting": ['conseil', 'consulting', 'consultant'],
            "Énergie": ['énergie', 'nucléaire', 'renouvelable', 'électricité', 'pétrole'],
            "Santé": ['santé', 'médical', 'pharmaceutique', 'pharma', 'biotechnologie'],
            "Commerce": ['commerce', 'retail', 'e-commerce', 'vente', 'distribution'],
            "Industrie": ['industrie', 'industriel', 'manufacturing', 'production', 'automobile'],
            "Telecom": ['télécom', 'telecom', 'télécommunication'],
            "Marketing": ['marketing', 'communication', 'publicité', 'digital marketing'],
        }

        best_sector = None
        best_count = 0
        for sector, keywords in sector_map.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > best_count:
                best_count = count
                best_sector = sector

        return best_sector if best_count >= 2 else None
