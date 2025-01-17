# Review Scraper API

An API server that extracts product reviews from any e-commerce website using AI-powered dynamic CSS identification.
This works only for amazon  product page !!!

## Features

- Dynamic CSS selector identification using Gemini AI
- Automated review extraction with pagination support
- Universal compatibility with different e-commerce platforms
- FastAPI-based REST API

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```
4. Create `.env` file from `.env.example` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the server:
   ```bash
   python -m src.main
   ```

2. Make API requests:
   ```bash
   curl "http://localhost:8000/api/reviews?page=https://example.com/product"
   ```

## API Specification

### GET /api/reviews

Parameters:
- `page`: URL of the product page (required)


