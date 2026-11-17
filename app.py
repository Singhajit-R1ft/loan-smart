import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Loan Smart", page_icon="💰", layout="wide")


# ---------- Day 1: Calculator ----------
def calculate_emi(principal, annual_rate, months):
    """EMI = P * r * (1+r)^n / ((1+r)^n - 1)"""
    r = annual_rate / 12 / 100
    if months <= 0:
        return 0.0
    if r == 0:  # zero-interest loan
        return principal / months
    factor = (1 + r) ** months
    return principal * r * factor / (factor - 1)


def analyse_offer(name, principal, rate, years, fee_pct):
    months = int(years * 12)
    emi = calculate_emi(principal, rate, months)
    total_payment = emi * months
    total_interest = total_payment - principal
    fee = principal * fee_pct / 100
    total_cost = total_interest + fee  # what the loan costs you beyond the principal
    return {
        "Bank": name,
        "Amount": round(principal, 2),
        "Rate (%)": rate,
        "Tenure (months)": months,
        "Fee": round(fee, 2),
        "EMI": round(emi, 2),
        "Total Interest": round(total_interest, 2),
        "Total Payment": round(total_payment + fee, 2),
        "Total Cost": round(total_cost, 2),
    }


# ---------- Day 3: AI part ----------
def explain_with_ai(df, income, api_key):
    from google import genai

    client = genai.Client(api_key=api_key)
    prompt = f"""You are a friendly financial helper. Explain these loan offers in
simple words for a student or first-time borrower. Use short sentences.
1) Which offer is cheapest and why (mention actual numbers).
2) Warnings: hidden/processing fees, long tenure meaning more interest.
3) One practical tip.
Monthly income: {income if income else 'not given'}
Offers (Total Cost = interest + fee):
{df.to_string(index=False)}
Keep it under 150 words. This is not professional financial advice."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",  # change if Google renames the free model
        contents=prompt,
    )
    return response.text


def fallback_explanation(df, best):
    worst = df.loc[df["Total Cost"].idxmax()]
    saving = worst["Total Cost"] - best["Total Cost"]
    return (
        f"**{best['Bank']}** is the cheapest: total cost {best['Total Cost']:,.0f}. "
        f"Choosing it instead of **{worst['Bank']}** saves about {saving:,.0f}. "
        "Watch out for processing fees and long tenures; both raise what you pay."
    )


# ---------- UI ----------
st.title("💰 Loan Smart")
st.caption("Compare loan offers and understand the cheapest one in simple words.")

with st.sidebar:
    st.header("Settings")
    income = st.number_input("Monthly income (optional)", min_value=0.0, step=1000.0)
    api_key = st.text_input(
        "Gemini API key (optional)",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Free key from aistudio.google.com",
    )
    n_offers = st.radio("Number of offers", [2, 3], index=0)

# ---------- Day 2: Compare offers ----------
offers = []
cols = st.columns(n_offers)
defaults = [("Bank A", 500000, 9.5, 5, 1.0), ("Bank B", 500000, 10.5, 4, 0.5),
            ("Bank C", 500000, 9.0, 7, 2.0)]
for i, col in enumerate(cols):
    d = defaults[i]
    with col:
        st.subheader(f"Offer {i + 1}")
        name = st.text_input("Bank name", d[0], key=f"n{i}")
        amount = st.number_input("Loan amount", min_value=1000.0, value=float(d[1]),
                                 step=10000.0, key=f"a{i}")
        rate = st.number_input("Interest rate (% per year)", min_value=0.0, value=d[2],
                               step=0.1, key=f"r{i}")
        years = st.number_input("Tenure (years)", min_value=0.5, value=float(d[3]),
                                step=0.5, key=f"y{i}")
        fee_pct = st.number_input("Processing fee (% of loan)", min_value=0.0,
                                  value=d[4], step=0.1, key=f"f{i}")
        offers.append((name, amount, rate, years, fee_pct))

if st.button("Compare offers", type="primary"):
    df = pd.DataFrame([analyse_offer(*o) for o in offers])
    best = df.loc[df["Total Cost"].idxmin()]

    st.session_state["df"] = df
    st.session_state["best"] = best

if "df" in st.session_state:
    df, best = st.session_state["df"], st.session_state["best"]

    st.subheader("Comparison")
    st.dataframe(
        df.style.apply(
            lambda row: ["background-color: #c8f7c5; color: black"] * len(row)
            if row["Bank"] == best["Bank"] else [""] * len(row),
            axis=1,
        ).format({c: "{:,.2f}" for c in ["Amount", "Fee", "EMI", "Total Interest",
                                         "Total Payment", "Total Cost"]}),
        use_container_width=True, hide_index=True,
    )
    st.success(f"✅ Cheapest: **{best['Bank']}** (total cost {best['Total Cost']:,.2f})")

    st.subheader("Total cost per offer")
    st.bar_chart(df.set_index("Bank")[["Total Interest", "Fee"]])

    # Income check
    if income > 0:
        for _, row in df.iterrows():
            ratio = row["EMI"] / income * 100
            if ratio > 40:
                st.warning(f"⚠️ {row['Bank']}: EMI is {ratio:.0f}% of your income "
                           "(above the ~40% safe limit).")
            else:
                st.info(f"{row['Bank']}: EMI is {ratio:.0f}% of your income.")

    # AI explanation
    st.subheader("🤖 Simple explanation")
    if api_key:
        try:
            with st.spinner("Asking AI..."):
                st.write(explain_with_ai(df, income, api_key))
        except Exception as e:
            st.error(f"AI call failed ({e}). Showing basic summary instead.")
            st.write(fallback_explanation(df, best))
    else:
        st.write(fallback_explanation(df, best))
        st.caption("Add a Gemini API key in the sidebar for a full AI explanation.")

st.caption("Educational tool only, not professional financial advice.")
