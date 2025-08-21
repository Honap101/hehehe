import streamlit as st
import plotly.graph_objects as go
import base64
from datetime import datetime
import io

# PDF Generation imports
try:
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import HorizontalBarChart
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# --- Sidebar Logo and Title (PUT THIS FIRST) ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""

bg_base64 = get_base64_image("sidebar_background.png")
logow_base64 = get_base64_image("logo_white.png") 
logoc_base64 = get_base64_image("logo_colored.png")

# Only show sidebar content if images exist
if logoc_base64:
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

# CSS for sidebar background
if bg_base64:
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
        </style>
        """,
        unsafe_allow_html=True
    )

# ===============================
# PDF GENERATION FUNCTIONS
# ===============================

def create_pdf_styles():
    """Create PDF styles matching Fynstra's color scheme"""
    if not PDF_AVAILABLE:
        return None
        
    base_styles = getSampleStyleSheet()
    
    # Fynstra color palette
    FYNSTRA_RED = colors.HexColor("#fc3134")
    FYNSTRA_ORANGE = colors.HexColor("#ff5f1f") 
    FYNSTRA_GOLD = colors.HexColor("#ffc542")
    DARK_GRAY = colors.HexColor("#333333")
    MEDIUM_GRAY = colors.HexColor("#666666")
    LIGHT_GRAY = colors.HexColor("#f8f9fa")
    
    styles = {
        "title": ParagraphStyle(
            "title",
            parent=base_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=FYNSTRA_RED,
            spaceAfter=12,
            alignment=1,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            textColor=MEDIUM_GRAY,
            spaceAfter=16,
            alignment=1,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=FYNSTRA_ORANGE,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=DARK_GRAY,
            spaceAfter=8,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=MEDIUM_GRAY,
            spaceAfter=4,
        ),
        "score": ParagraphStyle(
            "score",
            parent=base_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=36,
            leading=40,
            textColor=FYNSTRA_RED,
            alignment=1,
        ),
    }
    return styles, FYNSTRA_RED, FYNSTRA_ORANGE, FYNSTRA_GOLD, LIGHT_GRAY

def create_fhi_score_banner(fhi_score: float):
    """Create a visual banner for the FHI score"""
    if not PDF_AVAILABLE:
        return None
        
    d = Drawing(500, 80)
    
    # Background rectangle
    d.add(Rect(0, 0, 500, 80, fillColor=colors.white, strokeColor=colors.HexColor("#e5e7eb"), strokeWidth=1))
    
    # Gradient bar at top
    d.add(Rect(0, 70, 250, 10, fillColor=colors.HexColor("#fc3134"), strokeColor=None))
    d.add(Rect(250, 70, 250, 10, fillColor=colors.HexColor("#ffc542"), strokeColor=None))
    
    # Title and score
    title = String(20, 45, "Financial Health Index", fontName="Helvetica-Bold", fontSize=16, fillColor=colors.HexColor("#333333"))
    score = String(320, 35, f"{fhi_score:.1f}", fontName="Helvetica-Bold", fontSize=28, fillColor=colors.HexColor("#fc3134"))
    score_label = String(420, 40, "/ 100", fontName="Helvetica", fontSize=14, fillColor=colors.HexColor("#666666"))
    
    d.add(title)
    d.add(score)
    d.add(score_label)
    
    return d

def create_component_chart(components: dict):
    """Create a horizontal bar chart for component scores"""
    if not PDF_AVAILABLE:
        return None
        
    labels = list(components.keys())
    values = [float(components[k]) for k in labels]

    d = Drawing(500, 250)
    chart = HorizontalBarChart()
    chart.x = 80
    chart.y = 30
    chart.height = 190
    chart.width = 400
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 9
    
    # Fynstra color for bars
    chart.bars[0].fillColor = colors.HexColor("#ff5f1f")
    chart.bars[0].strokeColor = colors.white
    chart.barLabelFormat = "%0.0f"
    chart.barLabels.fontName = "Helvetica-Bold"
    chart.barLabels.fontSize = 9
    chart.barLabels.fillColor = colors.HexColor("#333333")
    
    d.add(chart)
    return d

def create_data_table(data_rows):
    """Create a styled table for financial data"""
    if not PDF_AVAILABLE:
        return None
        
    table = Table(data_rows, colWidths=[180, 200])
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#666666")),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#333333")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table

def generate_fynstra_pdf(fhi_score: float, components: dict, user_inputs: dict) -> bytes:
    """Generate a professional PDF report with Fynstra branding"""
    if not PDF_AVAILABLE:
        return generate_text_report(fhi_score, components, user_inputs).encode('utf-8')
    
    try:
        styles_data = create_pdf_styles()
        if styles_data is None:
            return generate_text_report(fhi_score, components, user_inputs).encode('utf-8')
            
        styles, FYNSTRA_RED, FYNSTRA_ORANGE, FYNSTRA_GOLD, LIGHT_GRAY = styles_data
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40,
            title="Fynstra Financial Health Report"
        )
        
        story = []
        
        # Header
        story.append(Paragraph("Financial Health Report", styles["title"]))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Fynstra AI Platform",
            styles["subtitle"]
        ))
        story.append(Spacer(1, 20))
        
        # FHI Score Banner
        banner = create_fhi_score_banner(fhi_score)
        if banner:
            story.append(banner)
        story.append(Spacer(1, 20))
        
        # Overall Assessment
        if fhi_score >= 85:
            assessment = "Excellent! You're in great financial shape and well-prepared for the future."
        elif fhi_score >= 70:
            assessment = "Good! You have a solid foundation. Stay consistent and work on gaps where needed."
        elif fhi_score >= 50:
            assessment = "Fair. You're on your way, but some areas need attention to build a stronger safety net."
        else:
            assessment = "Needs Improvement. Your finances require urgent attention."
            
        story.append(Paragraph("Overall Assessment", styles["section_header"]))
        story.append(Paragraph(assessment, styles["body"]))
        story.append(Spacer(1, 15))
        
        # Financial Profile
        story.append(HRFlowable(width="100%", thickness=1, color=FYNSTRA_ORANGE))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Your Financial Profile", styles["section_header"]))
        
        profile_data = [
            ["Age", f"{user_inputs.get('age', 'N/A')} years"],
            ["Monthly Income", f"₱{user_inputs.get('income', 0):,.0f}"],
            ["Monthly Expenses", f"₱{user_inputs.get('expenses', 0):,.0f}"],
            ["Monthly Savings", f"₱{user_inputs.get('savings', 0):,.0f}"],
            ["Total Investments", f"₱{user_inputs.get('total_investments', 0):,.0f}"],
            ["Net Worth", f"₱{user_inputs.get('net_worth', 0):,.0f}"],
            ["Emergency Fund", f"₱{user_inputs.get('emergency_fund', 0):,.0f}"],
        ]
        
        profile_table = create_data_table(profile_data)
        if profile_table:
            story.append(profile_table)
        story.append(Spacer(1, 20))
        
        # Component Breakdown
        story.append(HRFlowable(width="100%", thickness=1, color=FYNSTRA_ORANGE))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Component Breakdown", styles["section_header"]))
        story.append(Paragraph(
            "Your FHI score is calculated from five key components. Each component is scored from 0 to 100, with higher scores indicating better financial health.",
            styles["body"]
        ))
        story.append(Spacer(1, 10))
        
        # Component chart
        chart = create_component_chart(components)
        if chart:
            story.append(chart)
        story.append(Spacer(1, 15))
        
        # Component details
        component_data = []
        for component, score in components.items():
            component_data.append([component, f"{score:.1f}/100"])
        
        component_table = create_data_table(component_data)
        if component_table:
            story.append(component_table)
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(HRFlowable(width="100%", thickness=1, color=FYNSTRA_ORANGE))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Key Recommendations", styles["section_header"]))
        
        recommendations = []
        if components.get("Emergency Fund", 0) < 60:
            recommendations.append("Build your emergency fund to cover 3-6 months of expenses")
        if components.get("Debt-to-Income", 0) < 70:
            recommendations.append("Focus on reducing high-interest debt to improve your debt-to-income ratio")
        if components.get("Savings Rate", 0) < 20:
            recommendations.append("Increase your monthly savings rate to at least 20% of income")
        if components.get("Investment", 0) < 50:
            recommendations.append("Start or increase regular investments for long-term wealth building")
        if components.get("Net Worth", 0) < 50:
            recommendations.append("Focus on building assets and reducing liabilities to grow net worth")
        
        if not recommendations:
            recommendations.append("Continue your excellent financial habits and consider advanced investment strategies")
        
        for i, rec in enumerate(recommendations[:5], 1):
            story.append(Paragraph(f"{i}. {rec}", styles["body"]))
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "This report is for informational purposes only and does not constitute financial advice. "
            "For personalized financial planning, consult with a qualified financial advisor.",
            styles["small"]
        ))
        story.append(Spacer(1, 5))
        story.append(Paragraph(
            "Generated by Fynstra AI - Your AI-Powered Financial Strategy Platform",
            styles["small"]
        ))
        
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
        
    except Exception as e:
        st.error(f"PDF generation failed: {e}. Generating text report instead.")
        return generate_text_report(fhi_score, components, user_inputs).encode('utf-8')

# ===============================
# UTILITY FUNCTIONS
# ===============================

def load_user_financial_data():
    """Load user's financial data if they are signed in"""
    try:
        from supabase import create_client
        import gspread
        from google.oauth2.service_account import Credentials
        import time
        
        user_id = st.session_state.get("user_id")
        if not user_id:
            return False
        
        last_load_time = st.session_state.get("last_load_time", 0)
        current_time = time.time()
        if current_time - last_load_time < 5:
            return False
            
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
            if "429" in str(e) or "Quota exceeded" in str(e):
                st.warning("⏳ API rate limit reached. Please try loading again in a few minutes.")
                return False
            else:
                st.error(f"Failed to connect to database: {e}")
                return False
            
        try:
            values = ws.get_all_values()
            if not values:
                return False
                
            header = values[0]
            rows = values[1:] if len(values) > 1 else []
            
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
                    if len(user_row) > col_idx:
                        cell_value = user_row[col_idx]
                        
                        if cell_value and cell_value != "" and cell_value != "0":
                            try:
                                value = float(cell_value)
                                if value >= 0:
                                    if session_key == "age":
                                        st.session_state[session_key] = float(int(value))
                                    else:
                                        st.session_state[session_key] = value
                                    loaded_fields.append(session_key)
                            except (ValueError, TypeError):
                                pass
            
            st.session_state["last_load_time"] = current_time
            
            if loaded_fields:
                st.success(f"✅ Loaded {len(loaded_fields)} fields from your saved data")
                            
            return len(loaded_fields) > 0
            
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                st.warning("⏳ API rate limit reached. Please try loading again in a few minutes.")
            else:
                st.error(f"Error loading user data: {e}")
            return False
            
    except ImportError:
        return False
    except Exception as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.warning("⏳ API rate limit reached. Please try again in a few minutes.")
        return False

def save_user_financial_data():
    """Save user's financial data to the database"""
    try:
        from supabase import create_client
        import gspread
        from google.oauth2.service_account import Credentials
        import time
        import random
        from datetime import datetime
        
        user_id = st.session_state.get("user_id")
        email = st.session_state.get("email", "")
        display_name = st.session_state.get("display_name", "")
        
        if not user_id:
            return False
            
        last_save_time = st.session_state.get("last_save_time", 0)
        current_time = time.time()
        if current_time - last_save_time < 30:
            st.info("⏱️ Please wait before saving again (rate limiting)")
            return False
            
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
        
        has_meaningful_data = any(data_to_save[key] > 0 for key in data_to_save.keys() if key != "last_FHI")
        if not has_meaningful_data:
            return False
        
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
            if "429" in str(e) or "Quota exceeded" in str(e):
                st.warning("⏳ API rate limit reached. Your data will be saved automatically later. Please try again in a few minutes.")
                return False
            else:
                st.error(f"Failed to connect to database for saving: {e}")
                return False
            
        try:
            values = ws.get_all_values()
            if not values:
                return False
                
            header = values[0]
            rows = values[1:] if len(values) > 1 else []
            
            if "user_id" not in header:
                return False
                
            uid_idx = header.index("user_id")
            user_row_idx = None
            
            for i, row in enumerate(rows, start=2):
                if len(row) > uid_idx and row[uid_idx] == user_id:
                    user_row_idx = i
                    break
                    
            if not user_row_idx:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row_data = []
                
                for col in header:
                    if col == "user_id":
                        new_row_data.append(user_id)
                    elif col == "email":
                        new_row_data.append(email)
                    elif col == "username":
                        new_row_data.append(display_name)
                    elif col == "created_at":
                        new_row_data.append(now)
                    elif col == "last_login":
                        new_row_data.append(now)
                    elif col in data_to_save:
                        new_row_data.append(str(data_to_save[col]))
                    else:
                        new_row_data.append("")
                
                try:
                    ws.append_row(new_row_data)
                    user_row_idx = len(rows) + 2
                    st.success("📝 Created your user profile in the database")
                except Exception as e:
                    st.error(f"Failed to create user profile: {e}")
                    return False
            
            cells_to_update = []
            updated_fields = []
            
            for field, value in data_to_save.items():
                if field in header:
                    col_idx = header.index(field) + 1
                    cell_address = gspread.utils.rowcol_to_a1(user_row_idx, col_idx)
                    cells_to_update.append({
                        'range': cell_address,
                        'values': [[str(value)]]
                    })
                    updated_fields.append(field)
            
            if cells_to_update:
                def with_backoff(fn, tries: int = 3):
                    for i in range(tries):
                        try:
                            return fn()
                        except Exception as e:
                            if "429" in str(e) or "Quota exceeded" in str(e):
                                if i < tries - 1:
                                    wait_time = (2 ** i) + random.uniform(5, 15)
                                    time.sleep(wait_time)
                                else:
                                    raise
                            else:
                                if i == tries - 1:
                                    raise
                                time.sleep((2 ** i) + random.random())
                
                with_backoff(lambda: ws.batch_update(cells_to_update))
                st.session_state["last_save_time"] = current_time
                
                if updated_fields:
                    st.success(f"💾 Successfully saved {len(updated_fields)} financial fields!")
                    
            return len(updated_fields) > 0
            
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                st.warning("⏳ API rate limit reached. Please try saving again in a few minutes.")
                return False
            else:
                st.error(f"Error saving data: {e}")
                return False
            
    except ImportError:
        st.warning("Database connection not available")
        return False
    except Exception as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.warning("⏳ API rate limit reached. Please try saving again in a few minutes.")
        else:
            st.error(f"Unexpected error while saving: {e}")
        return False

def validated_number_input(label, key, min_value=0.0, step=1.0, help_text=None, **kwargs):
    def update_status():
        st.session_state[f"{key}_status"] = "✅" if st.session_state.get(key, 0) > 0 else "⬜️"

    if f"{key}_status" not in st.session_state:
        st.session_state[f"{key}_status"] = "⬜️"

    kwargs_clean = {k: v for k, v in kwargs.items() if k != "value"}
    
    if key in st.session_state and st.session_state[key] is not None:
        default_value = float(st.session_state[key])
    else:
        default_value = float(min_value)

    st.markdown(
        f"""
            <div style='display:flex; align-items:center; gap:6px; font-size:14px; margin-bottom:2px;'>
                <span>{st.session_state[f'{key}_status']}</span>
                <span>{label}</span>
            </div>
            """,
            unsafe_allow_html=True
    )

    value = st.number_input(
        label="",
        min_value=float(min_value),
        step=float(step),
        key=key,
        on_change=update_status,
        value=default_value,
        **kwargs_clean
    )

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

# ===============================
# MAIN APPLICATION
# ===============================

# Page config
st.set_page_config(page_title="Fynstra – Financial Health Index", layout="centered")

# Load user data if signed in
user_signed_in = st.session_state.get("user_id") is not None
if user_signed_in:
    if "force_reload" not in st.session_state:
        st.session_state["force_reload"] = True
        
    if st.session_state.get("force_reload", False):
        if load_user_financial_data():
            st.session_state["force_reload"] = False
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
                keys_to_clear = [
                    "age", "monthly_income", "monthly_expenses", "monthly_savings", 
                    "monthly_debt", "total_investments", "net_worth", "emergency_fund", 
                    "FHI", "life_stage", "other_stage_input", "proceed", "force_reload"
                ]
                
                status_keys = [f"{key}_status" for key in keys_to_clear]
                
                for key in keys_to_clear + status_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.session_state["age"] = 18.0
                st.session_state["monthly_income"] = 0.0
                st.session_state["monthly_expenses"] = 0.0
                st.session_state["monthly_savings"] = 0.0
                st.session_state["monthly_debt"] = 0.0
                st.session_state["total_investments"] = 0.0
                st.session_state["net_worth"] = 0.0
                st.session_state["emergency_fund"] = 0.0
                st.session_state["life_stage"] = "Student"
                        
                st.session_state["force_reload"] = True
                st.success("🔄 Form reset! All inputs cleared.")
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
    text-align: center;
    font-size: 20px;
    font-weight: 400;
    margin-bottom: 20px;
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
        age = validated_number_input("Your Age", key="age", min_value=18.0, step=1.0)
        monthly_expenses = validated_number_input("Monthly Living Expenses (₱)", key="monthly_expenses", step=50.0)
        monthly_savings = validated_number_input("Monthly Savings (₱)", key="monthly_savings", step=50.0)
        emergency_fund = validated_number_input("Emergency Fund Amount (₱)", key="emergency_fund", step=500.0)

    with col2:
        monthly_income = validated_number_input("Monthly Gross Income (₱)", key="monthly_income", step=100.0)
        monthly_debt = validated_number_input("Monthly Debt Payments (₱)", key="monthly_debt", step=50.0)
        total_investments = validated_number_input("Total Investments (₱)", key="total_investments", step=500.0)
        net_worth = validated_number_input("Net Worth (₱)", key="net_worth", step=500.0)

with st.container(border=True):
    st.markdown("""
    <div style="
        display: inline-block;
        background: #ff5f1f;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        text-align: center;
        font-size: 20px;
        font-weight: 400;
        margin-bottom: 20px;
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
[data-baseweb="radio"] label span {
    color: #ff5f1f;
}
</style>
""", unsafe_allow_html=True)

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
[data-testid="stButton"] button {
    background: linear-gradient(90deg, #fc3134, #ff5f1f, #ffc542 );
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    transition: all 0.3s ease;
}

[data-testid="stButton"] button:hover {
    filter: brightness(1.1);
}

[data-testid="stButton"] button:active {
    transform: scale(0.98);
}
</style>
""", unsafe_allow_html=True)

if st.button("Check My Financial Health"):
    missing_fields = []
    if monthly_income == 0: missing_fields.append("Monthly Income")
    if monthly_expenses == 0: missing_fields.append("Monthly Expenses")
    if net_worth == 0.00: missing_fields.append("Net Worth")
    if total_investments == 0.00: missing_fields.append("Total Investments")
    if emergency_fund == 0.00: missing_fields.append("Emergency Fund")
    if monthly_savings == 0.00: missing_fields.append("Monthly Savings")
    if monthly_debt == 0.00: missing_fields.append("Monthly Debt Payments")

    if missing_fields:
        missing_fields_popup(missing_fields)
    else:
        st.session_state['proceed'] = True

# Run FHI calculation if allowed
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
        
        # Store results in session state
        st.session_state["fhi_results"] = {
            "FHI": FHI_rounded,
            "components": components,
            "user_inputs": {
                "age": age,
                "income": monthly_income,
                "expenses": monthly_expenses,
                "savings": monthly_savings,
                "debt": monthly_debt,
                "total_investments": total_investments,
                "net_worth": net_worth,
                "emergency_fund": emergency_fund
            }
        }
        
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

        # Save to database if user is signed in
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
                    help_text = component_descriptions.get(label, "Higher is better.")
                    st.markdown(f"*{label} Score:* {round(score)} / 100", help=help_text)

                    interpretation, suggestions = interpret(label, score)
                    st.markdown(f"<span style='font-size:13px; color:#444;'>{interpretation}</span>", unsafe_allow_html=True)

                    with st.expander("💡 How to improve"):
                        for tip in suggestions:
                            st.write(f"- {tip}")

        # Peer comparison
        st.subheader("👥 How You Compare")
            
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
            
        # Generate Report Section
        st.subheader("📄 Download Your Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Text Report
            if st.button("📄 Generate Text Report", use_container_width=True):
                report = generate_text_report(FHI_rounded, components, {
                    "age": age,
                    "income": monthly_income,
                    "expenses": monthly_expenses,
                    "savings": monthly_savings
                })
                st.download_button(
                    label="⬇️ Download Text Report",
                    data=report,
                    file_name=f"fynstra_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col2:
            # PDF Report
            if PDF_AVAILABLE:
                if st.button("📄 Generate PDF Report", use_container_width=True):
                    with st.spinner("Generating PDF report..."):
                        try:
                            pdf_data = generate_fynstra_pdf(
                                FHI_rounded, 
                                components, 
                                {
                                    "age": age,
                                    "income": monthly_income,
                                    "expenses": monthly_expenses,
                                    "savings": monthly_savings,
                                    "debt": monthly_debt,
                                    "total_investments": total_investments,
                                    "net_worth": net_worth,
                                    "emergency_fund": emergency_fund
                                }
                            )
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=pdf_data,
                                file_name=f"fynstra_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Failed to generate PDF: {e}")
            else:
                st.button("📄 PDF Not Available", disabled=True, help="Install reportlab to enable PDF generation", use_container_width=True)

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
