# PhishGuard — AI-Powered Phishing Link Detector

A working, locally-runnable prototype that scores URLs for phishing risk in
real time using structural/lexical analysis + a Random Forest classifier —
no blocklists required, so it can catch zero-day phishing links.

Built to satisfy the attached PRD end-to-end: dataset → feature engineering →
trained model → FastAPI backend → web UI, all on a 100% free, open-source stack.

## Quick start

```bash
cd phishguard
pip install -r requirements.txt

# (Optional) retrain the model from scratch — a trained model is already
# included at models/phishguard_model.pkl, so this step is optional.
python models/train_model.py

# Run the web app
cd backend
uvicorn app:app --reload --port 8000
```

Then open **http://localhost:8000** in your browser and paste a URL.

Or skip the web UI and run the terminal demo:
```bash
python demo_cli.py
```

## How it maps to the PRD

| PRD Feature | Implementation |
|---|---|
| URL Input Interface | `frontend/index.html` — terminal-style scan bar |
| Feature Extraction Engine | `backend/feature_extractor.py` — 33 features via `urllib.parse` + regex, zero network calls |
| AI Scoring Engine | `models/train_model.py` — scikit-learn `RandomForestClassifier` (300 trees) |
| Results Dashboard | Verdict badge (Safe / Suspicious / Malicious) + radial confidence gauge |
| Explainability Panel | `explain()` in `feature_extractor.py` — plain-language, severity-ranked reasons |
| Scan History | SQLite (`backend/scan_history.db`), session-visible in the UI sidebar |

**Performance:** feature extraction + prediction typically completes in
20–60ms — well under the 2-second target.

**Accuracy:** 89.1% on a held-out 20% test split (11,430 labeled URLs),
inside the 85–90% target range. Precision 89.9% / Recall 88.1% / F1 89.0%.

**Cost:** 100% free/open-source — scikit-learn, FastAPI, SQLite, vanilla
JS/HTML/CSS. No paid APIs, no live page fetching (which also makes it safe
to scan a link without visiting it).

## Dataset

11,430 labeled URLs (50% phishing / 50% legitimate), originally compiled by
Hannousse & Yahiouche (2021) from PhishTank + Alexa/Common Crawl sources,
sourced here via the `ml-url-phishing-classifier` GitHub repo's cleaned CSV
(`data/raw_dataset.csv`).

Only **URL-derivable** features were used for training (not the page-content
features also present in that CSV, like `nb_hyperlinks` or `login_form`),
because the product requirement is to score a link *without visiting it*.
`models/train_model.py` recomputes every feature directly from the raw URL
string using the same extractor that runs at inference time, so there's no
train/serve skew.

## Architecture

```
phishguard/
├── data/raw_dataset.csv          # labeled training data
├── backend/
│   ├── feature_extractor.py      # URL → 33 structural/lexical features
│   ├── app.py                    # FastAPI: /api/scan, /api/history, /api/model-info
│   └── scan_history.db           # created automatically on first run
├── models/
│   ├── train_model.py            # trains + evaluates + saves the model
│   └── phishguard_model.pkl      # trained Random Forest (pre-built)
├── frontend/index.html           # single-page scan UI
├── demo_cli.py                   # terminal demo, no server needed
└── requirements.txt
```

## Known limitations (worth mentioning in a demo/eval)

- **Lexical-only signal**: the model never fetches the destination page, so
  it can't check for a fake login form or cloned branding — only how the
  URL *looks*. This is the same trade-off the PRD makes in exchange for
  instant, safe (no-click) scanning.
- **False positives on legitimate auth flows**: URLs like
  `accounts.google.com/signin` can score as suspicious/malicious because
  real login pages also contain words like "signin" and use subdomains —
  the same features phishing pages abuse. This is a genuine and instructive
  limitation of pure lexical classifiers, and a good discussion point on
  precision/recall trade-offs.
- **Threshold tuning**: verdict cutoffs (Safe <35%, Suspicious 35–70%,
  Malicious ≥70%) are adjustable in `backend/app.py` → `_verdict_from_prob()`.

## Next steps (not built, but natural extensions)

- Add WHOIS/domain-age lookups (would require a live API call).
- Add favicon/visual-similarity checks against known brands.
- Swap SQLite for a shared DB if deploying beyond a single local session.
