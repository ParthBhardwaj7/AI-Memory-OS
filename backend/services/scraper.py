import requests
from bs4 import BeautifulSoup

class WebScraper:
    """
    Service to scrape article body text and metadata from website URLs.
    """

    @staticmethod
    def scrape(url: str) -> str:
        """
        Dispatches a GET request to the target URL, extracts paragraphs and main headings
        using BeautifulSoup, cleans whitespace, and returns the raw clean text content.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return f"Failed to retrieve webpage. Status code: {response.status_code}"
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script, style, navigation, header, footer elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                element.extract()
                
            # Extract content from paragraph tags and headings
            content_tags = soup.find_all(["p", "h1", "h2", "h3", "h4", "article"])
            text_blocks = [tag.get_text().strip() for tag in content_tags if tag.get_text().strip()]
            
            if not text_blocks:
                # Fallback to general page text if no structural tags found
                text = soup.get_text(separator="\n")
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = "\n".join(chunk for chunk in chunks if chunk)
                return clean_text
                
            return "\n\n".join(text_blocks)
        except Exception as e:
            return f"Error scraping website: {str(e)}"
