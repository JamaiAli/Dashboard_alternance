import requests
from bs4 import BeautifulSoup
import re

class ScrapingService:
    @staticmethod
    def extract_text_from_url(url: str) -> str:
        """
        Extracts raw text content from the given URL.
        Uses a standard User-Agent to avoid simple blocking.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up extra spaces/newlines
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            return cleaned_text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
