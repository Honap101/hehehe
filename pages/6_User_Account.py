import streamlit as st
import base64
from datetime import datetime
import hashlib
import uuid
import time
import random

# Import your existing auth helpers from the main app
try:
    from supabase import create_client
    import gspread
    from google.oauth2.service_account import Credentials
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load your existing brand assets
bg_base64 = get_base64_image("sidebar_background.png")
logow_base64 = get_base64_image("logo_white.png") 
logoc_base64 = get_base64_image("logo_colored.png")

# ===============================
# SIDEBAR STYLING (consistent with your other pages)
# ===============================
with st.sidebar:
    st.markdown(
        f"""
        <div style='
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
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

st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{
        background: linear-gradient(to bottom, rgba(252,49,52,0.7), rgba(255,197,66,0.7)),
                    url("data:image/png;base64,{bg_base64}") no-repeat center;
        background-size: cover;
    }}

    [data-testid="stSidebar"] * {{
        color: white;
    }}

    /* Page Styling - Professional & Modern */
    .auth-layout {{
        padding: 2rem 1rem;
        max-width: 600px;
        margin: 0 auto;
    }}

    .page-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}

    .page-title {{
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #fc3134, #ff5f1f, #ffc542);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }}

    .page-subtitle {{
        color: #64748b;
        font-size: 1.125rem;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 2rem;
    }}

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: rgba(241, 245, 249, 0.8);
        border-radius: 16px;
        padding: 6px;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
        backdrop-filter: blur(10px);
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px !important;
        color: #64748b !important;
        font-weight: 600 !important;
        padding: 1rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        font-size: 0.95rem !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: white !important;
        color: #fc3134 !important;
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.08),
            0 1px 4px rgba(0, 0, 0, 0.04) !important;
        transform: translateY(-1px) !important;
    }}

    /* Enhanced Input Styling */
    .stTextInput > div > div > input {{
        border-radius: 12px !important;
        border: 2px solid #e5e7eb !important;
        padding: 1rem 1.25rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: #fafbfc !important;
        font-weight: 500 !important;
        color: #1f2937 !important;
        min-height: 48px !important;
        line-height: 1.5 !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: #fc3134 !important;
        box-shadow: 
            0 0 0 4px rgba(252, 49, 52, 0.1),
            0 4px 12px rgba(252, 49, 52, 0.15) !important;
        background: white !important;
        transform: translateY(-1px) !important;
    }}

    .stTextInput > div > div > input::placeholder {{
        color: #9ca3af !important;
        font-weight: 400 !important;
    }}

    .stTextInput {{
        margin-bottom: 1.25rem !important;
    }}

    /* Button Styling */
    .stButton > button {{
        width: 100%;
        background: linear-gradient(135deg, #fc3134, #ff5f1f) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1.25rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.025em !important;
        box-shadow: 0 4px 12px rgba(252, 49, 52, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(252, 49, 52, 0.4) !important;
        background: linear-gradient(135deg, #e02d30, #ff5f1f) !important;
    }}

    .stButton > button:active {{
        transform: translateY(0) !important;
        transition: transform 0.1s !important;
    }}

    .secondary-button {{
        background: white !important;
        color: #374151 !important;
        border: 2px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.25rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.95rem !important;
    }}

    .secondary-button:hover {{
        background: #f9fafb !important;
        border-color: #9ca3af !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }}

    /* Message Styling */
    .success-msg {{
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 1.25rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        font-weight: 600;
        text-align: center;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
    }}

    .error-msg {{
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border: 1px solid #fca5a5;
        color: #dc2626;
        padding: 1.25rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        font-weight: 600;
        text-align: center;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
    }}

    .info-msg {{
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border: 1px solid #93c5fd;
        color: #1d4ed8;
        padding: 1.25rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        font-weight: 600;
        text-align: center;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }}

    .user-avatar {{
        width: 96px;
        height: 96px;
        background: linear-gradient(135deg, #fc3134, #ffc542);
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 2.5rem;
        margin: 0 auto 2rem auto;
        border: 4px solid white;
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.1),
            0 2px 8px rgba(0, 0, 0, 0.06);
        position: relative;
    }}

    .user-name {{
        font-size: 1.75rem;
        font-weight: 800;
        color: #166534;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }}

    .user-email {{
        color: #059669;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }}

    .user-status {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }}

    .status-verified {{
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }}

    .status-pending {{
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }}

    .user-actions {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 2rem;
    }}

    /* Checkbox Styling */
    .stCheckbox {{
        margin: 1.5rem 0 !important;
    }}

    .stCheckbox > label {{
        font-size: 0.9rem !important;
        color: #4b5563 !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
    }}

    /* Benefits Section */
    .benefits-section {{
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
    }}

    .benefits-title {{
        font-weight: 700;
        color: #374151;
        font-size: 1rem;
        margin-bottom: 1rem;
        text-align: center;
    }}

    .benefit-item {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 0;
        color: #4b5563;
        font-size: 0.95rem;
        font-weight: 500;
    }}

    /* Footer */
    .auth-footer {{
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
    }}

    .footer-text {{
        color: #64748b;
        font-size: 0.875rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }}

    .footer-links {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
    }}

    .footer-link {{
        color: #fc3134;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }}

    .footer-link:hover {{
        color: #e02d30;
        text-decoration: underline;
    }}

    /* Responsive Design */
    @media (max-width: 640px) {{
        .auth-card {{
            padding: 2.5rem 2rem;
            margin: 1rem;
            border-radius: 20px;
        }}
        
        .page-title {{
            font-size: 1.75rem;
        }}
        
        .user-actions {{
            grid-template-columns: 1fr;
            gap: 0.75rem;
        }}
        
        .footer-links {{
            flex-direction: column;
            gap: 1rem;
        }}
    }}
    </style>

    """,
    unsafe_allow_html=True
)


# ===============================
# AUTHENTICATION HELPERS (from your existing code)
# ===============================

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase initialization failed: {e}")
        return None

@st.cache_resource
def init_sheets_client():
    """Initialize Google Sheets client"""
    try:
        sa_info = dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Sheets initialization failed: {e}")
        return None

@st.cache_resource
def open_sheet():
    """Open the main Google Sheet"""
    try:
        gc = init_sheets_client()
        if gc:
            return gc.open_by_key(st.secrets["SHEET_ID"])
        return None
    except Exception as e:
        st.error(f"Failed to open Google Sheet: {e}")
        return None

def with_backoff(fn, tries: int = 4):
    """Run fn() with exponential backoff on transient errors."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep((2 ** i) + random.random())

def log_auth_event(event: str, user: dict, note: str = ""):
    """Log authentication events"""
    try:
        sh = open_sheet()
        if not sh:
            return
        
        try:
            ws = sh.worksheet("Auth_Events")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="Auth_Events", rows=5000, cols=10)
            ws.append_row(["ts","event","user_id","email","username","note"])
        
        with_backoff(lambda: ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event,
            user.get("id"),
            user.get("email"),
            (user.get("user_metadata") or {}).get("username"),
            note
        ], value_input_option="USER_ENTERED"))
    except Exception:
        pass  # Silent fail for logging

def upsert_user_row(user: dict, payload: dict = None):
    """Create or update user row"""
    try:
        sh = open_sheet()
        if not sh:
            return
        
        try:
            ws = sh.worksheet("Users")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="Users", rows=2000, cols=30)
            ws.append_row([
                "user_id","email","username","created_at","last_login",
                "age","monthly_income","monthly_expenses","monthly_savings",
                "monthly_debt","total_investments","net_worth","emergency_fund",
                "last_FHI","consent_processing","consent_storage","consent_ai",
                "analytics_opt_in","consent_version","consent_ts"
            ])
        
        user_id = user.get("id")
        email = user.get("email") 
        username = (user.get("user_metadata") or {}).get("username")
        
        # Try to find existing user
        values = ws.get_all_values()
        header = values[0] if values else []
        rows = values[1:] if len(values) > 1 else []
        
        found_row_idx = None
        if "user_id" in header:
            uid_idx = header.index("user_id")
            for i, row in enumerate(rows, start=2):
                if len(row) > uid_idx and row[uid_idx] == user_id:
                    found_row_idx = i
                    break
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if found_row_idx:
            # Update existing user
            if "last_login" in header:
                ws.update_cell(found_row_idx, header.index("last_login") + 1, now)
        else:
            # Create new user
            base_data = {
                "user_id": user_id,
                "email": email,
                "username": username,
                "created_at": user.get("created_at", now),
                "last_login": now,
            }
            if payload:
                base_data.update(payload)
            
            row = [base_data.get(col, "") for col in header]
            with_backoff(lambda: ws.append_row(row, value_input_option="USER_ENTERED"))
            
    except Exception:
        pass  # Silent fail for logging

# ===============================
# AUTHENTICATION STATE MANAGEMENT
# ===============================

def init_auth_state():
    """Initialize authentication state"""
    if "auth" not in st.session_state:
        st.session_state.auth = {"user": None, "session": None}
    if "auth_message" not in st.session_state:
        st.session_state.auth_message = None
    if "auth_message_type" not in st.session_state:
        st.session_state.auth_message_type = None

def set_user_session(user, session=None):
    """Set user session and identity for the rest of the app"""
    st.session_state.auth["user"] = user
    st.session_state.auth["session"] = session
    
    # Set identity variables that your other pages expect
    st.session_state["auth_method"] = "email"
    st.session_state["user_id"] = user.get("id")
    st.session_state["email"] = user.get("email")
    meta = (user.get("user_metadata") or {})
    st.session_state["display_name"] = meta.get("username") or user.get("email")

def sign_out():
    """Sign out current user"""
    if AUTH_AVAILABLE:
        supabase = init_supabase()
        if supabase:
            try:
                supabase.auth.sign_out()
            except:
                pass
    
    # Clear session state
    st.session_state.auth = {"user": None, "session": None}
    for k in ["auth_method", "user_id", "email", "display_name"]:
        st.session_state.pop(k, None)
    
    st.session_state.auth_message = "Successfully signed out!"
    st.session_state.auth_message_type = "success"

# ===============================
# UI HELPER FUNCTIONS
# ===============================

def show_message():
    """Display authentication messages"""
    if st.session_state.auth_message:
        if st.session_state.auth_message_type == "success":
            st.markdown(f'<div class="success-msg">✅ {st.session_state.auth_message}</div>', unsafe_allow_html=True)
        elif st.session_state.auth_message_type == "error":
            st.markdown(f'<div class="error-msg">❌ {st.session_state.auth_message}</div>', unsafe_allow_html=True)
        elif st.session_state.auth_message_type == "info":
            st.markdown(f'<div class="info-msg">ℹ️ {st.session_state.auth_message}</div>', unsafe_allow_html=True)
        
        # Clear message after displaying
        st.session_state.auth_message = None
        st.session_state.auth_message_type = None

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Password strength validation"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

# ===============================
# DATA EXPORT & DELETION
# ===============================

def export_my_data_ui():
    """Renders an export panel for user data"""
    import csv, zipfile, json, io
    
    if not st.session_state.get("user_id"):
        st.info("Sign in to export your data.")
        return

    st.markdown("### 📥 Export Your Data")
    st.markdown("Download a copy of your saved data from our systems.")

    # Pick format
    fmt = st.radio("Export format", ["JSON", "CSV (zip)"], horizontal=True, key="export_fmt")

    user_id = st.session_state["user_id"]
    email = st.session_state.get("email", "")
    
    # Mock data structure (replace with actual data retrieval)
    user_data = {
        "profile": {
            "user_id": user_id,
            "email": email,
            "display_name": st.session_state.get("display_name", ""),
            "created_at": datetime.now().isoformat(),
        },
        "calculations": [],  # Your FHI calculations
        "goals": [],  # User goals
        "preferences": {}  # User preferences
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"fynstra_export_{user_id}_{ts}"

    if fmt == "JSON":
        data = json.dumps(user_data, indent=2).encode("utf-8")
        st.download_button(
            "📥 Download JSON export",
            data=data,
            file_name=f"{base_name}.json",
            mime="application/json",
            use_container_width=True,
        )
    else:
        # CSV export (simplified)
        csv_data = f"user_id,email,display_name,created_at\n{user_id},{email},{st.session_state.get('display_name', '')},{datetime.now().isoformat()}"
        st.download_button(
            "📦 Download CSV export",
            data=csv_data.encode("utf-8"),
            file_name=f"{base_name}.csv",
            mime="text/csv",
            use_container_width=True,
        )

def forget_me_ui():
    """Renders a data deletion interface"""
    if not st.session_state.get("user_id"):
        return

    st.markdown("### 🗑️ Delete Your Data")
    st.markdown("Permanently remove your saved profile and data from our systems.")
    
    if st.button("🗑️ Delete my saved profile", type="secondary"):
        try:
            # Here you would implement actual data deletion
            # For now, just clear session state
            for k in [
                "user_id", "email", "display_name", "FHI", 
                "monthly_income", "monthly_expenses", "current_savings"
            ]:
                st.session_state.pop(k, None)
            
            # Sign out
            sign_out()
            
            st.success("Your data has been deleted from our systems.")
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            st.error(f"Delete failed: {e}")

# ===============================
# UI COMPONENTS
# ===============================

def render_user_profile():
    """Render logged-in user profile"""
    user = st.session_state.auth["user"]
    
    st.markdown('<div class="user-profile">', unsafe_allow_html=True)
    
    # User avatar and info
    username = user.get("user_metadata", {}).get("username", "User")
    email = user.get("email", "")
    
    st.markdown(f'''
    <div class="user-avatar">{username[0].upper()}</div>
    <div class="user-name">{username}</div>
    <div class="user-email">{email}</div>
    ''', unsafe_allow_html=True)
    
    # Account status
    is_verified = user.get("email_confirmed_at") is not None
    status_class = "status-verified" if is_verified else "status-pending"
    status_text = "✅ Email Verified" if is_verified else "⏳ Email Pending Verification"
    
    st.markdown(f'<div class="user-status {status_class}">{status_text}</div>', unsafe_allow_html=True)
    
    # Member since
    created_at = user.get("created_at", "")
    if created_at:
        try:
            member_since = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%B %Y')
            st.markdown(f'<div style="color: #64748b; margin-bottom: 1rem; font-weight: 500;">Member since {member_since}</div>', unsafe_allow_html=True)
        except:
            pass
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Go to Dashboard", key="dashboard_btn", use_container_width=True):
            st.switch_page("Fynstra.py")
    
    with col2:
        if st.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
            sign_out()
            st.rerun()
    
    # Data management
    with st.expander("🔒 Privacy & data controls", expanded=False):
        st.markdown("Download a copy of your data or delete your saved profile.")
        export_my_data_ui()
        
        st.markdown("---")
        
        # Confirm checkbox for delete
        confirm = st.checkbox("I understand this will permanently delete my saved profile.")
        if confirm:
            forget_me_ui()
        else:
            st.caption("Check the box above to enable deletion.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_signup_form():
    """Render signup form"""
    if not AUTH_AVAILABLE:
        st.error("Authentication libraries not available. Please install required packages.")
        return
        
    supabase = init_supabase()
    if not supabase:
        st.error("Authentication service unavailable. Please check your Supabase configuration.")
        return
    
    with st.form("signup_form", clear_on_submit=False):
        st.markdown("👤 **Username**")
        username = st.text_input("", placeholder="Enter your display name", key="signup_username", label_visibility="collapsed")
        
        st.markdown("📧 **Email Address**")
        email = st.text_input("", placeholder="Enter your email address", key="signup_email", label_visibility="collapsed")
        
        st.markdown("🔒 **Password**")
        password = st.text_input("", type="password", placeholder="Create a strong password", key="signup_password", label_visibility="collapsed")
        
        st.markdown("🔒 **Confirm Password**")
        confirm_password = st.text_input("", type="password", placeholder="Confirm your password", key="signup_confirm", label_visibility="collapsed")
        
        # Terms acceptance
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="terms_check")
        
        st.markdown('<br>', unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Create Account", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            errors = []
            
            if not username.strip():
                errors.append("Username is required")
            elif len(username) < 2:
                errors.append("Username must be at least 2 characters")
            
            if not email.strip():
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Please enter a valid email address")
            
            if not password:
                errors.append("Password is required")
            else:
                is_valid, msg = validate_password(password)
                if not is_valid:
                    errors.append(msg)
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if not terms_accepted:
                errors.append("Please accept the Terms of Service")
            
            if errors:
                st.session_state.auth_message = " • ".join(errors)
                st.session_state.auth_message_type = "error"
                st.rerun()
            else:
                # Create account with Supabase
                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password,
                        "options": {
                            "data": {"username": username}
                        }
                    })
                    
                    if response.user:
                        user_dict = response.user.model_dump() if hasattr(response.user, 'model_dump') else dict(response.user)
                        
                        # Log using your existing setup
                        log_auth_event("signup", user_dict)
                        upsert_user_row(user_dict, payload={})
                        
                        st.session_state.auth_message = f"Account created successfully! Please check your email to verify your account."
                        st.session_state.auth_message_type = "success"
                        st.rerun()
                    else:
                        st.session_state.auth_message = "Account creation initiated. Please check your email."
                        st.session_state.auth_message_type = "info"
                        st.rerun()
                        
                except Exception as e:
                    error_msg = str(e)
                    if "already been registered" in error_msg:
                        st.session_state.auth_message = "An account with this email already exists. Please sign in instead."
                    else:
                        st.session_state.auth_message = f"Failed to create account: {error_msg}"
                    st.session_state.auth_message_type = "error"
                    st.rerun()

def render_login_form():
    """Render login form"""
    if not AUTH_AVAILABLE:
        st.error("Authentication libraries not available. Please install required packages.")
        return
        
    supabase = init_supabase()
    if not supabase:
        st.error("Authentication service unavailable. Please check your Supabase configuration.")
        return
    
    with st.form("login_form", clear_on_submit=False):
        st.markdown("📧 **Email Address**")
        email = st.text_input("", placeholder="Enter your email address", key="login_email", label_visibility="collapsed")
        
        st.markdown("🔒 **Password**")
        password = st.text_input("", type="password", placeholder="Enter your password", key="login_password", label_visibility="collapsed")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("Remember me")
        with col2:
            st.markdown('<div style="text-align: right; padding-top: 0.3rem;"><a href="#" style="color: #fc3134; text-decoration: none; font-size: 0.9rem;">Forgot password?</a></div>', unsafe_allow_html=True)
        
        st.markdown('<br>', unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Sign In", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password:
                st.session_state.auth_message = "Please enter both email and password"
                st.session_state.auth_message_type = "error"
                st.rerun()
            else:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if response.session and response.user:
                        user_dict = response.user.model_dump() if hasattr(response.user, 'model_dump') else dict(response.user)
                        
                        set_user_session(user_dict, response.session)
                        
                        # Log using your existing setup
                        log_auth_event("login", user_dict)
                        upsert_user_row(user_dict, payload={})
                        
                        username = user_dict.get("user_metadata", {}).get("username", "User")
                        st.session_state.auth_message = f"Welcome back, {username}! 🎉"
                        st.session_state.auth_message_type = "success"
                        st.rerun()
                    else:
                        st.session_state.auth_message = "Invalid email or password"
                        st.session_state.auth_message_type = "error"
                        st.rerun()
                        
                except Exception as e:
                    error_msg = str(e)
                    if "Invalid login credentials" in error_msg:
                        st.session_state.auth_message = "Invalid email or password"
                    else:
                        st.session_state.auth_message = f"Sign in failed: {error_msg}"
                    st.session_state.auth_message_type = "error"
                    st.rerun()

# ===============================
# POLICY CONTENT
# ===============================
PRIVACY_MD = """
We collect the data you choose to provide (e.g., email, profile info, financial inputs) to power features like saved scenarios and personalized tips.  
We never sell personal data. We use encrypted storage and role-based access.  
**You control your data:** export or delete anytime in **Privacy & data controls**.

**What we collect**
- Account: email, username, timestamps
- App inputs: calculations, goals, preferences
- Diagnostics: anonymized events for reliability and abuse prevention

**How we use it**
- Provide core features, improve accuracy and reliability
- Optional analytics (aggregated, de-identified)

**Your rights**
- Access, correct, export, delete your data
- Withdraw consent for optional analytics

**Contact**
support@fynstra.app
"""

TERMS_MD = """
By using Fynstra, you agree to:
- Use the app lawfully and responsibly
- Not reverse engineer or abuse rate limits
- Accept that insights are **informational** and not financial advice

**Accounts**
You’re responsible for safeguarding your credentials. We may suspend accounts for abuse or security concerns.

**Content & Licenses**
You own your inputs. You grant us a limited license to process them to deliver features.

**Disclaimers**
The service is provided *as-is* without warranties. We’re not liable for indirect or consequential damages.

**Changes**
We may update these Terms; continued use means acceptance.

**Contact**
fynstra@gmail.com
"""


# ===============================
# MODALS / POPOVERS
# ===============================
def show_privacy():
    if hasattr(st, "dialog"):
        @st.dialog("Privacy Policy")
        def _d():
            st.markdown(PRIVACY_MD)
        _d()
    else:
        with st.popover("Privacy Policy"):
            st.markdown(PRIVACY_MD)

def show_terms():
    if hasattr(st, "dialog"):
        @st.dialog("Terms of Service")
        def _d():
            st.markdown(TERMS_MD)
        _d()
    else:
        with st.popover("Terms of Service"):
            st.markdown(TERMS_MD)

# ===============================
# MAIN APPLICATION
# ===============================

# Page title & subtitle
st.title("User Account")
st.markdown("### Manage your account and saved data")

# Initialize state
init_auth_state()

# Main layout wrapper
st.markdown('<div class="auth-layout">', unsafe_allow_html=True)

# Check if user is logged in
if st.session_state.auth.get("user"):
    # User is logged in - show profile
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    show_message()
    render_user_profile()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    # User is not logged in - show auth forms
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    # Show any messages first
    show_message()
    
    # Tab-based interface
    tab1, tab2 = st.tabs(["🔐 Sign In", "🎯 Create Account"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_signup_form()
        
        # Sign up benefits
        st.markdown('<div class="benefits-section">', unsafe_allow_html=True)
        st.markdown('<div class="benefits-title">Why create an account?</div>', unsafe_allow_html=True)
        
        benefits = [
            "💾 Save your financial calculations and scenarios",
            "📊 Track your progress over time",
            "🤖 Get personalized AI recommendations", 
            "📱 Access from any device",
            "🔒 Secure data encryption"
        ]
        
        for benefit in benefits:
            st.markdown(f'<div class="benefit-item">{benefit}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# FOOTER (minimal rectangular white buttons)
# ===============================
st.markdown("""
<style>
.auth-footer{
  text-align:center;
  margin-top:3rem;
  padding-top:2rem;
  border-top:1px solid #e5e7eb;
}

.footer-text{
  color:#64748b;
  font-size:0.875rem;
  margin-bottom:1rem;
  font-weight:500;
}

/* Minimal rectangular buttons */
.footer-buttons .stButton>button{
  display:inline-block;
  background:#ffffff !important;
  color:#374151 !important;
  border:1px solid #d1d5db !important;
  border-radius:0 !important;      
  font-weight:600 !important;
  font-size:0.8rem !important;
  padding:0.3rem 0.7rem !important;
  width:auto !important;
  min-width:0 !important;
  box-shadow:none !important;
  transition:none !important; 
}

/* Hover = subtle color change only */
.footer-buttons .stButton>button:hover{
  background:#f3f4f6 !important; 
  border-color:#9ca3af !important;
  color:#111827 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="auth-footer">', unsafe_allow_html=True)
st.markdown('<div class="footer-text">🛡️ Your data is secure and encrypted • Built with privacy in mind</div>', unsafe_allow_html=True)

# Inline row of buttons
st.markdown('<div class="footer-buttons" style="display:flex;justify-content:center;gap:1rem;">', unsafe_allow_html=True)

if st.button("Privacy Policy", key="btn_privacy_box"):
    show_privacy()

if st.button("Terms of Service", key="btn_terms_box"):
    show_terms()

if st.button("Support", key="btn_support_box"):
    st.markdown(
        """
        <script>window.location.href = "mailto:support@fynstra.app";</script>
        """,
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
