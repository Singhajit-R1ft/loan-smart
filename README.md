# Loan Smart

Compare 2-3 loan offers, see the EMI and total cost of each, find the cheapest, and get a simple AI explanation.

Built for Arthaton 2026 (AI for Finance).

## Features
- EMI, total interest and total payment for each offer
- Processing fee included in total cost
- Cheapest offer highlighted, plus a bar chart
- Optional monthly income: warns if EMI is above 40% of income
- AI explanation via Gemini (falls back to a basic summary without a key)

## Formula
EMI = P × r × (1+r)^n / ((1+r)^n − 1)
P = loan amount, r = annual rate / 12 / 100, n = months

## Run
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key   # optional; Windows: set GEMINI_API_KEY=your_key
streamlit run app.py
```
Free key: https://aistudio.google.com

## Screenshots
(add screenshots here)

## Disclaimer
Educational tool only, not financial advice.
