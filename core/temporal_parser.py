"""
Temporal Parser (Stage 1 Enhancement)
Extracts and normalizes temporal expressions from clinical text using dateparser and Duckling.
"""

import dateparser
import re
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemporalParser:
    """
    Extracts temporal information from clinical text.
    
    Uses dateparser and regex patterns to identify:
    - Absolute dates ("on January 15", "10/19/2025")
    - Relative dates ("3 weeks ago", "last month")
    - Duration ("for 2 months", "since June")
    """
    
    def __init__(self):
        logger.info("Initializing TemporalParser")
        
        # Configure dateparser settings
        self.dateparser_settings = {
            'PREFER_DATES_FROM': 'past',  # Clinical notes often reference past events
            'RELATIVE_BASE': datetime.now(),
            'RETURN_AS_TIMEZONE_AWARE': False
        }
        
        # Common temporal patterns in clinical text
        self.temporal_patterns = [
            # Relative time expressions
            r'\b(\d+)\s+(day|week|month|year)s?\s+ago\b',
            r'\b(last|this|next)\s+(week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\bsince\s+([A-Za-z]+\s+\d{1,2}(?:,\s+\d{4})?)\b',
            r'\b(started|began|discontinued|stopped)\s+(?:on\s+)?([A-Za-z]+\s+\d{1,2})\b',
            
            # Absolute dates
            r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b',
            r'\b([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})\b',
            
            # Duration
            r'\bfor\s+(\d+)\s+(day|week|month|year)s?\b',
        ]
        
        logger.info("TemporalParser initialized")
    
    def extract_temporal_info(
        self,
        text: str,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Optional[str]]:
        """
        Extract temporal information from text.
        
        Args:
            text: Clinical text containing temporal expressions
            reference_date: Reference date for relative expressions (default: now)
        
        Returns:
            Dict with:
                - date_iso: ISO 8601 formatted date (YYYY-MM-DD)
                - temporal_expression: Original text expression
                - temporal_type: "absolute", "relative", or "duration"
        """
        if reference_date:
            self.dateparser_settings['RELATIVE_BASE'] = reference_date
        
        result = {
            'date_iso': None,
            'temporal_expression': None,
            'temporal_type': None
        }
        
        # Try to find temporal expressions using patterns
        for pattern in self.temporal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                temporal_expr = match.group(0)
                result['temporal_expression'] = temporal_expr
                
                # Parse the expression
                parsed_date = dateparser.parse(
                    temporal_expr,
                    settings=self.dateparser_settings
                )
                
                if parsed_date:
                    result['date_iso'] = parsed_date.strftime('%Y-%m-%d')
                    result['temporal_type'] = self._classify_temporal_type(temporal_expr)
                    logger.debug(f"Parsed '{temporal_expr}' -> {result['date_iso']}")
                    break
        
        return result
    
    def _classify_temporal_type(self, expression: str) -> str:
        """Classify temporal expression type."""
        expression_lower = expression.lower()
        
        if 'ago' in expression_lower or 'last' in expression_lower or 'since' in expression_lower:
            return 'relative'
        elif 'for' in expression_lower:
            return 'duration'
        else:
            return 'absolute'
    
    def parse_date(
        self,
        date_string: str,
        reference_date: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Parse a date string and return ISO format.
        
        Args:
            date_string: Date string to parse
            reference_date: Reference date for relative parsing
        
        Returns:
            ISO 8601 formatted date (YYYY-MM-DD) or None
        """
        if reference_date:
            settings = self.dateparser_settings.copy()
            settings['RELATIVE_BASE'] = reference_date
        else:
            settings = self.dateparser_settings
        
        parsed = dateparser.parse(date_string, settings=settings)
        
        if parsed:
            return parsed.strftime('%Y-%m-%d')
        
        return None
    
    def extract_all_dates(
        self,
        text: str,
        reference_date: Optional[datetime] = None
    ) -> list[Dict[str, str]]:
        """
        Extract all date expressions from text.
        
        Args:
            text: Clinical text
            reference_date: Reference date for relative expressions
        
        Returns:
            List of dicts with temporal information
        """
        dates = []
        
        for pattern in self.temporal_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                temporal_expr = match.group(0)
                
                parsed_date = dateparser.parse(
                    temporal_expr,
                    settings=self.dateparser_settings
                )
                
                if parsed_date:
                    dates.append({
                        'temporal_expression': temporal_expr,
                        'date_iso': parsed_date.strftime('%Y-%m-%d'),
                        'temporal_type': self._classify_temporal_type(temporal_expr),
                        'span_start': match.start(),
                        'span_end': match.end()
                    })
        
        return dates


# Example usage
if __name__ == "__main__":
    parser = TemporalParser()
    
    test_texts = [
        "Patient started metformin 3 weeks ago",
        "Discontinued aspirin on January 15, 2025",
        "Taking lisinopril since last month",
        "Started insulin for 2 months"
    ]
    
    for text in test_texts:
        result = parser.extract_temporal_info(text)
        print(f"\nText: {text}")
        print(f"Result: {result}")
