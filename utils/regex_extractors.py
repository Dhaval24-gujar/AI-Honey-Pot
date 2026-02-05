"""
Regex-based intelligence extraction utilities
"""
import re
from typing import List, Tuple


def extract_bank_accounts(text: str) -> List[str]:
    """
    Extract bank account numbers and IFSC codes
    
    Args:
        text: Text to search
        
    Returns:
        List of masked bank account numbers
    """
    accounts = []
    
    # Patterns for bank account numbers
    patterns = [
        r'\b\d{9,18}\b',  # Account numbers (9-18 digits)
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4,6}\b',  # Formatted account
        r'[A-Z]{4}0[A-Z0-9]{6}',  # IFSC codes
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            cleaned = match.replace("-", "").replace(" ", "")
            if len(cleaned) >= 9:
                # Mask for privacy: show first 4 and last 4 digits
                masked = f"{cleaned[:4]}-{'X'*(len(cleaned)-8)}-{cleaned[-4:]}"
                if masked not in accounts:
                    accounts.append(masked)
    
    return accounts


def extract_upi_ids(text: str) -> List[str]:
    """
    Extract UPI IDs from text
    
    Args:
        text: Text to search
        
    Returns:
        List of UPI IDs
    """
    upi_ids = []
    
    # Pattern for UPI IDs (email-like format)
    upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
    matches = re.findall(upi_pattern, text)
    
    # Common UPI providers
    upi_providers = [
        'paytm', 'phonepe', 'googlepay', 'gpay', 'ybl', 'axl',
        'okhdfcbank', 'oksbi', 'okicici', 'ibl', 'upi'
    ]
    
    for match in matches:
        if '@' in match:
            # Check if it's a known UPI provider
            if any(provider in match.lower() for provider in upi_providers):
                if match not in upi_ids:
                    upi_ids.append(match)
    
    return upi_ids


def extract_phone_numbers(text: str) -> List[str]:
    """
    Extract phone numbers (Indian format)
    
    Args:
        text: Text to search
        
    Returns:
        List of phone numbers in +91 format
    """
    phones = []
    
    patterns = [
        r'\+91[-\s]?\d{10}',  # +91 format
        r'\b[6-9]\d{9}\b',  # 10 digit Indian mobile
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for phone in matches:
            cleaned = re.sub(r'[-\s]', '', phone)
            # Ensure it starts with +91
            if len(cleaned) == 10:
                cleaned = f"+91{cleaned}"
            if cleaned not in phones:
                phones.append(cleaned)
    
    return phones


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs and phishing links
    
    Args:
        text: Text to search
        
    Returns:
        List of URLs
    """
    urls = []
    
    # Full URL pattern
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    url_matches = re.findall(url_pattern, text)
    urls.extend(url_matches)
    
    # Shortened URL pattern
    short_url_pattern = r'\b(?:bit\.ly|tinyurl\.com|goo\.gl|t\.co)/[A-Za-z0-9]+'
    short_urls = re.findall(short_url_pattern, text)
    
    for url in short_urls:
        full_url = f"http://{url}" if not url.startswith('http') else url
        if full_url not in urls:
            urls.append(full_url)
    
    return urls
