import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Optional


class ScrapingService:

    # Junk lines to filter out (lowercase matching)
    JUNK_LINES = [
        'se connecter', 's\'inscrire', 'déposer mon cv', 'créer mon alerte',
        'créez votre compte', 'téléchargez l\'app', 'mon espace', 'mes cv vus',
        'mes candidatures', 'mes alertes', 'mon profil', 'paramètres',
        'déconnexion', 'missions d\'intérim', 'diffuser ma première offre',
        'déjà client', 'accès recruteur', 'trouver mon', 'aller au contenu',
        'complétez votre profil', 'pour recevoir des offres', 'offres de stage',
        'offres en alternance', 'et postulez dans', 'premiers !',
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
        'emploi développeur', 'emploi informatique', 'emploi technicien',
        'emploi product owner', 'entreprises informatique',
        'alternance informatique', 'entreprises développeur', 'entreprises maisons',
        'alternance val-de-marne', 'alternance développeur', 'alternance maisons',
        'voir plus', 'voir moins', 'lire dans l\'app', 'c\'est noté',
        'postuler', 'dès maintenant', 'vous intéresser',
        'pour les postes éligibles', 'de plus', '/ 8',
        'en images', 'la carte', 'bdm',
        'stage de lycée', 'freelance', 'fonctionnaire', 'associé',
        'franchise', 'indépendant',
    ]

    JUNK_PATTERNS = [
        r'^emploi\s+\w+',
        r'^alternance\s+\w+',
        r'^entreprises\s+\w+',
        r'^il y a \d+ jours?$',
        r'^publiée? le',
        r'^réf\s*:',
        r'^[\d\s/]+$',
    ]

    @staticmethod
    def extract_text_from_url(url: str) -> str:
        """Extracts raw text content from the given URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator=' ', strip=True)
            return re.sub(r'\s+', ' ', text).strip()
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    @staticmethod
    def extract_structured_data(url: str) -> dict:
        """
        Extracts structured job data from a URL.
        Returns separate sections: job_title, company_name, location, salary, description, benefits, contract_type, sector.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # ========================
            # 1. JSON-LD EXTRACTION
            # ========================
            company_name = None
            job_title = None
            sector = None
            ld_description = None
            location = None
            salary = None

            for script_tag in soup.find_all("script", type="application/ld+json"):
                try:
                    if not script_tag.string:
                        continue
                    ld_data = json.loads(script_tag.string)
                    items = ld_data if isinstance(ld_data, list) else [ld_data]
                    # Handle @graph wrapping
                    expanded = []
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        if "@graph" in item:
                            graph = item["@graph"]
                            if isinstance(graph, list):
                                expanded.extend(g for g in graph if isinstance(g, dict))
                        else:
                            expanded.append(item)

                    for item in expanded:
                        if item.get("@type") == "JobPosting":
                            job_title = job_title or item.get("title")
                            sector = sector or item.get("industry")
                            ld_description = ld_description or item.get("description")

                            hiring_org = item.get("hiringOrganization")
                            if isinstance(hiring_org, dict):
                                company_name = company_name or hiring_org.get("name")
                            elif isinstance(hiring_org, str):
                                company_name = company_name or hiring_org

                            # Location
                            job_location = item.get("jobLocation")
                            if isinstance(job_location, dict):
                                address = job_location.get("address")
                                if isinstance(address, dict):
                                    parts = filter(None, [
                                        address.get("streetAddress"),
                                        address.get("addressLocality"),
                                        address.get("postalCode"),
                                        address.get("addressRegion"),
                                    ])
                                    location = ', '.join(parts) or None

                            # Salary
                            base_salary = item.get("baseSalary")
                            if isinstance(base_salary, dict):
                                value = base_salary.get("value")
                                if isinstance(value, dict):
                                    min_val = value.get("minValue")
                                    max_val = value.get("maxValue")
                                    unit = base_salary.get("unitText", "MONTH")
                                    unit_label = {"MONTH": "mois", "YEAR": "an", "HOUR": "heure"}.get(unit, unit)
                                    if min_val and max_val:
                                        salary = f"{min_val} - {max_val} € / {unit_label}"
                                    elif min_val:
                                        salary = f"{min_val} € / {unit_label}"

                except (json.JSONDecodeError, TypeError):
                    continue

            # ========================
            # 2. FALLBACK: META TAGS & HTML
            # ========================
            if not job_title:
                og_title = soup.find("meta", property="og:title")
                if og_title and og_title.get("content"):
                    job_title = og_title["content"]
            if not job_title:
                title_tag = soup.find("title")
                if title_tag:
                    job_title = title_tag.get_text(strip=True)

            if not company_name:
                for selector in ['[data-company-name]', '.company-name', '.companyName', '.employer-name']:
                    el = soup.select_one(selector)
                    if el:
                        text = el.get_text(strip=True)
                        if text and len(text) < 100:
                            company_name = text
                            break

            # Extract company from title
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

            # ========================
            # 3. EXTRACT CLEAN CONTENT FROM PAGE
            # ========================
            full_clean_text = ScrapingService._extract_clean_content(soup)

            # ========================
            # 4. SPLIT INTO STRUCTURED SECTIONS
            # ========================
            sections = ScrapingService._split_into_sections(full_clean_text, ld_description)

            # Use extracted sections
            description = sections.get("description", "")
            benefits = sections.get("benefits", "")

            # Fallback location from page text if not from JSON-LD
            if not location:
                location = ScrapingService._extract_location_from_text(full_clean_text, soup)

            # Fallback salary from page text
            if not salary:
                salary = ScrapingService._extract_salary_from_text(full_clean_text)

            # Detect contract type & sector
            all_text = f"{description} {benefits} {full_clean_text}"
            contract_type = ScrapingService._detect_contract_type(all_text)
            if not sector:
                sector = ScrapingService._detect_sector(all_text)

            # Build the raw_text summary
            raw_text = ScrapingService._build_summary(
                job_title, company_name, location, salary, contract_type, sector, description, benefits
            )

            return {
                "raw_text": raw_text,
                "company_name": company_name,
                "job_title": job_title,
                "contract_type": contract_type,
                "sector": sector,
                "location": location,
                "salary": salary,
                "description": description,
                "benefits": benefits,
            }

        except Exception as e:
            return {
                "raw_text": f"Error extracting text: {str(e)}",
                "company_name": None, "job_title": None, "contract_type": None,
                "sector": None, "location": None, "salary": None,
                "description": None, "benefits": None,
            }

    # ============================================================
    # CONTENT EXTRACTION
    # ============================================================

    @staticmethod
    def _extract_clean_content(soup: BeautifulSoup) -> str:
        """Extract the main page content, removing junk HTML elements."""
        soup_copy = BeautifulSoup(str(soup), 'html.parser')

        for tag in soup_copy.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style',
                                        'noscript', 'iframe', 'svg', 'form']):
            tag.decompose()

        junk_css = ['navbar', 'menu', 'cookie', 'banner', 'popup', 'breadcrumb',
                    'pagination', 'social', 'share', 'related', 'similar',
                    'recommend', 'subscribe', 'newsletter', 'signup', 'login',
                    'advert', 'sponsor']

        for element in soup_copy.find_all(True):
            el_class = ' '.join(element.get('class', []))
            el_id = element.get('id', '')
            combined = f"{el_class} {el_id}".lower()
            if any(p in combined for p in junk_css):
                element.decompose()

        text = soup_copy.get_text(separator='\n', strip=True)
        return text

    # ============================================================
    # SECTION SPLITTING
    # ============================================================

    @staticmethod
    def _split_into_sections(page_text: str, ld_description: Optional[str] = None) -> dict:
        """
        Split the page content into structured sections:
        - description: main job details (missions, responsibilities, profile)
        - benefits: advantages, conditions, perks
        """

        # If we have a JSON-LD description, use it as the main description
        if ld_description:
            desc_soup = BeautifulSoup(ld_description, 'html.parser')
            description_text = desc_soup.get_text(separator='\n', strip=True)
            description_clean = ScrapingService._clean_lines(description_text)
        else:
            description_clean = ""

        # Extract benefits from the full page text
        benefits_text = ScrapingService._extract_section_content(page_text, [
            'avantages', 'les avantages', 'pourquoi nous rejoindre',
            'conditions de travail', 'ce que nous offrons', 'nos avantages',
            'package', 'rémunération et avantages',
        ])

        # If no JSON-LD description, extract from page
        if not description_clean:
            description_clean = ScrapingService._extract_section_content(page_text, [
                'description du poste', 'missions', 'contenu du poste',
                'détail du poste', 'le job', 'le poste',
                'votre mission', 'vos missions', 'responsabilités',
                'introduction',
            ])

            # If still nothing, try to get the biggest block of clean text
            if not description_clean:
                description_clean = ScrapingService._extract_main_block(page_text)

        return {
            "description": description_clean,
            "benefits": benefits_text,
        }

    @staticmethod
    def _extract_section_content(text: str, section_headers: list) -> str:
        """Extract content that falls under specific section headers."""
        lines = text.split('\n')
        capturing = False
        captured = []
        stop_keywords = [
            'ces offres pourraient', 'offres similaires', 'voir plus d\'offres',
            'publiée le', 'créez votre compte', 'en images',
        ]

        # Section headers that indicate a NEW section (to stop capturing)
        all_section_headers = [
            'description du poste', 'missions', 'contenu du poste',
            'profil recherché', 'profil', 'compétences', 'qualifications',
            'formation', 'expérience', 'pourquoi nous rejoindre',
            'avantages', 'les avantages', 'conditions de travail',
            'rémunération', 'salaire', 'processus de recrutement',
            'étapes de recrutement', 'introduction', 'le job',
            'l\'entreprise', 'détail du poste', 'votre mission',
            'vos missions', 'responsabilités', 'requirements',
            'si c\'est vous',
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            # Stop at related offers
            if any(kw in line_lower for kw in stop_keywords):
                break

            # Check if this is one of our target section headers → start capturing
            if not capturing:
                if any(line_lower == h or line_lower.startswith(h + ' ') or line_lower.startswith(h + ':')
                       for h in section_headers):
                    capturing = True
                    continue
            else:
                # Check if we hit a different section header → stop
                is_new_section = any(
                    (line_lower == h or line_lower.startswith(h + ' ') or line_lower.startswith(h + ':'))
                    and h not in section_headers
                    for h in all_section_headers
                )
                if is_new_section:
                    capturing = False
                    continue

                if not ScrapingService._is_junk_line(line):
                    captured.append(line)

        return ScrapingService._format_section_text(captured)

    @staticmethod
    def _extract_main_block(text: str) -> str:
        """Fallback: extract the largest meaningful block of text from the page."""
        lines = text.split('\n')
        clean = []
        in_related = False

        for line in lines:
            line = line.strip()
            if not line:
                continue
            line_lower = line.lower()

            if any(kw in line_lower for kw in ['ces offres pourraient', 'offres similaires']):
                in_related = True
            if in_related:
                continue

            if not ScrapingService._is_junk_line(line) and len(line) > 30:
                clean.append(line)

        return ScrapingService._format_section_text(clean)

    # ============================================================
    # TEXT CLEANING & FORMATTING
    # ============================================================

    @staticmethod
    def _is_junk_line(line: str) -> bool:
        """Check if a line is junk."""
        line_lower = line.lower().strip()

        if len(line) < 3:
            return True

        for junk in ScrapingService.JUNK_LINES:
            if junk in line_lower:
                return True

        for pattern in ScrapingService.JUNK_PATTERNS:
            if re.match(pattern, line_lower):
                return True

        if line_lower in ['cdi', 'cdd', 'intérim', 'email', 'emploi', 'métier', 'localité', 'type de contrat']:
            return True

        return False

    @staticmethod
    def _clean_lines(text: str) -> str:
        """Clean a block of text, removing junk and deduplicating."""
        lines = text.split('\n')
        cleaned = []
        seen = set()

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            if ScrapingService._is_junk_line(line):
                continue
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(line)

        return ScrapingService._format_section_text(cleaned)

    @staticmethod
    def _format_section_text(lines: list) -> str:
        """Format lines into readable text with bullet points."""
        output = []
        for line in lines:
            if line.startswith('-') or line.startswith('•') or line.startswith('·'):
                output.append(f"  • {line.lstrip('-•· ').strip()}")
            else:
                output.append(line)

        result = '\n'.join(output).strip()
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result

    # ============================================================
    # FIELD EXTRACTION HELPERS
    # ============================================================

    @staticmethod
    def _extract_location_from_text(text: str, soup: BeautifulSoup) -> Optional[str]:
        """Try to find location from page content."""
        # Look for common address patterns in the text
        patterns = [
            r'(\d{1,3}[-\s]?\d{0,3}\s+(?:rue|avenue|boulevard|allée|place|chemin)\s+[^\n,]{3,50}[\s,]+\d{5}\s+[A-Za-zÀ-ÿ\-\s]+)',
            r'([A-Za-zÀ-ÿ\-\s]+\s*[-–]\s*\d{2,5})',  # "Maisons-Alfort - 94"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                loc = match.group(1).strip()
                if 10 < len(loc) < 100:
                    return loc

        return None

    @staticmethod
    def _extract_salary_from_text(text: str) -> Optional[str]:
        """Try to find salary info from text."""
        patterns = [
            r'(\d[\d\s,\.]+\s*[-–à]\s*\d[\d\s,\.]+\s*€\s*/\s*(?:mois|an|heure|jour))',
            r'(\d[\d\s,\.]+\s*€\s*/\s*(?:mois|an|heure|jour))',
            r'(\d[\d\s,\.]+\s*[-–à]\s*\d[\d\s,\.]+\s*(?:k€|K€|euros?)(?:\s*/\s*(?:mois|an))?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    # ============================================================
    # SUMMARY BUILDER
    # ============================================================

    @staticmethod
    def _build_summary(job_title, company_name, location, salary, contract_type, sector, description, benefits) -> str:
        """Build a formatted summary of all extracted data."""
        parts = []

        # Header
        if job_title:
            parts.append(f"📌 POSTE : {job_title}")
        if company_name:
            parts.append(f"🏢 ENTREPRISE : {company_name}")
        if location:
            parts.append(f"📍 LIEU : {location}")
        if salary:
            parts.append(f"💰 SALAIRE : {salary}")
        if contract_type:
            parts.append(f"📄 CONTRAT : {contract_type}")
        if sector:
            parts.append(f"🏭 SECTEUR : {sector}")

        if parts:
            parts.append("")
            parts.append("─" * 40)
            parts.append("")

        # Description
        if description:
            parts.append("📋 DÉTAILS DU POSTE")
            parts.append("")
            parts.append(description)
            parts.append("")

        # Benefits
        if benefits:
            parts.append("─" * 40)
            parts.append("")
            parts.append("🎁 AVANTAGES")
            parts.append("")
            parts.append(benefits)

        return '\n'.join(parts).strip()

    # ============================================================
    # DETECTORS
    # ============================================================

    @staticmethod
    def _detect_contract_type(text: str) -> Optional[str]:
        text_lower = text.lower()
        alternance_kw = ['alternance', 'contrat d\'apprentissage', 'apprentissage', 'professionnalisation']
        stage_kw = ['stage', 'stagiaire', 'internship', 'intern']

        has_alt = any(kw in text_lower for kw in alternance_kw)
        has_stg = any(kw in text_lower for kw in stage_kw)

        if has_alt and not has_stg:
            return "Alternance"
        elif has_stg and not has_alt:
            return "Stage"
        elif has_alt and has_stg:
            alt_count = sum(text_lower.count(kw) for kw in alternance_kw)
            stg_count = sum(text_lower.count(kw) for kw in stage_kw)
            return "Alternance" if alt_count >= stg_count else "Stage"
        return None

    @staticmethod
    def _detect_sector(text: str) -> Optional[str]:
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
