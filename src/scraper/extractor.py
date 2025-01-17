from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from typing import Dict, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReviewExtractor:
    def __init__(self):
        self.driver = None
        # Common patterns for review elements
        self.selector_patterns = {
            "shopify": {
                "review_container": ".shopify-product-reviews-widget, .spr-review, .product-reviews-widget",
                "title": ".spr-review-header-title, .review-title",
                "text": ".spr-review-content-body, .review-content",
                "rating": ".spr-review-rating, .rating",
                "reviewer": ".spr-review-header-byline, .review-author"
            },
            "generic": {
                "review_container": "[class*='review'], [id*='review']",
                "title": "[class*='review-title'], [class*='review-header']",
                "text": "[class*='review-content'], [class*='review-text']",
                "rating": "[class*='rating'], [class*='stars']",
                "reviewer": "[class*='review-author'], [class*='reviewer']"
            }
        }

    def _setup_driver(self):
        """Initialize and configure the Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise Exception(f"WebDriver setup failed: {str(e)}")

    def _cleanup_driver(self):
        """Clean up WebDriver resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup WebDriver: {str(e)}")

    def _extract_rating(self, element, selector) -> float:
        """Extract and normalize rating value"""
        try:
            rating_text = element.find_element(By.CSS_SELECTOR, selector).text.strip()
            # Extract numbers from text (e.g., "4.5 out of 5" -> 4.5)
            numbers = re.findall(r'\d+\.?\d*', rating_text)
            if numbers:
                return float(numbers[0])
            return 0
        except Exception:
            return 0

    def _find_reviews(self, patterns) -> List[Dict]:
        """Find and extract reviews using given patterns"""
        reviews = []
        try:
            containers = self.driver.find_elements(By.CSS_SELECTOR, patterns["review_container"])
            for container in containers:
                try:
                    review = {
                        "title": "",
                        "text": "",
                        "rating": 0,
                        "reviewer": ""
                    }
                    
                    # Try to extract each field
                    try:
                        review["title"] = container.find_element(
                            By.CSS_SELECTOR, patterns["title"]
                        ).text.strip()
                    except: pass

                    try:
                        review["text"] = container.find_element(
                            By.CSS_SELECTOR, patterns["text"]
                        ).text.strip()
                    except: pass

                    try:
                        review["rating"] = self._extract_rating(container, patterns["rating"])
                    except: pass

                    try:
                        review["reviewer"] = container.find_element(
                            By.CSS_SELECTOR, patterns["reviewer"]
                        ).text.strip()
                    except: pass

                    # Only add review if it has at least text or title
                    if review["text"] or review["title"]:
                        reviews.append(review)
                        
                except Exception as e:
                    logger.warning(f"Error extracting individual review: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error with pattern set: {str(e)}")
            
        return reviews

    async def extract_reviews(self, page: str) -> Dict:
        """Extract reviews from the given page URL"""
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info(f"Navigating to page: {page}")
            self.driver.get(page)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            all_reviews = []
            
            # Try Shopify patterns first
            shopify_reviews = self._find_reviews(self.selector_patterns["shopify"])
            if shopify_reviews:
                all_reviews.extend(shopify_reviews)
            
            # If no reviews found, try generic patterns
            if not all_reviews:
                generic_reviews = self._find_reviews(self.selector_patterns["generic"])
                all_reviews.extend(generic_reviews)
            
            logger.info(f"Found {len(all_reviews)} reviews")
            
            return {
                "reviews": all_reviews,
                "reviews_count": len(all_reviews)
            }
        
        except Exception as e:
            logger.error(f"Error in extract_reviews: {str(e)}")
            raise Exception(f"Error extracting reviews: {str(e)}")
        
        finally:
            self._cleanup_driver()