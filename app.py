import streamlit as st
import google.generativeai as genai
from github import Github
import re

# ==========================================
# 🛑 CONFIGURATION
# ==========================================
GEMINI_API_KEY = "AIzaSyAOuRy_VvYM7I1qYQmbbl6eMoyltW2rNkk" # PASTE KEY
GITHUB_TOKEN = "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"     # PASTE NEW TOKEN
GITHUB_REPO_NAME = "Writterharikrishnan/Fun"
NETLIFY_DOMAIN = "https://gilded-monstera-ffd1ca.netlify.app"
# ==========================================

# --- SETUP ---
if GEMINI_API_KEY.startswith("AIza"):
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Ultimate Web Builder", page_icon="⚡", layout="wide")

# Initialize Session State
if 'projects' not in st.session_state: st.session_state.projects = []
if 'experience' not in st.session_state: st.session_state.experience = []
if 'education' not in st.session_state: st.session_state.education = []

def create_slug(text): return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

# --- STYLE DICTIONARY (EASY TO EXPAND) ---
STYLES = {
    "Modern Minimalist": "Clean white background, sans-serif fonts (Inter), large whitespace, subtle gray text.",
    "Cyberpunk Neon": "Dark #0a0a0a background, neon green/pink borders, glowing text effects, tech/glitch font.",
    "Glassmorphism": "Gradient mesh background, semi-transparent white cards (backdrop-filter: blur), rounded corners.",
    "Neobrutalism": "Stark contrast, thick 3px black borders, hard drop shadows, bold vibrant colors (yellow/purple).",
    "Bento Grid": "Apple-style card layout, soft gray background, highly organized grid structure, rounded corners.",
    "Retro Terminal": "Black background, bright green monospace text, blinking cursor effect, code-editor aesthetic."
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Settings")
    
    # MODE SELECTOR (Foundation for Company Mode)
    mode = st.radio("Website Type", ["Personal Portfolio", "Company Landing Page"])
    
    st.subheader("🎨 Visual Style")
    # Using Radio for now, but you can add images above this later!
    selected_style_name = st.radio("Choose a Theme", list(STYLES.keys()))
    accent_color = st.color_picker("Accent Color", "#3B82F6")

# --- MAIN UI ---
st.title(f"🚀 Build your {mode}")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Basics", "💼 Experience", "📂 Projects", "🚀 Publish"])

# 1. BASICS
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name / Company Name", "Harikrishnan")
        role = st.text_input("Headline / Tagline", "Building the Future of AI")
        email = st.text_input("Email", "hello@example.com")
    with col2:
        logo_url = st.text_input("Logo Image URL (Optional)", placeholder="https://example.com/logo.png")
        socials = st.text_input("Social Links (GitHub, LinkedIn, X)", "GitHub, LinkedIn")
    
    bio = st.text_area("Bio / About Us", "We specialize in...")
    skills = st.text_input("Skills / Services (Comma separated)", "Python, AI, Web Dev")
    achievements = st.text_input("Key Achievements (Awards, Stats)", "Won Hackathon 2024, 50+ Clients Served")

# 2. EXPERIENCE & EDUCATION
with tab2:
    st.subheader("Work Experience")
    with st.expander("➕ Add Experience"):
        job_role = st.text_input("Role / Title")
        company = st.text_input("Company Name")
        duration = st.text_input("Duration (e.g. 2022-2024)")
        if st.button("Add Job"):
            st.session_state.experience.append(f"{job_role} at {company} ({duration})")
    st.write(st.session_state.experience)

    st.subheader("Education")
    with st.expander("➕ Add Education"):
        degree = st.text_input("Degree")
        school = st.text_input("University/School")
        if st.button("Add Education"):
            st.session_state.education.append(f"{degree} from {school}")
    st.write(st.session_state.education)

# 3. PROJECTS
with tab3:
    st.subheader("Projects / Case Studies")
    with st.expander("➕ Add Project"):
        p_title = st.text_input("Title")
        p_desc = st.text_input("Description")
        if st.button("Add Project"):
            st.session_state.projects.append(f"{p_title}: {p_desc}")
    st.write(st.session_state.projects)

# 4. PUBLISH
with tab4:
    if st.button("✨ GENERATE WEBSITE", type="primary"):
        if not GITHUB_TOKEN or "ghp_" not in GITHUB_TOKEN:
            st.error("GitHub Token Missing in Code!")
            st.stop()
            
        status = st.status("🧠 AI Architect Working...", expanded=True)
        
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash-preview-09-2025')
            
            # GET THE CSS RULES FROM DICTIONARY
            css_rules = STYLES[selected_style_name]
            
            prompt = f"""
            Act as a Senior Web Developer. Create a SINGLE HTML file with internal CSS.
            
            ### CONTENT:
            - Mode: {mode}
            - Name: {name}
            - Role: {role}
            - Bio: {bio}
            - Logo URL: {logo_url} (If empty, use Name as text logo)
            - Achievements: {achievements}
            - Experience List: {st.session_state.experience}
            - Education List: {st.session_state.education}
            - Projects List: {st.session_state.projects}
            - Skills: {skills}
            
            ### DESIGN INSTRUCTIONS (Strictly Follow):
            - Style Theme: {selected_style_name}
            - CSS Rules: {css_rules}
            - Accent Color: {accent_color}
            - Layout: Responsive, Single Page, Smooth Scroll.
            - Sections: Navbar, Hero, About, Experience (Timeline style), Projects (Grid), Contact.
            
            ### ICONS:
            - Use FontAwesome CDN for icons.
            
            Return ONLY raw HTML.
            """
            
            response = model.generate_content(prompt)
            clean_html = response.text.replace("```html", "").replace("```", "")
            
            # UPLOAD TO GITHUB
            status.write("☁️ Deploying to Netlify...")
            url_slug = create_slug(name)
            file_path = f"users/{url_slug}.html"
            
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(GITHUB_REPO_NAME)
            
            try:
                contents = repo.get_contents(file_path)
                repo.update_file(file_path, f"Update {name}", clean_html, contents.sha)
            except:
                repo.create_file(file_path, f"Create {name}", clean_html)
                
            live_link = f"{NETLIFY_DOMAIN}/{file_path}"
            status.update(label="🎉 PUBLISHED!", state="complete", expanded=False)
            
            st.success("Your website is live!")
            st.markdown(f"### [👉 Click here to open]({live_link})")
            
        except Exception as e:
            st.error(f"Error: {e}")
