import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Optional


class ScrapingService:

    # Junk lines to filter out (lowercase matching)
    JUNK_LINES = [
        # Platform UI / navigation
        'se connecter', 's\'inscrire', 'déposer mon cv', 'créer mon alerte',
        'créez votre compte', 'téléchargez l\'app', 'mon espace', 'mes cv vus',
        'mes candidatures', 'mes alertes', 'mon profil', 'paramètres',
        'déconnexion', 'missions d\'intérim', 'diffuser ma première offre',
        'déjà client', 'accès recruteur', 'trouver mon', 'aller au contenu',
        'complétez votre profil', 'pour recevoir des offres', 'offres de stage',
        'offres en alternance', 'et postulez dans', 'premiers !',
        # Footer / platform links
        'voir l\'offre', 'voir plus d\'offres', 'recherches similaires',
        'ces offres pourraient', 'initialisation', 'chargement du chat',
        'analyser mon cv', 'envoyez votre candidature',
        'informations légales', 'cgu', 'politique de confidentialité',
        'gérer les traceurs', 'accessibilité', 'aide et contact',
        'nous suivre sur', 'les sites hello', 'salaire brut net',
        'qui sommes-nous', 'on recrute', 'offres d\'emploi par',
        'localiser le poste', 'testez votre correspondance',
        'helloworkplace', 'hellocv', 'jobijoba', 'maformation', 'diplomeo',
        'l\'emploi', 'accès client', 'les apps', 'les sites',
        # Related offers / search links
        'emploi développeur', 'emploi informatique', 'emploi technicien',
        'emploi product owner', 'entreprises informatique',
        'alternance informatique', 'entreprises développeur',
        'entreprises maisons', 'alternance val-de-marne',
        'alternance développeur', 'alternance maisons',
        # Form elements
        'métier', 'localité', 'type de contrat',
        'stage de lycée', 'freelance', 'fonctionnaire', 'associé',
        'franchise', 'indépendant',
        # UI elements
        'voir plus', 'voir moins', 'lire dans l\'app', 'c\'est noté',
        'postuler', 'dès maintenant', 'vous intéresser',
        'pour les postes éligibles', 'de plus', '/ 8',
        'en images', 'la carte',
        # Misc
        'bdm',
    ]

    # Patterns for lines that are just platform noise (regex)
    JUNK_PATTERNS = [
        r'^emploi\s+\w+',           # "Emploi Rungis", "Emploi Créteil"
        r'^alternance\s+\w+',       # "Alternance Val-de-Marne"
        r'^entreprises\s+\w+',      # "Entreprises Maisons-Alfort"
        r'^il y a \d+ jours?$',     # "il y a 13 jours"
        r'^publiée? le',            # "Publiée le 13/03/2026"
        r'^réf\s*:',                # "Réf : 5334"
        r'^\d+\s*[-/]\s*\d+\s',     # address numbers at start
    ]

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
        Returns a dict with: raw_text, company_name, job_title, contract_type, sector, location, salary, education, remote.
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
            location = None
            salary = None

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

                            job_location = item.get("jobLocation")
                            if isinstance(job_location, dict):
                                address = job_location.get("address", {})
                                if isinstance(address, dict):
                                    parts = [address.get("addressLocality"), address.get("postalCode")]
                                    location = ' - '.join(p for p in parts if p)

                            base_salary = item.get("baseSalary")
                            if isinstance(base_salary, dict):
                                value = base_salary.get("value", {})
                                if isinstance(value, dict):
                                    min_val = value.get("minValue")
                                    max_val = value.get("maxValue")
                                    unit = base_salary.get("unitText", "")
                                    if min_val and max_val:
                                        salary = f"{min_val} - {max_val} € / {unit.lower()}"

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

            # --- Fallback: HTML patterns for company name ---
            if not company_name:
                for selector in [
                    '[data-company-name]',
                    '.company-name', '.companyName', '.employer-name',
                ]:
                    el = soup.select_one(selector)
                    if el:
                        text = el.get_text(strip=True)
                        if text and len(text) < 100:
                            company_name = text
                            break

            # --- Extract company from title patterns ---
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

            # --- Extract CLEAN job description ---
            clean_description = ScrapingService._extract_job_description(soup, ld_description)

            # --- Detect contract type ---
            contract_type = ScrapingService._detect_contract_type(clean_description)

            # --- Detect sector ---
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
        Extract only the relevant job description from the page.
        """

        # Priority 1: JSON-LD description (most reliable, already structured by the site)
        if ld_description:
            desc_soup = BeautifulSoup(ld_description, 'html.parser')
            text = desc_soup.get_text(separator='\n', strip=True)
            cleaned = ScrapingService._clean_and_organize(text)
            if len(cleaned) > 100:
                return cleaned

        # Priority 2: Find main content area
        content_selectors = [
            '[class*="job-description"]', '[class*="jobDescription"]',
            '[class*="job-detail"]', '[class*="jobDetail"]',
            '[class*="offer-description"]', '[class*="offerDescription"]',
            '[class*="description-poste"]',
            '[id*="job-description"]', '[id*="jobDescription"]',
            '[data-testid*="description"]',
            'article[class*="job"]', 'article[class*="offer"]',
            '.job-content', '.offer-content', '.posting-content',
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            for el in elements:
                text = el.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    cleaned = ScrapingService._clean_and_organize(text)
                    if len(cleaned) > 100:
                        return cleaned

        # Priority 3: <main> or <article>
        for tag_name in ['main', 'article']:
            tag = soup.find(tag_name)
            if tag:
                text = tag.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    cleaned = ScrapingService._clean_and_organize(text)
                    if len(cleaned) > 100:
                        return cleaned

        # Priority 4: Full body with junk removed
        soup_copy = BeautifulSoup(str(soup), 'html.parser')

        for tag in soup_copy.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style',
                                        'noscript', 'iframe', 'svg', 'form']):
            tag.decompose()

        junk_css_patterns = [
            'nav', 'navbar', 'header', 'footer', 'sidebar', 'menu',
            'cookie', 'banner', 'popup', 'breadcrumb', 'pagination',
            'social', 'share', 'comment', 'related', 'similar', 'recommend',
            'subscribe', 'newsletter', 'signup', 'login',
            'ad-', 'ads-', 'advert', 'sponsor',
        ]

        for element in soup_copy.find_all(True):
            el_class = ' '.join(element.get('class', []))
            el_id = element.get('id', '')
            combined = f"{el_class} {el_id}".lower()
            if any(p in combined for p in junk_css_patterns):
                element.decompose()

        text = soup_copy.get_text(separator='\n', strip=True)
        cleaned = ScrapingService._clean_and_organize(text)
        return cleaned

    @staticmethod
    def _is_junk_line(line: str) -> bool:
        """Check if a line is junk (platform UI, navigation, etc.)."""
        line_lower = line.lower().strip()

        # Too short to be useful
        if len(line) < 3:
            return True

        # Exact or substring match against junk keywords
        for junk in ScrapingService.JUNK_LINES:
            if junk in line_lower:
                return True

        # Regex pattern match
        for pattern in ScrapingService.JUNK_PATTERNS:
            if re.match(pattern, line_lower):
                return True

        # Contract type dropdown items (single words)
        if line_lower in ['cdi', 'cdd', 'intérim', 'email']:
            return True

        # Lines that are just a number or very short meaningless text
        if re.match(r'^[\d\s/]+$', line):
            return True

        # Lines that look like other job offers (company name + city pattern in isolation)
        if re.match(r'^[A-Z][a-zA-Z\s]+ - \d{2}$', line.strip()):
            return True

        return False

    @staticmethod
    def _is_other_job_offer(line: str, lines: list, idx: int) -> bool:
        """Detect if we've entered a 'related offers' section."""
        line_lower = line.lower()
        if any(kw in line_lower for kw in ['ces offres pourraient', 'offres similaires', 'voir plus d\'offres']):
            return True
        return False

    @staticmethod
    def _clean_and_organize(text: str) -> str:
        """Master cleaning function: filter junk, organize into sections."""
        lines = text.split('\n')
        cleaned_lines = []
        seen = set()
        in_related_offers = False

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Stop processing if we hit the 'related offers' section
            if ScrapingService._is_other_job_offer(line, lines, i):
                in_related_offers = True

            if in_related_offers:
                continue

            # Skip junk
            if ScrapingService._is_junk_line(line):
                continue

            # Skip duplicates
            line_key = line.lower().strip()
            if line_key in seen:
                continue
            seen.add(line_key)

            cleaned_lines.append(line)

        # Organize into sections
        result = ScrapingService._organize_into_sections(cleaned_lines)
        return result

    @staticmethod
    def _organize_into_sections(lines: list) -> str:
        """Organize extracted lines into a readable, structured format with section headers."""

        section_keywords = {
            'description du poste et missions': '📋 DESCRIPTION DU POSTE',
            'description du poste': '📋 DESCRIPTION DU POSTE',
            'missions': '📋 MISSIONS',
            'contenu du poste': '📋 CONTENU DU POSTE',
            'profil recherché': '👤 PROFIL RECHERCHÉ',
            'si c\'est vous': '👤 PROFIL RECHERCHÉ',
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
            'processus de recrutement': '📞 PROCESSUS DE RECRUTEMENT',
            'étapes de recrutement': '📞 ÉTAPES DE RECRUTEMENT',
            'les étapes de recrutement': '📞 ÉTAPES DE RECRUTEMENT',
            'introduction': '📝 PRÉSENTATION',
            'le job': '📋 LE POSTE',
            'l\'entreprise': '🏢 L\'ENTREPRISE',
            'détail du poste': '📋 DÉTAIL DU POSTE',
        }

        # Lines that are ONLY a section header (no content on same line) — skip them if isolated
        header_only_lines = set(section_keywords.keys())

        output_lines = []
        current_section = None
        section_has_content = False

        for line in lines:
            line_lower = line.lower().strip()

            # Check if this line is a section header
            matched_section = None
            for keyword, header in section_keywords.items():
                if line_lower == keyword or line_lower == keyword + ' :' or line_lower == keyword + ':':
                    matched_section = header
                    break

            if matched_section:
                # Don't add consecutive empty section headers
                current_section = matched_section
                section_has_content = False
                output_lines.append('')
                output_lines.append(f'━━━ {matched_section} ━━━')
                output_lines.append('')
            else:
                # Content line
                section_has_content = True

                # Format list items
                if line.startswith('-') or line.startswith('•') or line.startswith('·'):
                    output_lines.append(f'  • {line.lstrip("-•· ").strip()}')
                else:
                    output_lines.append(line)

        # --- Post-processing: remove empty sections ---
        final_lines = []
        i = 0
        while i < len(output_lines):
            # Check if this is a section header
            if i < len(output_lines) and output_lines[i].startswith('━━━'):
                # Look ahead to see if there's content before the next section header (or end)
                j = i + 1
                # skip blank lines after header
                while j < len(output_lines) and output_lines[j].strip() == '':
                    j += 1
                # Check if next non-blank line is another header or end of list
                if j >= len(output_lines) or output_lines[j].startswith('━━━'):
                    # Empty section — skip the header and blank lines
                    i = j
                    continue
                else:
                    final_lines.append(output_lines[i])
            else:
                final_lines.append(output_lines[i])
            i += 1

        result = '\n'.join(final_lines).strip()

        # Clean up multiple consecutive blank lines
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
