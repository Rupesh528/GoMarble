from fastapi import APIRouter, HTTPException
from src.scraper.extractor import ReviewExtractor
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/reviews")
async def get_reviews(page: str) -> Dict:
    """
    Extract reviews from the provided URL
    """
    logger.info(f"Received request to extract reviews from: {page}")
    
    try:
        extractor = ReviewExtractor()
        reviews = await extractor.extract_reviews(page)
        logger.info(f"Successfully extracted {reviews['reviews_count']} reviews")
        return reviews
    except Exception as e:
        logger.error(f"Failed to extract reviews: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract reviews: {str(e)}"
        )