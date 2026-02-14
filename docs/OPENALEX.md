# OpenAlex Integration

## Why OpenAlex?

We switched from PubMed + RSS feeds to **OpenAlex** as our primary source:

### ✅ Advantages
- **Completely free** — no API limits, no paywalls
- **Open data** — CC0 license, no copyright issues
- **Comprehensive** — 200M+ papers across all fields
- **No registration required** — just add your email to be polite
- **Stable API** — well-maintained by OurResearch
- **No RELX dependency** — independent of commercial publishers

### 📊 Coverage
- PubMed papers included
- Preprints from bioRxiv, medRxiv
- Major medical journals
- Conference proceedings

### 🔧 How It Works
1. Queries OpenAlex API by **concepts** (Cardiology, Endocrinology)
2. Searches by **keywords** in titles/abstracts
3. Filters by publication date (last 3 days)
4. Sorts by citation count (most impactful first)

### 📧 API Etiquette
Add your email to `User-Agent` header for better service:
```python
headers = {"User-Agent": "mailto:you@yourdomain.com"}
```

### 🌐 Resources
- API Docs: https://docs.openalex.org
- Website: https://openalex.org
- Coverage: https://openalex.org/faq#where-does-your-data-come-from

---

**Note:** Some papers may have limited abstracts. The summarizer handles this gracefully by generating placeholders for full-text review.
