import streamlit as st
import base64
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client

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

    /* Clean modern layout */
    .main-container {{
        max-width: 450px;
        margin: 3rem auto;
        padding: 0 1rem;
    }}

    .auth-card {{
        background: white;
        border-radius: 20px;
        padding: 3rem 2.5rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.08);
        border: 1px solid #f1f5f9;
        text-align: center;
    }}

    .brand-header {{
        margin-bottom: 3rem;
    }}

    .brand-title {{
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fc3134, #ff5f1f, #ffc542);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
        line-height: 1.2;
    }}

    .brand-subtitle {{
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 400;
        line-height: 1.5;
    }}

    .tab-container {{
        margin: 2rem 0;
    }}

    /* Form styling */
    .form-container {{
        padding: 2rem 0;
        text-align: left;
    }}

    .form-section {{
        margin-bottom: 1.5rem;
    }}

    .input-label {{
        font-weight: 600;
        color: #374151;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        display: block;
    }}

    /* Streamlit input overrides */
    .stTextInput > div > div > input {{
        border-radius: 12px !important;
        border: 2px solid #e5e7eb !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        background: #fafbfc !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: #fc3134 !important;
        box-shadow: 0 0 0 4px rgba(252, 49, 52, 0.1) !important;
        background: white !important;
    }}

    .stCheckbox > label {{
        font-size: 0.9rem !important;
        color: #4b5563 !important;
    }}

    /* Button styling */
    .auth-button {{
        margin: 1.5rem 0 1rem 0;
    }}

    .stButton > button {{
        width: 100%;
        background: linear-gradient(135deg, #fc3134, #ff5f1f) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(252, 49, 52, 0.3) !important;
        background: linear-gradient(135deg, #e02d30, #ff5f1f) !important;
    }}

    .stButton > button:active {{
        transform: translateY(0) !important;
    }}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.25rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px !important;
        color: #64748b !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: white !important;
        color: #fc3134 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }}

    /* Message styling */
    .success-msg {{
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        border: 1px solid #86efac;
        color: #166534;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        text-align: center;
    }}

    .error-msg {{
        background: linear-gradient(135deg, #fef2f2, #fecaca);
        border: 1px solid #f87171;
        color: #dc2626;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        text-align: center;
    }}

    .info-msg {{
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border: 1px solid #93c5fd;
        color: #1d4ed8;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        text-align: center;
    }}

    /* User profile styling */
    .user-profile {{
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 2px solid #bbf7d0;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
    }}

    .user-avatar {{
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #fc3134, #ffc542);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 2rem;
        margin: 0 auto 1.5rem auto;
        border: 4px solid white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }}

    .user-name {{
        font-size: 1.5rem;
        font-weight: 700;
        color: #166534;
        margin-bottom: 0.5rem;
    }}

    .user-email {{
        color: #65a30d;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }}

    .user-actions {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 2rem;
    }}

    .secondary-button {{
        background: white !important;
        color: #374151 !important;
        border: 2px solid #d1d5db !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}

    .secondary-button:hover {{
        background: #f9fafb !important;
        border-color: #9ca3af !important;
        transform: translateY(-1px) !important;
    }}

    /* Footer */
    .footer {{
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
    }}

    .footer-links {{
        margin-top: 1rem;
    }}

    .footer-links a {{
        color: #fc3134;
        text-decoration: none;
        margin: 0 1rem;
        font-weight: 500;
    }}

    .footer-links a:hover {{
        text-decoration: underline;
    }}

    /* Responsive */
    @media (max-width: 768px) {{
        .main-container {{
            margin: 1rem auto;
            padding: 0 1rem;
        }}
        
        .auth-card {{
            padding: 2rem 1.5rem;
        }}
        
        .brand-title {{
            font-size: 2rem;
        }}
        
        .user-actions {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# SUPABASE & GOOGLE SHEETS SETUP
# ===============================

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            st.error("Supabase credentials not found. Please add SUPABASE_URL and SUPABASE_ANON_KEY to secrets.")
            return None
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
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
        st.error(f"Failed to initialize Google Sheets: {e}")
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

def log_auth_event(event: str, user_data: dict, note: str = ""):
    """Log authentication events to Google Sheets"""
    try:
        sh = open_sheet()
        if not sh:
            return
        
        # Try to get or create Auth_Events worksheet
        try:
            ws = sh.worksheet("Auth_Events")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet("Auth_Events", rows=5000, cols=10)
            ws.append_row(["timestamp", "event", "user_id", "email", "username", "note"])
        
        # Append the event
        ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event,
            user_data.get("id", ""),
            user_data.get("email", ""),
            user_data.get("user_metadata", {}).get("username", ""),
            note
        ], value_input_option="USER_ENTERED")
    except Exception as e:
        st.warning(f"Could not log auth event: {e}")

def upsert_user_profile(user_data: dict):
    """Create or update user profile in Google Sheets"""
    try:
        sh = open_sheet()
        if not sh:
            return
        
        # Try to get or create Users worksheet
        try:
            ws = sh.worksheet("Users")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet("Users", rows=2000, cols=20)
            ws.append_row([
                "user_id", "email", "username", "created_at", "last_login",
                "email_confirmed", "last_sign_in_at", "sign_in_count"
            ])
        
        user_id = user_data.get("id", "")
        email = user_data.get("email", "")
        username = user_data.get("user_metadata", {}).get("username", "")
        
        # Check if user already exists
        try:
            cell = ws.find(user_id)
            # User exists, update last_login
            row_num = cell.row
            ws.update_cell(row_num, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # last_login
        except gspread.CellNotFound:
            # New user, add row
            ws.append_row([
                user_id,
                email,
                username,
                user_data.get("created_at", datetime.now().isoformat()),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # last_login
                str(user_data.get("email_confirmed_at") is not None),
                user_data.get("last_sign_in_at", ""),
                1  # sign_in_count
            ], value_input_option="USER_ENTERED")
            
    except Exception as e:
        st.warning(f"Could not update user profile: {e}")

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
    """Set user session"""
    st.session_state.auth["user"] = user
    st.session_state.auth["session"] = session
    
    # Set user identity for the rest of the app
    st.session_state["auth_method"] = "email"
    st.session_state["user_id"] = user.get("id")
    st.session_state["email"] = user.get("email")
    meta = (user.get("user_metadata") or {})
    st.session_state["display_name"] = meta.get("username") or user.get("email")

def sign_out():
    """Sign out current user"""
    supabase = init_supabase()
    if supabase:
        try:
            supabase.auth.sign_out()
        except:
            pass  # Silent fail if already signed out
    
    # Clear session state
    st.session_state.auth = {"user": None, "session": None}
    for k in ["auth_method", "user_id", "email", "display_name"]:
        st.session_state.pop(k, None)
    
    st.session_state.auth_message = "Successfully signed out!"
    st.session_state.auth_message_type = "success"

# ===============================
# UI COMPONENTS
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
    status_text = "✅ Email Verified" if is_verified else "⏳ Email Pending Verification"
    status_color = "#166534" if is_verified else "#d97706"
    
    st.markdown(f'<div style="color: {status_color}; font-weight: 600; margin-bottom: 1rem;">{status_text}</div>', unsafe_allow_html=True)
    
    # Member since
    created_at = user.get("created_at", "")
    if created_at:
        try:
            member_since = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%B %Y')
            st.markdown(f'<div style="color: #64748b; margin-bottom: 1.5rem;">Member since {member_since}</div>', unsafe_allow_html=True)
        except:
            pass
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Go to Dashboard", key="dashboard_btn", use_container_width=True):
            st.switch_page("Fynstra.py")
    
    with col2:
        st.markdown('<div class="secondary-button">', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
            sign_out()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_signup_form():
    """Render signup form"""
    supabase = init_supabase()
    if not supabase:
        st.error("Authentication service unavailable. Please try again later.")
        return
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("signup_form", clear_on_submit=False):
        st.markdown('<span class="input-label">👤 Username</span>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Enter your display name", key="signup_username", label_visibility="collapsed")
        
        st.markdown('<span class="input-label">📧 Email Address</span>', unsafe_allow_html=True)
        email = st.text_input("", placeholder="Enter your email address", key="signup_email", label_visibility="collapsed")
        
        st.markdown('<span class="input-label">🔒 Password</span>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Create a strong password", key="signup_password", label_visibility="collapsed")
        
        st.markdown('<span class="input-label">🔒 Confirm Password</span>', unsafe_allow_html=True)
        confirm_password = st.text_input("", type="password", placeholder="Confirm your password", key="signup_confirm", label_visibility="collapsed")
        
        # Terms acceptance
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="terms_check")
        
        st.markdown('<div class="auth-button">', unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Create Account")
        st.markdown('</div>', unsafe_allow_html=True)
        
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
                        
                        # Log to Google Sheets
                        log_auth_event("signup", user_dict)
                        upsert_user_profile(user_dict)
                        
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_login_form():
    """Render login form"""
    supabase = init_supabase()
    if not supabase:
        st.error("Authentication service unavailable. Please try again later.")
        return
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<span class="input-label">📧 Email Address</span>', unsafe_allow_html=True)
        email = st.text_input("", placeholder="Enter your email address", key="login_email", label_visibility="collapsed")
        
        st.markdown('<span class="input-label">🔒 Password</span>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Enter your password", key="login_password", label_visibility="collapsed")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("Remember me")
        with col2:
            st.markdown('<div style="text-align: right; padding-top: 0.3rem;"><a href="#" style="color: #fc3134; text-decoration: none; font-size: 0.9rem;">Forgot password?</a></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-button">', unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Sign In")
        st.markdown('</div>', unsafe_allow_html=True)
        
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
                        
                        # Log to Google Sheets
                        log_auth_event("login", user_dict)
                        upsert_user_profile(user_dict)
                        
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
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# MAIN APPLICATION
# ===============================

# Initialize state
init_auth_state()

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Check if user is logged in
if st.session_state.auth.get("user"):
    # User is logged in - show profile
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="brand-header">
        <div class="brand-title">Welcome Back!</div>
        <div class="brand-subtitle">Manage your Fynstra account and access your financial insights</div>
    </div>
    ''', unsafe_allow_html=True)
    
    show_message()
    render_user_profile()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    # User is not logged in - show auth forms
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="brand-header">
        <div class="brand-title">Join Fynstra</div>
        <div class="brand-subtitle">Your AI-powered financial companion for smarter money decisions</div>
    </div>
    ''', unsafe_allow_html=True)
    
    show_message()
    
    # Tab-based interface
    tab1, tab2 = st.tabs(["🔐 Sign In", "🎯 Create Account"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_signup_form()
        
        # Sign up benefits
        st.markdown("---")
        st.markdown("**Why create an account?**")
        benefits = [
            "💾 Save your financial calculations and scenarios",
            "📊 Track your progress over time", 
            "🤖 Get personalized AI recommendations",
            "📱 Access from any device",
            "🔒 Secure data encryption"
        ]
        for benefit in benefits:
            st.markdown(f"• {benefit}")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('''
<div class="footer">
    <div>🛡️ Your data is secure and encrypted • Built with privacy in mind</div>
    <div class="footer-links">
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
        <a href="#">Support</a>
    </div>
</div>
''', unsafe_allow_html=True)
