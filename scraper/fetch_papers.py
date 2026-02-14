#!/usr/bin/env python3
"""
MedLit AI - Paper Scraper
Main entry point - uses OpenAlex as primary source
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openalex_scraper import OpenAlexScraper

def main():
    """Run scraper for all specialties"""
    os.makedirs("../data", exist_ok=True)
    
    scraper = OpenAlexScraper()
    total = scraper.fetch_all_specialties(days_back=3)
    
    print(f"\n{'='*50}")
    print(f"✅ Scraping complete!")
    print(f"📚 Total new papers added: {total}")
    print(f"{'='*50}")
    
    scraper.close()


if __name__ == "__main__":
    main()
