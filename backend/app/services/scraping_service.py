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
            ld_description = None

            for script_tag in soup.find_all("script", type="application/ld+json"):
                try:
                    ld_data = json.loads(script_tag.string)
                    items = ld_data if isinstance(ld_data, list) else [ld_data]
                    for item in items:
                        if item.get("@type") == "JobPosting":
                            job_title = job_title or item.get("title")
                            sector = sector or item.get("industry")
                            ld_description = ld_description or item.get("description")
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
                for sep in [' - ', ' | ', ' chez ', ' at ', ' — ', ' · ']:
                    if sep in job_title:
                        parts = job_title.split(sep)
                        if len(parts) >= 2:
                            candidate = parts[-1].strip()
                            platforms = ['indeed', 'linkedin', 'welcome to the jungle', 'glassdoor',
                                         'monster', 'hellowork', 'apec', 'pôle emploi', 'pole emploi',
                                         'france travail', 'meteojob', 'cadremploi', 'jobteaser']
                            if candidate.lower() not in platforms and len(candidate) < 80:
                                company_name = candidate
                                job_title = sep.join(parts[:-1]).strip()
                            break

            # --- Extract CLEAN job description (not the whole page) ---
            clean_description = ScrapingService._extract_job_description(soup, ld_description)

            # --- Detect contract type from text ---
            contract_type = ScrapingService._detect_contract_type(clean_description)

            # --- Detect sector from text ---
            if not sector:
                sector = ScrapingService._detect_sector(clean_description)

            return {
                "raw_text": clean_description,
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
    def _extract_job_description(soup: BeautifulSoup, ld_description: Optional[str] = None) -> str:
        """
        Extract only the relevant job description from the page,
        removing navigation, footers, sidebars, ads, etc.
        Returns a clean, organized text.
        """

        # Priority 1: JSON-LD description (most reliable)
        if ld_description:
            # JSON-LD description can be HTML, clean it
            desc_soup = BeautifulSoup(ld_description, 'html.parser')
            text = desc_soup.get_text(separator='\n', strip=True)
            cleaned = ScrapingService._clean_text_block(text)
            if len(cleaned) > 100:
                return cleaned

        # Priority 2: Try to find the main job content area
        content_selectors = [
            # Common job posting content selectors
            '[class*="job-description"]', '[class*="jobDescription"]',
            '[class*="job-detail"]', '[class*="jobDetail"]',
            '[class*="offer-description"]', '[class*="offerDescription"]',
            '[class*="description-poste"]', '[class*="descriptionPoste"]',
            '[id*="job-description"]', '[id*="jobDescription"]',
            '[data-testid*="description"]', '[data-testid*="job"]',
            'article[class*="job"]', 'article[class*="offer"]',
            '[class*="detail-poste"]', '[class*="detailPoste"]',
            '.job-content', '.offer-content', '.posting-content',
            'main article', 'main [role="main"]',
            # Hellowork specific
            '[class*="tw-"]',
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            for el in elements:
                text = el.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    cleaned = ScrapingService._clean_text_block(text)
                    if len(cleaned) > 100:
                        return cleaned

        # Priority 3: Extract from <main> or <article> tags
        for tag_name in ['main', 'article']:
            tag = soup.find(tag_name)
            if tag:
                text = tag.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    cleaned = ScrapingService._clean_text_block(text)
                    if len(cleaned) > 100:
                        return cleaned

        # Priority 4: Fallback — remove junk elements, extract remaining body text
        soup_copy = BeautifulSoup(str(soup), 'html.parser')

        # Remove unwanted elements
        for tag in soup_copy.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style',
                                        'noscript', 'iframe', 'svg', 'form']):
            tag.decompose()

        # Remove by common class/id patterns for navigation, ads, etc.
        junk_patterns = [
            'nav', 'navbar', 'header', 'footer', 'sidebar', 'menu',
            'cookie', 'banner', 'alert', 'modal', 'popup',
            'breadcrumb', 'pagination', 'social', 'share',
            'comment', 'related', 'similar', 'recommend',
            'subscribe', 'newsletter', 'signup', 'login',
            'ad-', 'ads-', 'advert', 'sponsor',
        ]

        for element in soup_copy.find_all(True):
            el_class = ' '.join(element.get('class', []))
            el_id = element.get('id', '')
            combined = f"{el_class} {el_id}".lower()
            if any(p in combined for p in junk_patterns):
                element.decompose()

        text = soup_copy.get_text(separator='\n', strip=True)
        cleaned = ScrapingService._clean_text_block(text)
        return cleaned

    @staticmethod
    def _clean_text_block(text: str) -> str:
        """Clean and organize a text block into readable sections."""
        lines = text.split('\n')
        cleaned_lines = []
        seen = set()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip very short lines that are likely UI elements
            if len(line) < 3:
                continue
            # Skip common junk patterns
            junk_keywords = [
                'se connecter', 's\'inscrire', 'déposer mon cv', 'créer mon alerte',
                'créez votre compte', 'téléchargez l\'app', 'mon espace', 'mes cv vus',
                'mes candidatures', 'mes alertes', 'mon profil', 'paramètres',
                'déconnexion', 'missions d\'intérim', 'diffuser ma première offre',
                'déjà client', 'accès recruteur', 'trouver mon j', 'trouver mon e',
                'voir l\'offre', 'voir plus d\'offres', 'recherches similaires',
                'ces offres pourraient', 'initialisation', 'chargement du chat',
                'analyser mon cv', 'postuler', 'envoyez votre candidature',
                'informations légales', 'cgu', 'politique de confidentialité',
                'gérer les traceurs', 'accessibilité', 'aide et contact',
                'nous suivre sur', 'les sites hello', 'salaire brut net',
                'qui sommes-nous', 'on recrute', 'offres d\'emploi par',
                'localiser le poste', 'créer mon alerte',
            ]
            if any(junk.lower() in line.lower() for junk in junk_keywords if len(junk) > 5):
                continue
            # Skip duplicate lines
            line_key = line.lower().strip()
            if line_key in seen:
                continue
            seen.add(line_key)
            cleaned_lines.append(line)

        # --- Organize into sections ---
        result = ScrapingService._organize_into_sections(cleaned_lines)
        return result

    @staticmethod
    def _organize_into_sections(lines: list) -> str:
        """Organize extracted lines into a readable, structured format."""
        section_keywords = {
            'description du poste': '📋 DESCRIPTION DU POSTE',
            'missions': '📋 MISSIONS',
            'contenu du poste': '📋 CONTENU DU POSTE',
            'profil recherché': '👤 PROFIL RECHERCHÉ',
            'profil': '👤 PROFIL',
            'compétences': '🔧 COMPÉTENCES',
            'requirements': '🔧 COMPÉTENCES REQUISES',
            'qualifications': '🔧 QUALIFICATIONS',
            'formation': '🎓 FORMATION',
            'expérience': '📅 EXPÉRIENCE',
            'pourquoi nous rejoindre': '⭐ POURQUOI NOUS REJOINDRE',
            'avantages': '🎁 AVANTAGES',
            'les avantages': '🎁 AVANTAGES',
            'conditions de travail': '🏢 CONDITIONS DE TRAVAIL',
            'rémunération': '💰 RÉMUNÉRATION',
            'salaire': '💰 SALAIRE',
            'processus de recrutement': '📞 PROCESSUS DE RECRUTEMENT',
            'étapes de recrutement': '📞 ÉTAPES DE RECRUTEMENT',
            'les étapes de recrutement': '📞 ÉTAPES DE RECRUTEMENT',
            'introduction': '📝 INTRODUCTION',
            'le job': '📋 LE POSTE',
            'l\'entreprise': '🏢 L\'ENTREPRISE',
            'détail du poste': '📋 DÉTAIL DU POSTE',
            'si c\'est vous': '👤 PROFIL RECHERCHÉ',
        }

        output_lines = []
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()

            # Check if this line is a section header
            matched_section = None
            for keyword, header in section_keywords.items():
                if line_lower == keyword or line_lower.startswith(keyword + ' '):
                    matched_section = header
                    break

            if matched_section:
                if matched_section != current_section:
                    output_lines.append('')
                    output_lines.append(f'━━━ {matched_section} ━━━')
                    output_lines.append('')
                    current_section = matched_section
            else:
                # Detect list items (lines starting with - or •)
                if line.startswith('-') or line.startswith('•') or line.startswith('·'):
                    output_lines.append(f'  • {line.lstrip("-•· ").strip()}')
                else:
                    output_lines.append(line)

        result = '\n'.join(output_lines).strip()

        # Clean up multiple newlines
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result

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
            "Industrie Manufacturière": ['industrie', 'industriel', 'manufacturing', 'production', 'automobile', 'thermique'],
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
