"""
PhishGuard - Quick CLI Demo
-----------------------------
Run this to see the model in action without starting the web server.
Usage:  python demo_cli.py
"""

import sys
import os
import joblib
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from feature_extractor import extract_features, FEATURE_NAMES, explain

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "phishguard_model.pkl")

TEST_URLS = [
    "https://github.com/anthropics",
    "https://www.wikipedia.org/wiki/Phishing",
    "http://paypal-secure-login.verify-account.tk/update",
    "http://192.168.4.22/wp-admin/verify.html",
    "http://update-icloud-billing.com/secure/login?ref=39281",
    "http://xn--pypal-4ve.com/login",
]

def main():
    print("Loading trained model...")
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    metrics = bundle["metrics"]
    print(f"Model test-set accuracy: {metrics['accuracy']*100:.1f}%  "
          f"(precision {metrics['precision']*100:.1f}%, recall {metrics['recall']*100:.1f}%)\n")

    urls = sys.argv[1:] if len(sys.argv) > 1 else TEST_URLS

    for url in urls:
        feats = extract_features(url)
        vec = pd.DataFrame([[feats[n] for n in FEATURE_NAMES]], columns=FEATURE_NAMES)
        prob = model.predict_proba(vec)[0][1]
        verdict = "MALICIOUS" if prob >= 0.70 else ("SUSPICIOUS" if prob >= 0.35 else "SAFE")

        print(f"URL: {url}")
        print(f"  Verdict: {verdict}   (phishing probability: {prob*100:.1f}%)")
        for sev, reason in explain(url, top_n=3):
            print(f"    [{sev.upper()}] {reason}")
        print()

if __name__ == "__main__":
    main()
