import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from datetime import date

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_base64 = get_base64_image("sidebar_background.png")  # Replace with your image path
logow_base64 = get_base64_image("logo_white.png") 
logoc_base64 = get_base64_image("logo_colored.png")

with st.sidebar:
    st.markdown(
        f"""
        <div style='
            display: flex;
            flex-direction: column;
            justify-content: flex-end;  /* push to bottom */
            align-items: center;
            text-align: center;
            padding: 0;
        '>
            <img src="data:image/png;base64,{logoc_base64}" 
                 width="150" 
                 style="display:block; margin-bottom:10px; filter: drop-shadow(2px 2px 5px white);">
            <h1 style='color:#ffffff; font-size:20px; margin:0;'>Fynstra AI</h1>
            <p style='color:#ffffff; font-size:14px; margin:0 0 20px 0;'>Your AI-Powered Financial Strategy and Analytics Platform</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --- CSS for sidebar background with gradient overlay ---
st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{
        background: linear-gradient(to bottom, rgba(252,49,52,0.7), rgba(255,197,66,0.7)),
                    url("data:image/png;base64,{bg_base64}") no-repeat center;
        background-size: cover;
    }}

    /* Make all sidebar text white */
    [data-testid="stSidebar"] * {{
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Budget Tracker", layout="wide")
st.title("Budget Tracker")

# --- SESSION STATE INIT ---
if "budget_entries" not in st.session_state:
    st.session_state.budget_entries = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# --- BUDGET ENTRY FORM ---
st.subheader("➕ Add New Entry")
with st.form("budget_form"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        entry_date = st.date_input("Date", value=date.today())

    with col2:
        entry_type = st.selectbox("Type", ["Income", "Expense"])

    with col3:
        category_options = ["Food", "Transportation", "Bills", "Shopping", "Entertainment", "Health", "Savings", "Others", "➕ Add new..."]
        selected = st.selectbox("Category", category_options)

        if selected == "➕ Add new...":
            new_category = st.text_input("New Category")
            category = new_category if new_category else "Others"
        else:
            category = selected

    with col4:
        amount = st.number_input("Amount", min_value=0.0, step=1.0)

    submitted = st.form_submit_button("Add Entry")
    if submitted:
        new_entry = {
            "date": entry_date,
            "type": entry_type,
            "category": category,
            "amount": amount
        }

        if st.session_state.edit_index is not None:
            st.session_state.budget_entries[st.session_state.edit_index] = new_entry
            st.session_state.edit_index = None
            st.success("✅ Entry updated!")
        else:
            st.session_state.budget_entries.append(new_entry)
            st.success("✅ Entry added!")

# --- IF THERE ARE ENTRIES ---
if st.session_state.budget_entries:
    df = pd.DataFrame(st.session_state.budget_entries)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)

    st.subheader("📊 Budget Summary")
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    net_savings = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₱{total_income:,.2f}")
    col2.metric("Total Expenses", f"₱{total_expense:,.2f}")
    col3.metric("Net Savings", f"₱{net_savings:,.2f}")

    st.subheader("📈 Visual Breakdown")
    col4, col5 = st.columns(2)

    with col4:
        expense_df = df[df["type"] == "Expense"]
        if not expense_df.empty:
            pie = px.pie(expense_df, values="amount", names="category", title="Expenses by Category")
            st.plotly_chart(pie, use_container_width=True)
        else:
            st.info("No expenses to show.")

    with col5:
        df_by_date = df.groupby(["date", "type"])["amount"].sum().reset_index()
        bar = px.bar(df_by_date, x="date", y="amount", color="type", barmode="group", title="Daily Income vs Expenses")
        st.plotly_chart(bar, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧾 Transactions")
        for i, entry in df.iterrows():
            with st.expander(f"{entry['date'].strftime('%Y-%m-%d')} | {entry['type']} | {entry['category']} | ₱{entry['amount']:,.2f}"):
                colA, colB = st.columns(2)
                if colA.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    # preload values
                    st.experimental_rerun()
                if colB.button("❌ Delete", key=f"delete_{i}"):
                    st.session_state.budget_entries.pop(i)
                    st.experimental_rerun()

    with col2:
        st.subheader("📂 Expense Breakdown")
        if not expense_df.empty:
            breakdown = expense_df.groupby("category")["amount"].sum().reset_index()
            st.dataframe(breakdown)
        else:
            st.info("No expenses recorded yet.")

else:
    st.info("No entries yet. Add your income or expenses above.")

# --- FUTURE BANK INTEGRATION ---
st.markdown("---")
st.subheader("🏦 Bank Integration (Coming Soon)")
st.markdown("""
Sync your budget tracker directly with BPI’s online system.

✅ Auto-track your transactions  
✅ Real-time budget suggestions  
✅ Safer, smarter saving
🔒 This feature is part of our future roadmap to integrate with banks for automated budget tracking and financial health analysis.
.
""")
