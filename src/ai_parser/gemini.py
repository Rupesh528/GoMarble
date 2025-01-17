from google.generativeai import GenerativeModel
import google.generativeai as genai
from src.config import settings
import json
import logging
import asyncio
from functools import partial

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAI:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = GenerativeModel('gemini-pro')

    async def analyze_page_structure(self, html_content: str) -> dict:
        """
        Analyze HTML content to identify review elements asynchronously
        """
        try:
            prompt = f"""
            Analyze this HTML content and identify the CSS selectors for review elements.
            Return only a JSON object with the following structure:
            {{
                "selectors": {{
                    "review_container": "CSS selector for review container",
                    "title": "CSS selector for review title",
                    "text": "CSS selector for review text",
                    "rating": "CSS selector for rating",
                    "reviewer": "CSS selector for reviewer name"
                }}
            }}
            HTML Content: {html_content}
            """
            
            # Run the Gemini generation in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(self.model.generate_content, prompt)
            )
            
            # Extract and parse the JSON response
            result = response.text
            try:
                selectors = json.loads(result)
                logger.info(f"Successfully parsed selectors: {selectors}")
                return selectors
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {result}")
                raise Exception(f"Invalid JSON response from AI: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            raise Exception(f"Failed to analyze page structure: {str(e)}")