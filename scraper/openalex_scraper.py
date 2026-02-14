#!/usr/bin/env python3
"""
MedLit AI - OpenAlex Scraper
Fetches latest papers from OpenAlex (free, open scholarly API)
"""

import requests
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict
import time

DB_PATH = "data/medlit.db"

# OpenAlex API endpoint
OPENALEX_BASE = "https://api.openalex.org/works"

# Search configurations by specialty
SPECIALTY_CONFIGS = {
    "cardiology": {
        "concepts": ["cardiology", "heart failure", "myocardial infarction", 
                     "arrhythmia", "coronary artery disease", "hypertension"],
        "keywords": ["cardiac", "heart", "cardiovascular", "stent", "pci", "cabg"]
    },
    "endocrinology": {
        "concepts": ["diabetes mellitus", "type 2 diabetes", "diabetic nephropathy",
                     "insulin resistance", "thyroid", "obesity", "metabolic syndrome"],
        "keywords": ["glp-1", "sglt2", "insulin", "hba1c", "thyroid", "cgm"]
    }
}

class OpenAlexScraper:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._init_db()
        self.session = requests.Session()
        email = self._load_config().get("admin_email", "user@medlit.ai")
        self.session.headers.update({
            "User-Agent": f"mailto:{email}"
        })
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            return {}
    
    def _init_db(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                abstract TEXT,
                authors TEXT,
                journal TEXT,
                pub_date TEXT,
                doi TEXT,
                specialty TEXT,
                source TEXT,
                openalex_id TEXT,
                fetched_at TEXT,
                summarized INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def fetch_papers(self, specialty: str, days_back: int = 3, per_page: int = 50) -> List[Dict]:
        """Fetch papers from OpenAlex for a specialty"""
        papers = []
        config = SPECIALTY_CONFIGS[specialty]
        
        # Build search query
        concept_filter = "|".join(config["concepts"])
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Build OpenAlex query
        params = {
            "filter": f"concepts.id:openalex:C{self._get_concept_hash(specialty)},from_publication_date:{start_date.strftime('%Y-%m-%d')}",
            "sort": "cited_by_count:desc",  # Most cited first = more impactful
            "per-page": per_page,
            "mailto": "your@email.com"  # Be nice to the API
        }
        
        # Also search by keywords in title/abstract
        keyword_queries = []
        for keyword in config["keywords"][:3]:  # Top 3 keywords
            keyword_params = {
                "search": keyword,
                "filter": f"from_publication_date:{start_date.strftime('%Y-%m-%d')}",
                "sort": "publication_date:desc",
                "per-page": 20,
                "mailto": "your@email.com"
            }
            
            try:
                response = self.session.get(OPENALEX_BASE, params=keyword_params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                for work in data.get("results", []):
                    paper = self._parse_openalex_work(work, specialty)
                    if paper and paper["id"] not in [p["id"] for p in papers]:
                        papers.append(paper)
                
                # Rate limiting - be nice to the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching keyword '{keyword}': {e}")
        
        # Fetch by concepts (main query)
        try:
            response = self.session.get(OPENALEX_BASE, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for work in data.get("results", []):
                paper = self._parse_openalex_work(work, specialty)
                if paper and paper["id"] not in [p["id"] for p in papers]:
                    papers.append(paper)
                    
        except Exception as e:
            print(f"Error fetching concept query for {specialty}: {e}")
        
        print(f"Fetched {len(papers)} papers for {specialty} from OpenAlex")
        return papers
    
    def _get_concept_hash(self, specialty: str) -> str:
        """Get OpenAlex concept ID for specialty"""
        # OpenAlex concept IDs (these are stable)
        concept_map = {
            "cardiology": "120531980",  # Cardiology concept
            "endocrinology": "131988081"  # Endocrinology concept
        }
        return concept_map.get(specialty, "")
    
    def _parse_openalex_work(self, work: Dict, specialty: str) -> Dict:
        """Parse OpenAlex work into paper dict"""
        try:
            # Get ID
            openalex_id = work.get("id", "").replace("https://openalex.org/", "")
            
            # Get title
            title = work.get("display_name", "No title")
            if not title or title == "No title":
                return None
            
            # Get abstract (OpenAlex has some abstracts)
            abstract = work.get("abstract", "")
            if not abstract:
                # Try to get from inverted index
                abstract_inv = work.get("abstract_inverted_index", {})
                if abstract_inv:
                    # Reconstruct abstract from inverted index
                    words = []
                    for word, positions in abstract_inv.items():
                        for pos in positions:
                            while len(words) <= pos:
                                words.append("")
                            words[pos] = word
                    abstract = " ".join(words)
            
            # Get authors
            authorships = work.get("authorships", [])
            authors = []
            for auth in authorships[:3]:  # First 3 authors
                author_name = auth.get("author", {}).get("display_name", "")
                if author_name:
                    authors.append(author_name)
            
            # Get journal/venue
            host_venue = work.get("host_venue", {}) or work.get("primary_location", {})
            if host_venue:
                journal = host_venue.get("display_name", "Unknown")
            else:
                journal = "Unknown"
            
            # Get publication date
            pub_date = work.get("publication_date", "")
            if not pub_date:
                pub_date = datetime.now().strftime("%Y")
            
            # Get DOI
            doi = work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else ""
            
            # Get OpenAlex URL for reference
            oa_url = work.get("open_access", {}).get("oa_url", "")
            
            return {
                "id": f"oa_{openalex_id}",
                "openalex_id": openalex_id,
                "title": title,
                "abstract": abstract[:2000] if abstract else "Abstract not available",  # Limit length
                "authors": ", ".join(authors) + (" et al." if len(authorships) > 3 else ""),
                "journal": journal,
                "pub_date": pub_date,
                "doi": doi,
                "specialty": specialty,
                "source": "openalex",
                "oa_url": oa_url
            }
            
        except Exception as e:
            print(f"Error parsing work: {e}")
            return None
    
    def save_papers(self, papers: List[Dict]) -> int:
        """Save papers to database, skip duplicates"""
        cursor = self.conn.cursor()
        added = 0
        
        for paper in papers:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO papers 
                    (id, title, abstract, authors, journal, pub_date, doi, specialty, source, openalex_id, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    paper["id"],
                    paper["title"],
                    paper["abstract"],
                    paper["authors"],
                    paper["journal"],
                    paper["pub_date"],
                    paper["doi"],
                    paper["specialty"],
                    paper["source"],
                    paper.get("openalex_id", ""),
                    datetime.now().isoformat()
                ))
                if cursor.rowcount > 0:
                    added += 1
            except Exception as e:
                print(f"Error saving paper {paper.get('id')}: {e}")
        
        self.conn.commit()
        return added
    
    def get_unsummarized(self, specialty: str = None, limit: int = 20) -> List[Dict]:
        """Get papers that need summarization"""
        cursor = self.conn.cursor()
        
        if specialty:
            cursor.execute('''
                SELECT * FROM papers 
                WHERE summarized = 0 AND specialty = ?
                ORDER BY fetched_at DESC
                LIMIT ?
            ''', (specialty, limit))
        else:
            cursor.execute('''
                SELECT * FROM papers 
                WHERE summarized = 0
                ORDER BY fetched_at DESC
                LIMIT ?
            ''', (limit,))
        
        columns = [col[0] for col in cursor.description]
        papers = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return papers
    
    def mark_summarized(self, paper_id: str):
        """Mark a paper as summarized"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE papers SET summarized = 1 WHERE id = ?', (paper_id,))
        self.conn.commit()
    
    def fetch_all_specialties(self, days_back: int = 3) -> int:
        """Fetch papers for all specialties"""
        total_added = 0
        
        for specialty in ["cardiology", "endocrinology"]:
            print(f"\n=== Fetching {specialty.upper()} from OpenAlex ===")
            papers = self.fetch_papers(specialty, days_back=days_back)
            added = self.save_papers(papers)
            print(f"Added {added} new papers")
            total_added += added
            
            # Rate limiting between specialties
            time.sleep(1)
        
        return total_added
    
    def close(self):
        self.conn.close()


def main():
    """Run scraper for all specialties"""
    import os
    os.makedirs("data", exist_ok=True)
    
    scraper = OpenAlexScraper()
    total = scraper.fetch_all_specialties(days_back=3)
    
    print(f"\n=== Total: {total} new papers added ===")
    scraper.close()


if __name__ == "__main__":
    main()
