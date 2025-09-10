"""
AI-Powered Financial Statement Scraper using LLM for intelligent extraction.
This replaces the regex-based approach with an AI agent that understands financial documents.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

from app.core.logging import get_logger
from app.core.config import AppConfig
from app.core.exceptions import ProcessingError, APIError

load_dotenv()

logger = get_logger(__name__)


class AIFinancialScraper:
    """
    AI-powered scraper that uses LLM to intelligently extract financial statements
    from SEC 10-Q documents with high accuracy and adaptability.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize the AI Financial Scraper.
        
        Args:
            model (str): OpenAI model to use for extraction
        """
        self.client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
        self.model = model
        logger.info(f"🤖 Initialized AI Financial Scraper with model: {model}")
    
    def extract_financial_statements_ai(self, file_path: str, ticker: str) -> Dict[str, Any]:
        """
        Extract financial statements using AI for intelligent parsing.
        
        Args:
            file_path (str): Path to the HTML file
            ticker (str): Stock ticker symbol for context
            
        Returns:
            Dict[str, Any]: Extracted financial data with high accuracy
        """
        logger.info(f"🤖 AI-extracting financial statements from: {file_path}")
        
        try:
            # Read and clean the HTML content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean HTML for better AI processing
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove scripts, styles, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Extract text content
            text_content = soup.get_text()
            
            # Limit content size for API (keep most relevant parts)
            text_content = self._truncate_content(text_content, max_chars=50000)
            
            # Use AI to extract financial statements
            financial_data = self._ai_extract_financials(text_content, ticker)
            
            logger.info(f"🤖 AI extraction complete - Income: {len(financial_data.get('income_statement', {}))} items, "
                       f"Balance: {len(financial_data.get('balance_sheet', {}))} items, "
                       f"Cash Flow: {len(financial_data.get('cash_flow', {}))} items")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"❌ AI extraction failed for {file_path}: {e}")
            raise ProcessingError(f"AI extraction failed for {file_path}: {e}")
    
    def _ai_extract_financials(self, content: str, ticker: str) -> Dict[str, Any]:
        """
        Use AI to extract financial statements from text content.
        
        Args:
            content (str): Cleaned text content from HTML
            ticker (str): Stock ticker for context
            
        Returns:
            Dict[str, Any]: Structured financial data
        """
        prompt = f"""
You are a financial data extraction expert. Extract financial statements from the following SEC 10-Q document for {ticker}.

INSTRUCTIONS:
1. Identify and extract Income Statement, Balance Sheet, and Cash Flow Statement data
2. For each financial statement, extract account names and their corresponding values
3. Values should be in millions of USD (convert if necessary)
4. Return ONLY valid JSON in the exact format specified below
5. If a statement is not found, return an empty object {{}}
6. Be precise with account names and values

REQUIRED JSON FORMAT:
{{
    "income_statement": {{
        "Revenue": [value1, value2],
        "Cost of Revenue": [value1, value2],
        "Gross Profit": [value1, value2],
        "Operating Income": [value1, value2],
        "Net Income": [value1, value2]
    }},
    "balance_sheet": {{
        "Total Assets": [value1, value2],
        "Current Assets": [value1, value2],
        "Total Liabilities": [value1, value2],
        "Current Liabilities": [value1, value2],
        "Shareholders Equity": [value1, value2]
    }},
    "cash_flow": {{
        "Operating Cash Flow": [value1, value2],
        "Investing Cash Flow": [value1, value2],
        "Financing Cash Flow": [value1, value2],
        "Net Cash Flow": [value1, value2]
    }},
    "metadata": {{
        "company_name": "Company Name",
        "periods": ["Period 1", "Period 2"],
        "extraction_method": "ai_llm"
    }}
}}

DOCUMENT CONTENT:
{content[:40000]}  # Limit content size
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial data extraction expert. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=4000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Clean and parse JSON
            ai_response = self._clean_ai_response(ai_response)
            financial_data = json.loads(ai_response)
            
            logger.info(f"🤖 AI successfully extracted financial data for {ticker}")
            return financial_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response as JSON: {e}")
            logger.debug(f"AI Response: {ai_response}")
            return self._fallback_extraction(content, ticker)
        except Exception as e:
            logger.error(f"❌ AI extraction failed: {e}")
            return self._fallback_extraction(content, ticker)
    
    def _clean_ai_response(self, response: str) -> str:
        """
        Clean AI response to ensure valid JSON.
        
        Args:
            response (str): Raw AI response
            
        Returns:
            str: Cleaned JSON string
        """
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Remove any text before the first {
        first_brace = response.find('{')
        if first_brace > 0:
            response = response[first_brace:]
        
        # Remove any text after the last }
        last_brace = response.rfind('}')
        if last_brace > 0:
            response = response[:last_brace + 1]
        
        return response.strip()
    
    def _fallback_extraction(self, content: str, ticker: str) -> Dict[str, Any]:
        """
        Fallback extraction method if AI fails.
        
        Args:
            content (str): Text content
            ticker (str): Stock ticker
            
        Returns:
            Dict[str, Any]: Basic extracted data
        """
        logger.warning(f"⚠️ Using fallback extraction for {ticker}")
        
        return {
            'income_statement': {},
            'balance_sheet': {},
            'cash_flow': {},
            'metadata': {
                'company_name': ticker,
                'periods': [],
                'extraction_method': 'fallback'
            }
        }
    
    def _truncate_content(self, content: str, max_chars: int = 50000) -> str:
        """
        Truncate content to fit within API limits while keeping most relevant parts.
        
        Args:
            content (str): Full content
            max_chars (int): Maximum characters
            
        Returns:
            str: Truncated content
        """
        if len(content) <= max_chars:
            return content
        
        # Keep the beginning and end of the document
        half_chars = max_chars // 2
        truncated = content[:half_chars] + "\n\n[... CONTENT TRUNCATED ...]\n\n" + content[-half_chars:]
        
        logger.debug(f"📝 Truncated content from {len(content)} to {len(truncated)} characters")
        return truncated
    
    def extract_with_confidence(self, file_path: str, ticker: str) -> Tuple[Dict[str, Any], float]:
        """
        Extract financial statements with confidence score.
        
        Args:
            file_path (str): Path to HTML file
            ticker (str): Stock ticker
            
        Returns:
            Tuple[Dict[str, Any], float]: (financial_data, confidence_score)
        """
        try:
            financial_data = self.extract_financial_statements_ai(file_path, ticker)
            
            # Calculate confidence based on extracted data quality
            confidence = self._calculate_confidence(financial_data)
            
            logger.info(f"🤖 Extraction confidence for {ticker}: {confidence:.2f}")
            return financial_data, confidence
            
        except Exception as e:
            logger.error(f"❌ Confidence extraction failed: {e}")
            return {}, 0.0
    
    def _calculate_confidence(self, financial_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on extracted data quality.
        
        Args:
            financial_data (Dict[str, Any]): Extracted financial data
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        confidence = 0.0
        
        # Check for key financial statement items
        income_items = financial_data.get('income_statement', {})
        balance_items = financial_data.get('balance_sheet', {})
        cashflow_items = financial_data.get('cash_flow', {})
        
        # Revenue is critical for income statement
        if 'Revenue' in income_items or 'Total Revenue' in income_items:
            confidence += 0.3
        
        # Net Income is critical
        if 'Net Income' in income_items:
            confidence += 0.2
        
        # Total Assets is critical for balance sheet
        if 'Total Assets' in balance_items:
            confidence += 0.2
        
        # Operating Cash Flow is important
        if 'Operating Cash Flow' in cashflow_items:
            confidence += 0.1
        
        # Bonus for having multiple statements
        statement_count = sum([
            len(income_items) > 0,
            len(balance_items) > 0,
            len(cashflow_items) > 0
        ])
        confidence += statement_count * 0.1
        
        return min(confidence, 1.0)


# Backward compatibility
def extract_financial_statements_ai(file_path: str, ticker: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    scraper = AIFinancialScraper()
    return scraper.extract_financial_statements_ai(file_path, ticker)


def extract_with_confidence(file_path: str, ticker: str) -> Tuple[Dict[str, Any], float]:
    """Backward compatibility function."""
    scraper = AIFinancialScraper()
    return scraper.extract_with_confidence(file_path, ticker)
