"""
Helper utility functions.
Reusable functions following DRY principle.
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing extra whitespace and normalizing.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    words = text.split()
    return len(words)


def truncate_text(text: str, max_words: int) -> str:
    """
    Truncate text to maximum word count.
    
    Args:
        text: Input text
        max_words: Maximum number of words
        
    Returns:
        Truncated text
    """
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'


def format_date(date_str: str, input_format: str = "%Y-%m-%d", output_format: str = "%B %d, %Y") -> str:
    """Format date string."""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text that may contain additional content.
    Tries multiple strategies to parse JSON from LLM responses.
    """
    cleaned = clean_json_response(text)
    
    # Strategy 1: Direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Find JSON objects
    json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    matches.sort(key=len, reverse=True)
    
    for match in matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict) and ('title' in parsed or 'introduction' in parsed):
                return parsed
        except json.JSONDecodeError:
            continue
    
    # Strategy 3: Fix common errors
    try:
        fixed_text = cleaned.replace("'", '"')
        return json.loads(fixed_text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 4: Remove trailing commas
    try:
        fixed_text = re.sub(r',\s*}', '}', cleaned)
        fixed_text = re.sub(r',\s*]', ']', fixed_text)
        return json.loads(fixed_text)
    except json.JSONDecodeError:
        pass
    
    return None


def clean_json_response(response: str) -> str:
    """Clean JSON response by removing markdown and extra text."""
    response = response.strip()
    
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'```javascript\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'```\s*', '', response)
    
    # Remove common prefixes
    prefixes = [
        r'^Here is the JSON.*?:',
        r'^Here is the cover letter.*?:',
        r'^The JSON response is.*?:',
        r'^Response:', r'^Output:', r'^JSON:',
    ]
    for prefix in prefixes:
        response = re.sub(prefix, '', response, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove trailing text after last }
    last_brace = response.rfind('}')
    if last_brace != -1:
        response = response[:last_brace + 1]
    
    # Extract JSON content
    json_match = re.search(r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0).strip()
    
    return response.strip()


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate that required fields are present in data."""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields


def merge_dicts_deep(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_deep(result[key], value)
        else:
            result[key] = value
    
    return result


def format_list_as_bullets(items: List[str], indent: int = 0) -> str:
    """Format list items as bullet points."""
    indent_str = "  " * indent
    return "\n".join([f"{indent_str}• {item}" for item in items])


def calculate_similarity_score(text1: str, text2: str) -> float:
    """Calculate simple similarity score between two texts (Jaccard similarity)."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

