#!/usr/bin/env python3
"""
MedLit AI - AI Summarizer
Processes medical papers and extracts clinical takeaways
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.openalex_scraper import OpenAlexScraper as PaperScraper

DB_PATH = "data/medlit.db"

class PaperSummarizer:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._init_db()
        self.api_key = self._load_config().get("openai_api_key", "")
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            return {}
    
    def _init_db(self):
        """Initialize summaries table"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT UNIQUE,
                key_finding TEXT,
                clinical_impact TEXT,
                action_item TEXT,
                audience TEXT,
                confidence TEXT,
                created_at TEXT,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            )
        ''')
        self.conn.commit()
    
    def summarize_with_ai(self, paper: Dict) -> Dict:
        """
        Generate AI summary of a medical paper
        For MVP, using rule-based extraction + template
        In production, replace with actual LLM API call
        """
        title = paper["title"]
        abstract = paper["abstract"]
        specialty = paper["specialty"]
        
        # Handle missing/short abstracts (common with OpenAlex)
        if not abstract or abstract == "Abstract not available" or len(abstract) < 50:
            return {
                "paper_id": paper["id"],
                "key_finding": f"Study on: {title[:150]}...",
                "clinical_impact": "🟡 Moderate - Review if relevant to practice",
                "action_item": "Read full text if topic matches your interest",
                "audience": self._determine_audience(title, ""),
                "confidence": "Moderate",
                "created_at": datetime.now().isoformat()
            }
        
        # Extract key finding from abstract
        key_finding = self._extract_key_finding(abstract, title)
        
        # Determine clinical impact
        clinical_impact = self._determine_impact(abstract, title, specialty)
        
        # Generate action item
        action_item = self._generate_action_item(abstract, specialty)
        
        # Determine target audience
        audience = self._determine_audience(title, abstract)
        
        # Confidence based on study type
        confidence = self._assess_confidence(abstract)
        
        return {
            "paper_id": paper["id"],
            "key_finding": key_finding,
            "clinical_impact": clinical_impact,
            "action_item": action_item,
            "audience": audience,
            "confidence": confidence,
            "created_at": datetime.now().isoformat()
        }
    
    def _extract_key_finding(self, abstract: str, title: str) -> str:
        """Extract main finding from abstract"""
        # Look for results/conclusion section
        abstract_lower = abstract.lower()
        
        # Common patterns indicating results
        result_indicators = [
            "results:", "we found", "showed that", "demonstrated",
            "associated with", "reduced", "increased", "improved",
            "significantly", "compared to", "versus"
        ]
        
        # If abstract is short, use it directly
        if len(abstract) < 300:
            return abstract[:200] + "..." if len(abstract) > 200 else abstract
        
        # Find sentences with results
        sentences = abstract.split(". ")
        for sentence in sentences:
            if any(ind in sentence.lower() for ind in result_indicators):
                return sentence.strip() + "."
        
        # Fallback: first sentence
        return sentences[0].strip() + "." if sentences else title
    
    def _determine_impact(self, abstract: str, title: str, specialty: str) -> str:
        """Determine clinical significance"""
        text = (title + " " + abstract).lower()
        
        high_impact = ["mortality", "death", "stroke", "mi", "heart attack", 
                       "kidney failure", "blindness", "amputation"]
        medium_impact = ["hospitalization", "quality of life", "symptoms",
                        "glycemic control", "bp control", "ldl"]
        
        if any(term in text for term in high_impact):
            return "🔴 High - May change mortality/morbidity outcomes"
        elif any(term in text for term in medium_impact):
            return "🟡 Moderate - Improves management/quality of care"
        else:
            return "🟢 Low - Incremental/adds to existing knowledge"
    
    def _generate_action_item(self, abstract: str, specialty: str) -> str:
        """Generate actionable recommendation"""
        abstract_lower = abstract.lower()
        
        # Drug/therapy studies
        if any(term in abstract_lower for term in ["trial", "randomized", "efficacy", "safety"]):
            if specialty == "cardiology":
                return "Consider for appropriate patients; discuss risk/benefit"
            else:
                return "Consider adding to regimen for eligible patients"
        
        # Guidelines/consensus
        if "guideline" in abstract_lower or "consensus" in abstract_lower:
            return "Review against current practice; update protocols if needed"
        
        # Biomarkers/diagnostics
        if any(term in abstract_lower for term in ["biomarker", "diagnostic", "screening"]):
            return "Consider for risk stratification or early detection"
        
        # Default
        return "Stay informed; may influence future patient discussions"
    
    def _determine_audience(self, title: str, abstract: str) -> str:
        """Determine target audience"""
        text = (title + " " + abstract).lower()
        
        if any(term in text for term in ["interventional", "pci", "cabg", "stent"]):
            return "Interventional Cardiologists"
        elif any(term in text for term in ["electrophysiology", "arrhythmia", "ablation", "af"]):
            return "EP Specialists"
        elif any(term in text for term in ["heart failure", "hfref", "hfpef"]):
            return "Heart Failure Specialists"
        elif any(term in text for term in ["insulin", "pump", "cgm", "glp-1", "sglt2"]):
            return "Endocrinologists / Diabetologists"
        else:
            return "General Cardiology / Medicine"
    
    def _assess_confidence(self, abstract: str) -> str:
        """Assess evidence quality"""
        abstract_lower = abstract.lower()
        
        if "randomized" in abstract_lower and "double-blind" in abstract_lower:
            return "High (RCT)"
        elif "meta-analysis" in abstract_lower:
            return "High (Meta-analysis)"
        elif "prospective" in abstract_lower:
            return "Moderate (Prospective)"
        elif "retrospective" in abstract_lower or "observational" in abstract_lower:
            return "Limited (Observational)"
        else:
            return "Moderate"
    
    def save_summary(self, summary: Dict):
        """Save summary to database"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO summaries 
                (paper_id, key_finding, clinical_impact, action_item, audience, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                summary["paper_id"],
                summary["key_finding"],
                summary["clinical_impact"],
                summary["action_item"],
                summary["audience"],
                summary["confidence"],
                summary["created_at"]
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving summary: {e}")
            return False
    
    def process_papers(self, specialty: str = None, limit: int = 10):
        """Process unsummarized papers"""
        cursor = self.conn.cursor()
        
        if specialty:
            cursor.execute('''
                SELECT p.* FROM papers p
                LEFT JOIN summaries s ON p.id = s.paper_id
                WHERE s.paper_id IS NULL AND p.specialty = ?
                ORDER BY p.fetched_at DESC
                LIMIT ?
            ''', (specialty, limit))
        else:
            cursor.execute('''
                SELECT p.* FROM papers p
                LEFT JOIN summaries s ON p.id = s.paper_id
                WHERE s.paper_id IS NULL
                ORDER BY p.fetched_at DESC
                LIMIT ?
            ''', (limit,))
        
        columns = [col[0] for col in cursor.description]
        papers = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        print(f"Processing {len(papers)} papers...")
        
        processed = 0
        for paper in papers:
            safe_title = paper['title'][:60].encode('ascii', 'ignore').decode('ascii')
            print(f"  Summarizing: {safe_title}...")
            summary = self.summarize_with_ai(paper)
            if self.save_summary(summary):
                processed += 1
        
        print(f"OK - Processed {processed} papers")
        return processed
    
    def get_daily_digest(self, specialty: str, date: str = None) -> List[Dict]:
        """Get formatted digest for a specialty"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.*, s.key_finding, s.clinical_impact, s.action_item, s.audience, s.confidence
            FROM papers p
            JOIN summaries s ON p.id = s.paper_id
            WHERE p.specialty = ? AND date(p.fetched_at) = date(?)
            ORDER BY p.fetched_at DESC
            LIMIT 5
        ''', (specialty, date))
        
        columns = [col[0] for col in cursor.description]
        papers = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return papers
    
    def close(self):
        self.conn.close()


def main():
    """Run summarizer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Summarize medical papers")
    parser.add_argument("--specialty", choices=["cardiology", "endocrinology"], help="Filter by specialty")
    parser.add_argument("--limit", type=int, default=10, help="Max papers to process")
    
    args = parser.parse_args()
    
    summarizer = PaperSummarizer()
    count = summarizer.process_papers(args.specialty, args.limit)
    summarizer.close()
    
    print(f"\nDone. Summarized {count} papers.")


if __name__ == "__main__":
    main()
