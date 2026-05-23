"""
Script de seed : insère des candidatures réalistes en alternance cybersécurité
dans la base PostgreSQL de NEXUS.

Usage (depuis le dossier backend/) :
    python scripts/seed_data.py
"""

import sys
import uuid
from datetime import datetime, timezone, timedelta

try:
    import psycopg
except ImportError:
    print("❌ psycopg non trouvé. Installe-le : pip install psycopg")
    sys.exit(1)

# ── Config ───────────────────────────────────────────────────────────────────
CONN_STR = "postgresql://crm_user:crm_password@localhost:5432/crm_db"

# ── Helpers ──────────────────────────────────────────────────────────────────
def uid():
    return str(uuid.uuid4())

def dt(days_ago: int = 0):
    return datetime.now(timezone.utc) - timedelta(days=days_ago)

# ── DATA ─────────────────────────────────────────────────────────────────────
# (name, sector, tech_stack, glassdoor_url, linkedin_url)
COMPANIES = [
    ("Thales", "Défense & Cybersécurité",
     ["Python", "C++", "SIEM", "Splunk", "Azure"],
     "https://www.glassdoor.fr/Avis/Thales-Avis-E3612.htm",
     "https://www.linkedin.com/company/thales/"),

    ("Airbus CyberSecurity", "Aérospatial & Cybersécurité",
     ["ISO 27001", "SIEM", "Python", "Docker"],
     "https://www.glassdoor.fr/Avis/Airbus-Avis-E610.htm",
     "https://www.linkedin.com/company/airbus/"),

    ("Orange Cyberdefense", "Télécoms & Cybersécurité",
     ["SOC", "Splunk", "QRadar", "Python", "Linux"],
     "https://www.glassdoor.fr/Avis/Orange-Avis-E3871.htm",
     "https://www.linkedin.com/company/orange-cyberdefense/"),

    ("Capgemini", "Conseil & IT",
     ["Java", "Python", "Azure", "DevSecOps", "Terraform"],
     "https://www.glassdoor.fr/Avis/Capgemini-Avis-E2672.htm",
     "https://www.linkedin.com/company/capgemini/"),

    ("Sopra Steria", "ESN & Conseil",
     ["EBIOS RM", "ISO 27001", "Python", "AWS"],
     "https://www.glassdoor.fr/Avis/Sopra-Steria-Avis-E349731.htm",
     "https://www.linkedin.com/company/soprasteria/"),

    ("BPCE", "Banque & Finance",
     ["AppSec", "SAST", "DAST", "DevSecOps", "Python", "Power BI"],
     "https://www.glassdoor.fr/Avis/BPCE-Avis-E371889.htm",
     "https://www.linkedin.com/company/bpce/"),

    ("ANSSI", "Agence gouvernementale",
     ["Analyse de malware", "CTF", "Python", "Reverse Engineering"],
     None,
     "https://www.linkedin.com/company/anssi/"),

    ("Atos", "IT & Cloud",
     ["Azure", "Kubernetes", "Docker", "CI/CD", "DevSecOps"],
     "https://www.glassdoor.fr/Avis/Atos-Avis-E372737.htm",
     "https://www.linkedin.com/company/atos/"),

    ("Accenture", "Conseil & Stratégie",
     ["Python", "GRC", "ISO 27001", "Business Analysis"],
     "https://www.glassdoor.fr/Avis/Accenture-Avis-E4138.htm",
     "https://www.linkedin.com/company/accenture/"),

    ("Société Générale", "Banque",
     ["Splunk", "SIEM", "CyberArk", "Python"],
     "https://www.glassdoor.fr/Avis/Societe-Generale-Avis-E5538.htm",
     "https://www.linkedin.com/company/societe-generale/"),

    ("VINCI Energies", "Énergie & BTP",
     ["GRC", "EBIOS RM", "ISO 27001", "Power BI"],
     "https://www.glassdoor.fr/Avis/VINCI-Energies-Avis-E383091.htm",
     "https://www.linkedin.com/company/vinci-energies/"),

    ("Inetum", "ESN",
     ["Python", "Docker", "Jenkins", "OWASP", "Pen Testing"],
     "https://www.glassdoor.fr/Avis/Inetum-Avis-E11972.htm",
     "https://www.linkedin.com/company/inetum/"),

    ("CNP Assurances", "Assurance",
     ["ISO 27001", "GRC", "Risk Management", "Python"],
     "https://www.glassdoor.fr/Avis/CNP-Assurances-Avis-E394021.htm",
     "https://www.linkedin.com/company/cnp-assurances/"),

    ("Wavestone", "Conseil Cybersécurité",
     ["EBIOS RM", "ISO 27001", "Pen Testing", "Python"],
     "https://www.glassdoor.fr/Avis/Wavestone-Avis-E721509.htm",
     "https://www.linkedin.com/company/wavestone/"),

    ("IBM France", "Technologie",
     ["QRadar", "SIEM", "AI", "Python", "Kubernetes"],
     "https://www.glassdoor.fr/Avis/IBM-Avis-E354.htm",
     "https://www.linkedin.com/company/ibm/"),
]

# (cidx, status, type, days_sent_ago, salary, location, job_url, description, flagged, note)
APPLICATIONS = [
    # ── REJECTED ──────────────────────────────────────────────────────────
    (0, "Rejected", "Alternance", 75, "1 400 €/mois", "Vélizy-Villacoublay (92)",
     "https://www.thalesgroup.com/fr/emplois",
     "Alternance Analyste SOC - 24 mois. Surveillance et analyse des événements de sécurité sur les plateformes Splunk/SIEM, réponse aux incidents, rédaction de playbooks.",
     False,
     "Rejeté après un entretien RH. Feedback : profil junior, demandaient plus d'expérience réseau."),

    (1, "Rejected", "Alternance", 60, "1 350 €/mois", "Élancourt (78)",
     "https://www.airbus.com/fr/carrieres",
     "Alternance Cybersécurité - Gouvernance des risques (24 mois). Support à la mise en oeuvre de la politique SSI, suivi des audits ISO 27001, rédaction de procédures.",
     False,
     "Pas de retour après l'entretien technique. Relancé 2 fois."),

    # ── INTERVIEW ─────────────────────────────────────────────────────────
    (2, "Interview", "Alternance", 30, "1 450 €/mois", "Paris (75)",
     "https://www.orangecyberdefense.com/fr/carrieres",
     "Alternance Analyste SOC Niveau 1/2 - 24 mois. Traitement des alertes sur QRadar/Splunk, investigation des incidents, amélioration continue des règles de détection.",
     True,
     "Entretien technique prévu le 8 avril 2026. Préparer : KillChain, MITRE ATT&CK, escalade d'incidents."),

    (5, "Interview", "Alternance", 25, "1 500 €/mois", "Paris (75)",
     "https://recrutement.bpce.fr",
     "Alternance DevSecOps / AppSec - 24 mois. Intégration des contrôles de sécurité dans les pipelines CI/CD, SAST/DAST avec SonarQube et OWASP ZAP, threat modeling.",
     True,
     "Entretien RH passé. Attente retour entretien technique avec le manager."),

    # ── TECHNICAL_TEST ────────────────────────────────────────────────────
    (13, "Technical Test", "Alternance", 20, "1 600 €/mois", "Paris-La Défense (92)",
     "https://www.wavestone.com/fr/nos-offres-emploi/",
     "Alternance Consultant Cybersécurité GRC - 24 mois. Réalisation d'analyses de risques EBIOS RM, accompagnement de clients dans leur démarche ISO 27001, veille réglementaire DORA/NIS2.",
     True,
     "Test technique envoyé : étude de cas EBIOS RM sur un SI bancaire. À rendre avant le 01/04."),

    # ── FOLLOW_UP ─────────────────────────────────────────────────────────
    (4, "Follow-up", "Alternance", 45, "1 300 €/mois", "Annecy (74)",
     "https://www.soprasteria.com/fr/recrutement",
     "Alternance Cybersécurité & GRC - 24 mois. Cartographie des risques SI, pilotage des plans de traitement, sensibilisation des collaborateurs à la sécurité.",
     False,
     "Relancé par email le 10/03. Toujours en attente de réponse."),

    (8, "Follow-up", "Alternance", 40, "1 350 €/mois", "Paris (75)",
     "https://www.accenture.com/fr-fr/careers",
     "Alternance Risk & Cybersecurity Analyst - 24 mois. Évaluation de la maturité cybersécurité de clients grands comptes, rédaction de plans d'action, coordination avec les équipes techniques.",
     False,
     "CV transmis par un contact LinkedIn. À relancer cette semaine."),

    # ── APPLIED ───────────────────────────────────────────────────────────
    (3, "Applied", "Alternance", 15, "1 400 €/mois", "Paris (75)",
     "https://www.capgemini.com/fr-fr/carrieres/",
     "Alternance DevSecOps Engineer - 24 mois. Automatisation de la sécurité dans les pipelines CI/CD, gestion des secrets (HashiCorp Vault), revue de code sécurisé.",
     False,
     "Candidature déposée via le portail Capgemini. Postulé en réponse à une annonce LinkedIn."),

    (7, "Applied", "Alternance", 12, "1 350 €/mois", "Grenoble (38)",
     "https://atos.net/fr/france/carrieres",
     "Alternance Cloud Security Engineer - 24 mois. Sécurisation des environnements Azure/AWS, gestion des identités IAM, revue des configurations de sécurité.",
     False,
     "Candidature via Atos Careers. Offre vue sur LinkedIn."),

    (9, "Applied", "Alternance", 10, "1 400 €/mois", "Paris (75)",
     "https://careers.societegenerale.com",
     "Alternance Analyste Cybersécurité - 24 mois. Participation aux revues SOC, analyse de logs Splunk, gestion des accès privilégiés CyberArk, suivi des vulnérabilités.",
     False,
     "Postulé via LinkedIn Easy Apply."),

    (10, "Applied", "Alternance", 8, "1 450 €/mois", "Nanterre (92)",
     "https://www.vinci-energies.com/fr/carrieres/",
     "Alternance Chef de Projet GRC Cybersécurité - 24 mois. Pilotage de projets de conformité NIS2/DORA, réalisation d'analyses EBIOS RM, tableaux de bord Power BI.",
     True,
     "Offre très bien alignée avec mon profil GRC. Lettre de motivation personnalisée rédigée."),

    (11, "Applied", "Alternance", 5, "1 300 €/mois", "Paris (75)",
     "https://www.inetum.com/fr/carrieres",
     "Alternance Pen Tester / Ethical Hacker - 24 mois. Tests d'intrusion web (OWASP Top 10), rédaction de rapports de vulnérabilités, CTF internes.",
     False,
     "Postulé via Indeed. Profil technique très axé pentest."),

    (12, "Applied", "Alternance", 3, "1 350 €/mois", "Paris (75)",
     "https://www.cnp.fr/travailler-chez-cnp/",
     "Alternance Risk Manager Cybersécurité - 24 mois. Identification et évaluation des risques SI, classification des actifs critiques, contribution au SMSI (ISO 27001).",
     False,
     "Candidature déposée ce matin. Secteur assurance intéressant pour DORA."),

    (14, "Applied", "Alternance", 2, "1 500 €/mois", "Bois-Colombes (92)",
     "https://www.ibm.com/fr-fr/employment/",
     "Alternance Cybersecurity Analyst - QRadar SIEM - 24 mois. Déploiement et tuning de règles QRadar, analyse des menaces, corrélation d'événements de sécurité, reporting.",
     False,
     "IBM France — très bon nom pour le CV. Offre en anglais."),

    # ── WISHLIST ──────────────────────────────────────────────────────────
    (6, "Wishlist", "Stage", 0, None, "Paris (75)",
     "https://www.ssi.gouv.fr/agence/recrutement/",
     "Stage Analyste Sécurité / Reverse Engineering - 6 mois. Analyse de binaires malveillants, rédaction de rapports d'incidents, participation aux exercices de crise cyber.",
     True,
     "Rêve de stage ! Compétences requises : C, Python, assembleur, Ghidra/IDA Pro. À postuler en priorité."),
]

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("🔌 Connexion à PostgreSQL…")
    try:
        conn = psycopg.connect(CONN_STR)
    except Exception as e:
        print(f"❌ Impossible de se connecter à la base de données :\n   {e}")
        print("\n💡 Assurez-vous que PostgreSQL tourne et que docker-compose est démarré.")
        sys.exit(1)

    with conn:
        with conn.cursor() as cur:
            # Vérifier si des données existent déjà
            cur.execute("SELECT COUNT(*) FROM companies")
            count = cur.fetchone()[0]
            if count > 0:
                print(f"⚠️  La base contient déjà {count} entreprise(s).")
                print("   Pour re-seeder, vide d'abord : DELETE FROM notes; DELETE FROM applications; DELETE FROM companies;")
                return

            # 1. Insérer les entreprises
            company_ids = []
            for name, sector, tech_stack, glassdoor, linkedin in COMPANIES:
                cid = uid()
                company_ids.append(cid)
                cur.execute("""
                    INSERT INTO companies (id, name, sector, tech_stack, glassdoor_link, linkedin_link)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (cid, name, sector, tech_stack, glassdoor, linkedin))
            print(f"✅ {len(company_ids)} entreprises insérées.")

            # 2. Insérer les candidatures + notes
            app_count = 0
            note_count = 0
            for (cidx, status, app_type, days_ago, salary, location,
                 job_url, description, flagged, note_text) in APPLICATIONS:

                app_id = uid()
                sent_dt = dt(days_ago) if days_ago > 0 else None
                last_contact = dt(max(days_ago - 5, 0))

                cur.execute("""
                    INSERT INTO applications
                      (id, company_id, date_sent, last_contact_date, status,
                       salary_proposed, type, job_url, location, raw_description, is_flagged)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (app_id, company_ids[cidx], sent_dt, last_contact, status,
                      salary, app_type, job_url, location, description, flagged))
                app_count += 1

                if note_text:
                    note_created = dt(max(days_ago - 2, 0))
                    cur.execute("""
                        INSERT INTO notes (id, application_id, content, created_at)
                        VALUES (%s, %s, %s, %s)
                    """, (uid(), app_id, note_text, note_created))
                    note_count += 1

            print(f"✅ {app_count} candidatures insérées.")
            print(f"✅ {note_count} notes insérées.")
            print("\n🎉 Seed terminé avec succès ! Lance NEXUS et explore tes candidatures.")

    conn.close()

if __name__ == "__main__":
    main()
