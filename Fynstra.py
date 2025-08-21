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

# Add function to load user data
def load_user_financial_data():
    """Load user's financial data if they are signed in"""
    try:
        # Import here to avoid issues if auth modules aren't available
        from supabase import create_client
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Check if user is authenticated
        user_id = st.session_state.get("user_id")
        if not user_id:
            return False
            
        # Initialize Google Sheets client
        try:
            sa_info = dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(st.secrets["SHEET_ID"])
            ws = sh.worksheet("Users")
        except Exception as e:
            st.error(f"Failed to connect to database: {e}")
            return False
            
        # Get user data from Google Sheets
        try:
            values = ws.get_all_values()
            if not values:
                return False
                
            header = values[0]
            rows = values[1:] if len(values) > 1 else []
            
            # Find user row
            if "user_id" not in header:
                return False
                
            uid_idx = header.index("user_id")
            user_row = None
            
            for row in rows:
                if len(row) > uid_idx and row[uid_idx] == user_id:
                    user_row = row
                    break
                    
            if not user_row:
                return False
                
            # Map data to session state with exact key matching
            field_mapping = {
                "age": "age",
                "monthly_income": "monthly_income", 
                "monthly_expenses": "monthly_expenses",
                "monthly_savings": "monthly_savings",
                "monthly_debt": "monthly_debt",
                "total_investments": "total_investments",
                "net_worth": "net_worth",
                "emergency_fund": "emergency_fund",
                "last_FHI": "FHI"
            }
            
            loaded_fields = []
            for sheet_col, session_key in field_mapping.items():
                if sheet_col in header:
                    col_idx = header.index(sheet_col)
                    if len(user_row) > col_idx and user_row[col_idx] and user_row[col_idx] != "0" and user_row[col_idx] != "":
                        try:
                            # Convert to float first, then int for age if needed
                            value = float(user_row[col_idx])
                            if value >= 0:  # Load even if 0 for financial fields
                                if session_key == "age":
                                    # For age, convert to int but store as float to avoid type conflicts
                                    st.session_state[session_key] = float(int(value))
                                else:
                                    st.session_state[session_key] = value
                                loaded_fields.append(f"{sheet_col}: {value}")
                        except (ValueError, TypeError):
                            # Keep default if conversion fails
                            pass
            
            # Debug information (remove in production)
            if loaded_fields:
                st.success(f"✅ Loaded data: {', '.join(loaded_fields[:3])}{'...' if len(loaded_fields) > 3 else ''}")
                            
            return len(loaded_fields) > 0
            
        except Exception as e:
            st.error(f"Error loading user data: {e}")
            return False
            
    except ImportError:
        # Auth modules not available
        return False
    except Exception as e:
        # Other errors
        st.error(f"Unexpected error: {e}")
        return False

def save_user_financial_data():
    """Save user's financial data to the database"""
    try:
        from supabase import create_client
        import gspread
        from google.oauth2.service_account import Credentials
        import time
        import random
        
        user_id = st.session_state.get("user_id")
        if not user_id:
            return False
            
        # Prepare data to save with current input values
        data_to_save = {
            "age": st.session_state.get("age", 0),
            "monthly_income": st.session_state.get("monthly_income", 0),
            "monthly_expenses": st.session_state.get("monthly_expenses", 0), 
            "monthly_savings": st.session_state.get("monthly_savings", 0),
            "monthly_debt": st.session_state.get("monthly_debt", 0),
            "total_investments": st.session_state.get("total_investments", 0),
            "net_worth": st.session_state.get("net_worth", 0),
            "emergency_fund": st.session_state.get("emergency_fund", 0),
            "last_FHI": st.session_state.get("FHI", 0)
        }
        
        # Only save if we have some meaningful data
        has_meaningful_data = any(data_to_save[key] > 0 for key in data_to_save.keys() if key != "last_FHI")
        if not has_meaningful_data:
            return False
        
        # Initialize Google Sheets
        try:
            sa_info = dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(st.secrets["SHEET_ID"])
            ws = sh.worksheet("Users")
        except Exception as e:
            st.error(f"Failed to connect to database for saving: {e}")
            return False
            
        # Update user row with financial data
        try:
            values = ws.get_all_values()
            if not values:
                return False
                
            header = values[0]
            rows = values[1:] if len(values) > 1 else []
            
            # Find user row
            if "user_id" not in header:
                return False
                
            uid_idx = header.index("user_id")
            user_row_idx = None
            
            for i, row in enumerate(rows, start=2):  # Start at 2 because of header
                if len(row) > uid_idx and row[uid_idx] == user_id:
                    user_row_idx = i
                    break
                    
            if not user_row_idx:
                return False
                
            # Update each field with retry logic
            def with_backoff(fn, tries: int = 3):
                for i in range(tries):
                    try:
                        return fn()
                    except Exception as e:
                        if i == tries - 1:
                            raise
                        time.sleep((2 ** i) + random.random())
                        
            updated_fields = []
            for field, value in data_to_save.items():
                if field in header:
                    col_idx = header.index(field) + 1  # +1 for 1-based indexing
                    try:
                        with_backoff(lambda f=field, v=value, c=col_idx, r=user_row_idx: 
                                   ws.update_cell(r, c, str(v)))
                        updated_fields.append(f"{field}: {value}")
                    except Exception as e:
                        st.error(f"Failed to update {field}: {e}")
                        
            # Show what was saved (for debugging - remove in production)
            if updated_fields:
                st.info(f"Saved: {', '.join(updated_fields[:3])}{'...' if len(updated_fields) > 3 else ''}")
                    
            return len(updated_fields) > 0
            
        except Exception as e:
            st.error(f"Error saving data: {e}")
            return False
            
    except ImportError:
        st.warning("Database connection not available")
        return False
    except Exception as e:
        st.error(f"Unexpected error while saving: {e}")
        return False

def validated_number_input(label, key, min_value=0.0, step=1.0, help_text=None, **kwargs):
    def update_status():
        st.session_state[f"{key}_status"] = "✅" if st.session_state.get(key, 0) > 0 else "⬜️"

    # Initialize session state status
    if f"{key}_status" not in st.session_state:
        st.session_state[f"{key}_status"] = "⬜️"

    # Get default value from session state if available, otherwise use min_value
    # Remove any 'value' from kwargs to avoid conflicts
    kwargs_clean = {k: v for k, v in kwargs.items() if k != "value"}
    
    if key in st.session_state and st.session_state[key] is not None:
        default_value = float(st.session_state[key])
    else:
        default_value = float(min_value)

    # ✅ + Label + ❓ tooltip forced inline
    help_html = f"<span style='cursor: help; color: #1f77b4;' title='{help_text}'> ❓</span>" if help_text else ""
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

    # Input box below with default value - ensure all numeric types are consistent
    value = st.number_input(
        label="",
        min_value=float(min_value),
        step=float(step),
        key=key,
        on_change=update_status,
        value=default_value,
        **kwargs_clean
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
                    "You're *halfway to a full emergency buffer*." if score < 70 else
                    "✅ Your *emergency fund is solid*."
                ), [
                    "Build up to 3–6 months of essential expenses.",
                    "Keep it liquid and easily accessible.",
                    "Set a monthly auto-save amount."
                ]

def generate_text_report(fhi_score, components, user_data):
    """Generate a text report for download"""
    report = f"""
FYNSTRA FINANCIAL HEALTH REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

===========================================
OVERALL FINANCIAL HEALTH INDEX (FHI): {fhi_score}/100
===========================================

USER PROFILE:
Age: {user_data['age']} years
Monthly Income: ₱{user_data['income']:,.2f}
Monthly Expenses: ₱{user_data['expenses']:,.2f}
Monthly Savings: ₱{user_data['savings']:,.2f}

COMPONENT BREAKDOWN:
"""
    
    for component, score in components.items():
        report += f"\n{component}: {score:.1f}/100"
        
    report += f"""

RECOMMENDATIONS:
- Focus on improving components scoring below 60
- Maintain consistency in savings and investments
- Review and adjust your financial strategy regularly

This report was generated by Fynstra AI - Your Financial Strategy Platform
"""
    
    return report


# Page config
st.set_page_config(page_title="Fynstra – Financial Health Index", layout="centered")

# Load user data if signed in - moved to happen BEFORE any input rendering
user_signed_in = st.session_state.get("user_id") is not None
if user_signed_in:
    # Force reload data every time to ensure we have latest
    if "force_reload" not in st.session_state:
        st.session_state["force_reload"] = True
        
    if st.session_state.get("force_reload", False):
        if load_user_financial_data():
            st.session_state["force_reload"] = False
            # Clear any existing status flags to ensure fresh load
            for key in list(st.session_state.keys()):
                if key.endswith("_status"):
                    del st.session_state[key]

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
Fynstra is your AI-powered financial advisor and simulation tool. Whether you're new to managing money or already experienced, the platform makes financial planning accessible, insightful, and actionable.
</p>
""", unsafe_allow_html=True)

# Show user status
if user_signed_in:
    user_email = st.session_state.get("email", "")
    display_name = st.session_state.get("display_name", "User")
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**👤 Signed in as:** {display_name} ({user_email})")
            if st.session_state.get("FHI"):
                st.markdown(f"**📊 Last FHI Score:** {st.session_state['FHI']}/100")
            
            # Show data status
            has_saved_data = any(st.session_state.get(key, 0) > 0 for key in 
                               ["age", "monthly_income", "monthly_expenses", "monthly_savings"])
            if has_saved_data:
                st.markdown("**💾 Status:** Data ready to save when you calculate FHI")
            
        with col2:
            if st.button("📥 Load My Data", help="Reload your saved financial data"):
                st.session_state["force_reload"] = True
                st.rerun()
        with col3:
            if st.button("🔄 Reset Form", help="Clear all inputs and start fresh"):
                # Clear all financial input keys and status keys
                keys_to_clear = [
                    "age", "monthly_income", "monthly_expenses", "monthly_savings", 
                    "monthly_debt", "total_investments", "net_worth", "emergency_fund", 
                    "FHI", "life_stage", "other_stage_input", "proceed", "force_reload"
                ]
                
                # Also clear status keys
                status_keys = [f"{key}_status" for key in keys_to_clear]
                
                for key in keys_to_clear + status_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                        
                # Set force reload flag for next visit
                st.session_state["force_reload"] = True
                st.success("🔄 Form reset! Data will reload on next visit.")
                st.rerun()
else:
    with st.container(border=True):
        st.info("💡 **Sign in** to save your financial data and access personalized features! Visit the **User Account** page to create an account or sign in.")

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
        age = validated_number_input("Your Age", key="age", min_value=18.0, step=1.0, help_text="Your current age in years.")
        monthly_expenses = validated_number_input("Monthly Living Expenses (₱)", key="monthly_expenses", step=50.0,
                                                help_text="E.g., rent, food, transportation, utilities.")
        monthly_savings = validated_number_input("Monthly Savings (₱)", key="monthly_savings", step=50.0,
                                                help_text="The amount saved monthly.")
        emergency_fund = validated_number_input("Emergency Fund Amount (₱)", key="emergency_fund", step=500.0,
                                                help_text="For medical costs, job loss, or other emergencies.")

    with col2:
        monthly_income = validated_number_input("Monthly Gross Income (₱)", key="monthly_income", step=100.0,
                                                help_text="Income before taxes and deductions.")
        monthly_debt = validated_number_input("Monthly Debt Payments (₱)", key="monthly_debt", step=50.0,
                                            help_text="Loans, credit cards, etc.")
        total_investments = validated_number_input("Total Investments (₱)", key="total_investments", step=500.0,
                                                help_text="Stocks, bonds, retirement accounts.")
        net_worth = validated_number_input("Net Worth (₱)", key="net_worth", step=500.0,
                                        help_text="Total assets minus total liabilities.")

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

    # Get default life stage from session state
    default_stage_index = 0
    if "life_stage" in st.session_state and st.session_state["life_stage"] in life_stages:
        default_stage_index = life_stages.index(st.session_state["life_stage"])

    selected_stage = st.radio("Select your life stage:", life_stages, index=default_stage_index, horizontal=False)

    other_stage = ""
    if selected_stage == "Other":
        other_stage = st.text_input("Please specify:", key="other_stage_input", 
                                   value=st.session_state.get("life_stage", "") if st.session_state.get("life_stage") not in life_stages else "")

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

        # Update session state
        st.session_state["FHI"] = FHI_rounded
        st.session_state["current_savings"] = monthly_savings

        # Save to database immediately after calculation if user is signed in
        if user_signed_in:
            try:
                if save_user_financial_data():
                    st.success("💾 Your financial data has been saved successfully!")
                else:
                    st.warning("⚠️ Could not save your data, but calculation is complete.")
            except Exception as e:
                st.warning(f"⚠️ Save failed: {str(e)}, but calculation is complete.")

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
                st.success(f"🎯 Excellent! You're in great financial shape and well-prepared for the future.{weak_text}")
            elif FHI >= 70:
                st.info(f"🟢 Good! You have a solid foundation. Stay consistent and work on gaps where needed.{weak_text}")
            elif FHI >= 50:
                st.warning(f"🟡 Fair. You're on your way, but some areas need attention to build a stronger safety net.{weak_text}")
            else:
                st.error(f"🔴 Needs Improvement. Your finances require urgent attention – prioritize stabilizing your income, debt, and savings.{weak_text}")

        # Component radar chart
        st.subheader("📈 FHI Breakdown")
        radar_fig = create_component_radar_chart(components)
        st.plotly_chart(radar_fig, use_container_width=True)

        # Component interpretations
        st.subheader("📊 FHI Interpretation")

        component_descriptions = {
            "Net Worth": "Your assets minus liabilities – shows your financial position. Higher is better.",
            "Debt-to-Income (DTI)": "Proportion of income used to pay debts. Lower is better.",
            "Savings Rate": "How much of your income you save. Higher is better.",
            "Investment Allocation": "Proportion of assets invested for growth. Higher means better long-term potential.",
            "Emergency Fund": "Covers how well you're protected in financial emergencies. Higher is better."
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

# Container for FYNyx CTA
with st.container():
    st.markdown("### 💬 Want more personalized financial advice?")
    st.markdown(
        "FYNyx, our AI-powered financial assistant, can give you **tailored recommendations** "
        "based on your inputs. You can visit it via the **tabs on the sidebar** to explore more."
    )

st.markdown("---")
st.markdown("**Fynstra AI** - Empowering Filipinos to **F**orecast, **Y**ield, and **N**avigate their financial future with confidence.")
st.markdown("*Developed by Team HI-4requency for BPI DATA Wave 2025*")
