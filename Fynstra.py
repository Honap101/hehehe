import streamlit as st
import plotly.graph_objects as go
import base64
from datetime import datetime

# --- Sidebar Logo and Title (PUT THIS FIRST) ---
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


def validated_number_input(label, key, min_value=0.0, step=1.0, help_text=None, **kwargs):
    def update_status():
        st.session_state[f"{key}_status"] = "✅" if st.session_state[key] else "⬜️"

    # Initialize session state status
    if f"{key}_status" not in st.session_state:
        st.session_state[f"{key}_status"] = "⬜️"

    # ✅ + Label + ⓘ tooltip forced inline
    help_html = f"<span style='cursor: help; color: #1f77b4;' title='{help_text}'> ⓘ</span>" if help_text else ""
    st.markdown(
        f"""
            <div style='display:flex; align-items:center; gap:6px; font-size:14px; margin-bottom:2px;'>
                <span>{st.session_state[f'{key}_status']}</span>
                <span>{label}</span>
                {help_html}
            </div>
            """,
            unsafe_allow_html=True
    )

    # Input box below
    value = st.number_input(
        label="",
        min_value=min_value,
        step=step,
        key=key,
        on_change=update_status,
        **kwargs
    )

    # Update check status initially
    update_status()

    return value

def create_component_radar_chart(components):
    """Create radar chart for component breakdown"""
    categories = list(components.keys())
    values = list(components.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Scores',
        line_color='blue'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[70] * len(categories),  # Target scores
        theta=categories,
        fill='toself',
        name='Target (70%)',
        line_color='green',
        opacity=0.3
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        height=400,
    )
    
    return fig

def interpret(label, score):
            if label == "Net Worth":
                return (
                    "Your *net worth is low* relative to your income." if score < 40 else
                    "Your *net worth is progressing*, but still has room to grow." if score < 70 else
                    "You have a *strong net worth* relative to your income."
                ), [
                    "Build your assets by saving and investing consistently.",
                    "Reduce liabilities such as debts and loans.",
                    "Track your net worth regularly to monitor growth."
                ]
            if label == "Debt-to-Income":
                return (
                    "Your *debt is taking a big chunk of your income*." if score < 40 else
                    "You're *managing debt moderately well*, but aim to lower it further." if score < 70 else
                    "Your *debt load is well-managed*."
                ), [
                    "Pay down high-interest debts first.",
                    "Avoid taking on new unnecessary credit obligations.",
                    "Increase income to improve your ratio."
                ]
            if label == "Savings Rate":
                return (
                    "You're *saving very little* monthly." if score < 40 else
                    "Your *savings rate is okay*, but can be improved." if score < 70 else
                    "You're *saving consistently and strongly*."
                ), [
                    "Automate savings transfers if possible.",
                    "Set a target of saving at least 20% of income.",
                    "Review expenses to increase what's saved."
                ]
            if label == "Investment":
                return (
                    "You're *not investing much yet*." if score < 40 else
                    "You're *starting to invest*; try to boost it." if score < 70 else
                    "You're *investing well* and building wealth."
                ), [
                    "Start small and invest regularly.",
                    "Diversify your portfolio for stability.",
                    "Aim for long-term investing over short-term speculation."
                ]
            if label == "Emergency Fund":
                return (
                    "You have *less than 1 month saved* for emergencies." if score < 40 else
                    "You’re *halfway to a full emergency buffer*." if score < 70 else
                    "✅ Your *emergency fund is solid*."
                ), [
                    "Build up to 3–6 months of essential expenses.",
                    "Keep it liquid and easily accessible.",
                    "Set a monthly auto-save amount."
                ]


# Page config
st.set_page_config(page_title="Fynstra – Financial Health Index", layout="centered")


# Title and header
st.markdown(
    """
    <h1 style="
        font-size: 40px;
        background: linear-gradient(to right, #fc3134, #ff5f1f, #ffc542);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    ">
        Your AI-Powered Financial Strategy<br>and Analytics Platform
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("""
<p style='font-size:20px; color:#333; line-height:1.5;'>
Fynstra is your AI-powered financial advisor and simulation tool. Whether you’re new to managing money or already experienced, the platform makes financial planning accessible, insightful, and actionable.
</p>
""", unsafe_allow_html=True)

# Form input container
with st.container(border=True):
    st.markdown("""
<div style="
    display: inline-block;
    background: #ff5f1f;
    color: white;
    padding: 4px 12px;
    border-radius: 6px;
    text-align: center;       /* centers the text */
    font-size: 20px;
    font-weight: 400;
    margin-bottom: 20px;  /* space below */
">
    Calculate your FHI Score
</div>
""", unsafe_allow_html=True)
    
    st.markdown("The Financial Health Index (FHI) Score provides a holistic view of your financial well-being. It helps you understand how secure and prepared you are at the moment, while also highlighting areas for improvement. \n \n"
                "A higher score indicates stronger financial resilience, while a lower score can point to potential vulnerabilities. Integrated into the Fynstra platform, this dynamic score allows you to make informed decisions and set realistic goals to strengthen your financial future.")
    st.markdown("""
<p style="color:#ff5f1f; font-weight:bold; font-size:16px; margin-bottom:10px;">
    Enter the following details:
</p>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        age = validated_number_input("Your Age", key="age", min_value=18, step=1, help="Your current age in years.")
        monthly_expenses = validated_number_input("Monthly Living Expenses (₱)", key="expenses", step=50.0,
                                                help="E.g., rent, food, transportation, utilities.")
        monthly_savings = validated_number_input("Monthly Savings (₱)", key="savings", step=50.0,
                                                help="The amount saved monthly.")
        emergency_fund = validated_number_input("Emergency Fund Amount (₱)", key="emergency", step=500.0,
                                                help="For medical costs, job loss, or other emergencies.")

    with col2:
        monthly_income = validated_number_input("Monthly Gross Income (₱)", key="income", step=100.0,
                                                help="Income before taxes and deductions.")
        monthly_debt = validated_number_input("Monthly Debt Payments (₱)", key="debt", step=50.0,
                                            help="Loans, credit cards, etc.")
        total_investments = validated_number_input("Total Investments (₱)", key="investments", step=500.0,
                                                help="Stocks, bonds, retirement accounts.")
        net_worth = validated_number_input("Net Worth (₱)", key="networth", step=500.0,
                                        help="Total assets minus total liabilities.")

with st.container(border=True):
    st.markdown("""
    <div style="
        display: inline-block;
        background: #ff5f1f;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        text-align: center;       /* centers the text */
        font-size: 20px;
        font-weight: 400;
        margin-bottom: 20px;  /* space below */
    ">
        Describe your Current Life Stage
    </div>
    """, unsafe_allow_html=True)

    life_stages = [
        "Student",
        "Beginning my career",
        "Raising a family",
        "Approaching retirement",
        "Retired",
        "Employee",
        "Other"
    ]
    st.markdown("""
<style>
/* Radio button label text color */
[data-baseweb="radio"] label span {
    color: #ff5f1f;  /* default text */
}

</style>
""", unsafe_allow_html=True)

    selected_stage = st.radio("Select your life stage:", life_stages, index=0, horizontal=False)

    other_stage = ""
    if selected_stage == "Other":
        other_stage = st.text_input("Please specify:", key="other_stage_input")

    st.session_state["life_stage"] = other_stage if selected_stage == "Other" else selected_stage
@st.dialog("⚠️ Missing Information")
def missing_fields_popup(missing_fields):
    st.write(
        f"The following fields are missing or zero: **{', '.join(missing_fields)}.**"
    )
    st.write("Some results may be less accurate. Do you want to proceed?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Proceed Anyway"):
            st.session_state['proceed'] = True
            st.rerun()
    with col2:
        if st.button("Continue Filling In"):
            st.session_state['proceed'] = False
            st.rerun()

# FHI calculation logic
st.markdown("""
<style>
/* Gradient button style */
[data-testid="stButton"] button {
    background: linear-gradient(90deg, #fc3134, #ff5f1f, #ffc542 );
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    transition: all 0.3s ease;
}

/* Hover effect */
[data-testid="stButton"] button:hover {
    filter: brightness(1.1);
}

/* Active / clicked effect */
[data-testid="stButton"] button:active {
    transform: scale(0.98);
}
</style>
""", unsafe_allow_html=True)

if st.button("Check My Financial Health"):
    # Track missing fields
    missing_fields = []
    if monthly_income == 0: missing_fields.append("Monthly Income")
    if monthly_expenses == 0: missing_fields.append("Monthly Expenses")
    if net_worth == 0.00: missing_fields.append("Net Worth")
    if total_investments == 0.00: missing_fields.append("Total Investments")
    if emergency_fund == 0.00: missing_fields.append("Emergency Fund")
    if monthly_savings == 0.00: missing_fields.append("Monthly Savings")
    if monthly_debt == 0.00: missing_fields.append("Monthly Debt Payments")

    if missing_fields:
        missing_fields_popup(missing_fields)   # Show popup
    else:
        st.session_state['proceed'] = True      # All good → calculate


# --- Only run FHI calc if allowed ---
if st.session_state.get('proceed'):
    if monthly_income == 0 or monthly_expenses == 0:
        st.warning("Please input your income and expenses.")
    else:
        # Age-based target multipliers
        if age < 30:
            alpha, beta = 2.5, 2.0
        elif age < 40:
            alpha, beta = 3.0, 3.0
        elif age < 50:
            alpha, beta = 3.5, 4.0
        else:
            alpha, beta = 4.0, 5.0

        annual_income = monthly_income * 12

        # Sub-scores
        Nworth = min(max((net_worth / (annual_income * alpha)) * 100, 0), 100)
        DTI = 100 - min((monthly_debt / monthly_income) * 100, 100)
        Srate = min((monthly_savings / monthly_income) * 100, 100)
        Invest = min(max((total_investments / (beta * annual_income)) * 100, 0), 100)
        Emerg = min((emergency_fund / monthly_expenses) / 6 * 100, 100)

        components = {
            "Net Worth": Nworth,
            "Debt-to-Income": DTI,
            "Savings Rate": Srate,
            "Investment": Invest,
            "Emergency Fund": Emerg,
        }

        # Final FHI Score
        FHI = 0.20 * Nworth + 0.15 * DTI + 0.15 * Srate + 0.15 * Invest + 0.20 * Emerg + 15
        FHI_rounded = round(FHI, 2)
        st.markdown("---")
        # Gauge Chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=FHI_rounded,
            title={"text": "Your FHI Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "salmon"},
                    {'range': [50, 70], 'color': "gold"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ]
            }
        ))

        st.session_state["FHI"] = FHI_rounded
        st.session_state["monthly_income"] = monthly_income
        st.session_state["monthly_expenses"] = monthly_expenses
        st.session_state["current_savings"] = monthly_savings

        fig.update_layout(height=300, margin=dict(t=20, b=20))
        score_col, text_col = st.columns([1, 2])

        with score_col:
            st.plotly_chart(fig, use_container_width=True)

        with text_col:
            st.markdown(f"### Overall FHI Score: *{FHI_rounded}/100*")

            # Identify weak areas
            weak_areas = []
            if Nworth < 60:
                weak_areas.append("net worth")
            if DTI < 60:
                weak_areas.append("debt-to-income ratio")
            if Srate < 60:
                weak_areas.append("savings rate")
            if Invest < 60:
                weak_areas.append("investment levels")
            if Emerg < 60:
                weak_areas.append("emergency fund")

            # Construct weakness text
            weak_text = ""
            if weak_areas:
                if len(weak_areas) == 1:
                    weak_text = f" However, your {weak_areas[0]} needs improvement."
                else:
                    all_but_last = ", ".join(weak_areas[:-1])
                    weak_text = f" However, your {all_but_last} and {weak_areas[-1]} need improvement."

                weak_text += " Addressing this will help strengthen your overall financial health."

            # Final output based on FHI
            if FHI >= 85:
                st.success(f"🎯 Excellent! You’re in great financial shape and well-prepared for the future.{weak_text}")
            elif FHI >= 70:
                st.info(f"🟢 Good! You have a solid foundation. Stay consistent and work on gaps where needed.{weak_text}")
            elif FHI >= 50:
                st.warning(f"🟡 Fair. You’re on your way, but some areas need attention to build a stronger safety net.{weak_text}")
            else:
                st.error(f"🔴 Needs Improvement. Your finances require urgent attention — prioritize stabilizing your income, debt, and savings.{weak_text}")

        # Component radar chart
        st.subheader("📈 FHI Breakdown")
        radar_fig = create_component_radar_chart(components)
        st.plotly_chart(radar_fig, use_container_width=True)

        # Component interpretations

        st.subheader("📊 FHI Interpretation")

        component_descriptions = {
            "Net Worth": "Your assets minus liabilities — shows your financial position. Higher is better.",
            "Debt-to-Income (DTI)": "Proportion of income used to pay debts. Lower is better.",
            "Savings Rate": "How much of your income you save. Higher is better.",
            "Investment Allocation": "Proportion of assets invested for growth. Higher means better long-term potential.",
            "Emergency Fund": "Covers how well you’re protected in financial emergencies. Higher is better."
        }

        col1, col2 = st.columns(2)
        for i, (label, score) in enumerate(components.items()):
            with (col1 if i % 2 == 0 else col2):
                with st.container(border=True):
                    # Use the more descriptive help text
                    help_text = component_descriptions.get(label, "Higher is better.")
                    st.markdown(f"*{label} Score:* {round(score)} / 100", help=help_text)

                    interpretation, suggestions = interpret(label, score)
                    st.markdown(f"<span style='font-size:13px; color:#444;'>{interpretation}</span>", unsafe_allow_html=True)

                    with st.expander("💡 How to improve"):
                        for tip in suggestions:
                            st.write(f"- {tip}")

# Peer comparison
        st.subheader("👥 How You Compare")
            
        # Simulated peer data
        peer_averages = {
            "18-25": {"FHI": 45, "Savings Rate": 15, "Emergency Fund": 35},
            "26-35": {"FHI": 55, "Savings Rate": 18, "Emergency Fund": 55},
            "36-50": {"FHI": 65, "Savings Rate": 22, "Emergency Fund": 70},
            "50+": {"FHI": 75, "Savings Rate": 25, "Emergency Fund": 85}
        }

        age_group = "18-25" if age < 26 else "26-35" if age < 36 else "36-50" if age < 51 else "50+"
        peer_data = peer_averages[age_group]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your FHI", f"{FHI_rounded}", f"{FHI_rounded - peer_data['FHI']:+.0f} vs peers")
        with col2:
            st.metric("Your Savings Rate", f"{components['Savings Rate']:.0f}%", 
                 f"{components['Savings Rate'] - peer_data['Savings Rate']:+.0f}% vs peers")
        with col3:
            st.metric("Your Emergency Fund", f"{components['Emergency Fund']:.0f}%", 
                     f"{components['Emergency Fund'] - peer_data['Emergency Fund']:+.0f}% vs peers")
            
            # Download report
        if st.button("📄 Generate Report"):
            report = generate_text_report(FHI_rounded, components, {
                "age": age,
                "income": monthly_income,
                "expenses": monthly_expenses,
                "savings": monthly_savings
               })
            st.download_button(
                label="Download Financial Health Report",
                data=report,
                file_name=f"fynstra_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
           )
st.markdown("---")

# Container for FYNnyx CTA
# Container for FYNnyx CTA
with st.container():
    st.markdown("### 💬 Want more personalized financial advice?")
    st.markdown(
        "FYNnyx, our AI-powered financial assistant, can give you **tailored recommendations** "
        "based on your inputs. You can visit it via the **tabs on the sidebar** to explore more."
    )

st.markdown("---")
st.markdown("**Fynstra AI** - Empowering Filipinos to **F**orecast, **Y**ield, and **N**avigate their financial future with confidence.")
st.markdown("*Developed by Team HI-4requency for BPI DATA Wave 2025*")