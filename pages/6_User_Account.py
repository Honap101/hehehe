import streamlit as st
import base64
from datetime import datetime
import hashlib
import uuid

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

    /* Authentication page styling */
    .auth-container {{
        max-width: 500px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }}

    .auth-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}

    .auth-title {{
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #fc3134, #ff5f1f, #ffc542);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}

    .auth-subtitle {{
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }}

    .form-section {{
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }}

    .form-header {{
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .success-message {{
        background: #dcfce7;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}

    .error-message {{
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}

    .info-message {{
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1d4ed8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}

    /* Button styling */
    .stButton > button {{
        width: 100%;
        background: linear-gradient(90deg, #fc3134, #ff5f1f) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(252, 49, 52, 0.3) !important;
    }}

    /* Secondary button */
    .secondary-btn > button {{
        background: #ffffff !important;
        color: #374151 !important;
        border: 2px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
    }}

    .secondary-btn > button:hover {{
        background: #f9fafb !important;
        border-color: #9ca3af !important;
    }}

    /* Input styling */
    .stTextInput > div > div > input {{
        border-radius: 8px !important;
        border: 2px solid #e5e7eb !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: #fc3134 !important;
        box-shadow: 0 0 0 3px rgba(252, 49, 52, 0.1) !important;
    }}

    /* User profile section */
    .user-profile {{
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    .user-info {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }}

    .user-avatar {{
        width: 48px;
        height: 48px;
        background: linear-gradient(45deg, #fc3134, #ffc542);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# AUTHENTICATION FUNCTIONS
# ===============================

def initialize_auth_state():
    """Initialize authentication state"""
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_message" not in st.session_state:
        st.session_state.auth_message = None
    if "auth_message_type" not in st.session_state:
        st.session_state.auth_message_type = None

def hash_password(password):
    """Simple password hashing (use proper hashing in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_id():
    """Generate unique user ID"""
    return str(uuid.uuid4())[:12]

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

def simulate_user_signup(email, password, username):
    """Simulate user signup (replace with real database in production)"""
    # In production, you would:
    # 1. Check if email already exists
    # 2. Hash the password properly
    # 3. Store in database
    # 4. Send verification email
    
    user_data = {
        "id": create_user_id(),
        "email": email,
        "username": username,
        "password_hash": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "verified": False  # Would be set to True after email verification
    }
    
    # Store in session state (temporary - use real database in production)
    if "users_db" not in st.session_state:
        st.session_state.users_db = {}
    
    st.session_state.users_db[email] = user_data
    return user_data

def simulate_user_login(email, password):
    """Simulate user login (replace with real authentication in production)"""
    if "users_db" not in st.session_state:
        st.session_state.users_db = {}
    
    user_data = st.session_state.users_db.get(email)
    if user_data and user_data["password_hash"] == hash_password(password):
        return user_data
    return None

def logout_user():
    """Log out current user"""
    st.session_state.auth_user = None
    st.session_state.auth_message = "Successfully logged out!"
    st.session_state.auth_message_type = "success"

# ===============================
# UI COMPONENTS
# ===============================

def show_message():
    """Display authentication messages"""
    if st.session_state.auth_message:
        if st.session_state.auth_message_type == "success":
            st.markdown(f'<div class="success-message">✅ {st.session_state.auth_message}</div>', unsafe_allow_html=True)
        elif st.session_state.auth_message_type == "error":
            st.markdown(f'<div class="error-message">❌ {st.session_state.auth_message}</div>', unsafe_allow_html=True)
        elif st.session_state.auth_message_type == "info":
            st.markdown(f'<div class="info-message">ℹ️ {st.session_state.auth_message}</div>', unsafe_allow_html=True)
        
        # Clear message after displaying
        st.session_state.auth_message = None
        st.session_state.auth_message_type = None

def render_user_profile():
    """Render logged-in user profile"""
    user = st.session_state.auth_user
    
    st.markdown('<div class="user-profile">', unsafe_allow_html=True)
    
    # User info header
    st.markdown(f'''
    <div class="user-info">
        <div class="user-avatar">{user["username"][0].upper()}</div>
        <div>
            <div style="font-weight: 600; font-size: 1.1rem; color: #166534;">{user["username"]}</div>
            <div style="color: #65a30d; font-size: 0.9rem;">{user["email"]}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Account status
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Account Status:** " + ("✅ Verified" if user.get("verified") else "⏳ Pending Verification"))
    with col2:
        st.markdown(f"**Member Since:** {datetime.fromisoformat(user['created_at']).strftime('%B %Y')}")
    
    # User actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Go to Dashboard", key="dashboard_btn"):
            st.info("Navigate to your financial dashboard here!")
    
    with col2:
        if st.button("⚙️ Account Settings", key="settings_btn"):
            st.info("Account settings would be implemented here!")
    
    with col3:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="logout_btn"):
            logout_user()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_signup_form():
    """Render signup form"""
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">🎯 Create Your Account</div>', unsafe_allow_html=True)
    
    with st.form("signup_form", clear_on_submit=False):
        username = st.text_input("👤 Username", placeholder="Enter your display name")
        email = st.text_input("📧 Email Address", placeholder="Enter your email address")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        # Terms acceptance
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submitted = st.form_submit_button("🚀 Create Account")
        
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
            
            # Check if email already exists
            if "users_db" in st.session_state and email in st.session_state.users_db:
                errors.append("An account with this email already exists")
            
            if errors:
                st.session_state.auth_message = " • ".join(errors)
                st.session_state.auth_message_type = "error"
                st.rerun()
            else:
                # Create account
                try:
                    user_data = simulate_user_signup(email, password, username)
                    st.session_state.auth_message = f"Account created successfully! Welcome {username}! 🎉"
                    st.session_state.auth_message_type = "success"
                    st.rerun()
                except Exception as e:
                    st.session_state.auth_message = f"Failed to create account: {str(e)}"
                    st.session_state.auth_message_type = "error"
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_login_form():
    """Render login form"""
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">🔐 Sign In to Your Account</div>', unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("📧 Email Address", placeholder="Enter your email address")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            remember_me = st.checkbox("Remember me")
        with col2:
            st.markdown('<div style="text-align: right; padding-top: 0.3rem;"><a href="#" style="color: #fc3134; text-decoration: none; font-size: 0.9rem;">Forgot password?</a></div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Sign In")
        
        if submitted:
            if not email or not password:
                st.session_state.auth_message = "Please enter both email and password"
                st.session_state.auth_message_type = "error"
                st.rerun()
            else:
                user_data = simulate_user_login(email, password)
                if user_data:
                    st.session_state.auth_user = user_data
                    st.session_state.auth_message = f"Welcome back, {user_data['username']}! 🎉"
                    st.session_state.auth_message_type = "success"
                    st.rerun()
                else:
                    st.session_state.auth_message = "Invalid email or password"
                    st.session_state.auth_message_type = "error"
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# MAIN APPLICATION
# ===============================

st.title("Account Access")

# Initialize state
initialize_auth_state()

# Show any pending messages
show_message()

# Check if user is logged in
if st.session_state.auth_user:
    # User is logged in - show profile
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="auth-header">
        <div class="auth-title">Welcome Back!</div>
        <div class="auth-subtitle">Manage your Fynstra account and access your financial insights</div>
    </div>
    ''', unsafe_allow_html=True)
    
    render_user_profile()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    # User is not logged in - show auth forms
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="auth-header">
        <div class="auth-title">Join Fynstra</div>
        <div class="auth-subtitle">Your AI-powered financial companion for smarter money decisions</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Tab-based interface
    tab1, tab2 = st.tabs(["🔐 Sign In", "🎯 Create Account"])
    
    with tab1:
        render_login_form()
        
        # Additional login options
        st.markdown("---")
        st.markdown("**Demo Accounts** (for testing):")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Try Demo User", help="Email: demo@fynstra.com, Password: Demo123!"):
                # Create demo user if doesn't exist
                if "users_db" not in st.session_state:
                    st.session_state.users_db = {}
                if "demo@fynstra.com" not in st.session_state.users_db:
                    st.session_state.users_db["demo@fynstra.com"] = {
                        "id": "demo123",
                        "email": "demo@fynstra.com",
                        "username": "Demo User",
                        "password_hash": hash_password("Demo123!"),
                        "created_at": datetime.now().isoformat(),
                        "verified": True
                    }
                
                # Auto-login demo user
                st.session_state.auth_user = st.session_state.users_db["demo@fynstra.com"]
                st.session_state.auth_message = "Logged in as Demo User! 🎉"
                st.session_state.auth_message_type = "success"
                st.rerun()
    
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

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #64748b; font-size: 0.9rem;">'
    '🛡️ Your data is secure and encrypted • Built with privacy in mind<br>'
    'Questions? Contact support@fynstra.com'
    '</div>', 
    unsafe_allow_html=True
)
