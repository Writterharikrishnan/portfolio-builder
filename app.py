import streamlit as st
import google.generativeai as genai
from github import Github
import re
import time
import random
import os

# ==========================================
# 🔐 SECURE CONFIGURATION
# ==========================================
# This section automatically finds your keys from a safe place.
# DO NOT TYPE YOUR KEYS HERE. Put them in .streamlit/secrets.toml
try:
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    if "GITHUB_TOKEN" in st.secrets:
        GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    else:
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
except:
    GEMINI_API_KEY = None
    GITHUB_TOKEN = None

# Hardcoded settings (Safe to be public)
GITHUB_REPO_NAME = "Writterharikrishnan/Fun"
NETLIFY_DOMAIN = "https://gilded-monstera-ffd1ca.netlify.app"
# ==========================================

# --- SETUP ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Ultimate Web Builder", page_icon="⚡", layout="wide")

# Initialize Session State
if 'projects' not in st.session_state: st.session_state.projects = []
if 'experience' not in st.session_state: st.session_state.experience = []
if 'education' not in st.session_state: st.session_state.education = []

def create_slug(text): 
    # Creates "hari-krishnan" from "Hari Krishnan"
    clean_text = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    # Adds random number to prevent duplicates (e.g., hari-krishnan-482)
    return f"{clean_text}-{random.randint(100, 999)}"

# --- STYLE DICTIONARY ---
STYLES = {
    "Modern Minimalist": "Clean white background, sans-serif fonts (Inter), large whitespace, subtle gray text, no borders.",
    "Cyberpunk Neon": "Dark #0a0a0a background, neon green/pink borders, glowing text effects, tech/glitch font, high contrast.",
    "Glassmorphism": "Gradient mesh background, semi-transparent white cards (backdrop-filter: blur 10px), rounded corners, soft shadows.",
    "Neobrutalism": "Stark high contrast, thick 3px black borders, hard drop shadows (box-shadow: 4px 4px 0 #000), bold vibrant colors.",
    "Bento Grid": "Apple-style card layout, soft gray background (#f5f5f7), highly organized grid structure, rounded corners (24px).",
    "Retro Terminal": "Black background, bright green monospace text, blinking cursor effect, looks like a VS Code editor or CMD prompt."
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Pro Settings")
    
    # Check Connection
    if not GEMINI_API_KEY or not GITHUB_TOKEN:
        st.error("❌ Keys Missing! Add them to secrets.toml")
    else:
        st.success("✅ System Online")

    st.markdown("---")
    mode = st.radio("Website Mode", ["Personal Portfolio", "Company Landing Page"])
    
    st.subheader("🎨 Visual Design")
    selected_style_name = st.selectbox("Choose a Theme", list(STYLES.keys()))
    accent_color = st.color_picker("Brand Color", "#3B82F6")

# --- MAIN UI ---
st.title(f"🚀 Build your {mode}")
st.markdown("Fill in the details below to generate a professional, hosted website in seconds.")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Identity", "💼 Experience", "📂 Projects", "🚀 Publish"])

# 1. BASICS
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name / Company Name", placeholder="e.g. Acme AI or John Doe")
        role = st.text_input("Headline / Tagline", placeholder="e.g. Building the Future")
        email = st.text_input("Email", placeholder="contact@example.com")
    with col2:
        logo_url = st.text_input("Logo URL (Optional)", placeholder="https://example.com/logo.png")
        socials = st.text_input("Social Links (GitHub, LinkedIn, X)", placeholder="Comma separated links")
    
    bio = st.text_area("Bio / About Us", placeholder="Tell your story here...")
    skills = st.text_input("Skills / Services (Comma separated)", placeholder="Python, React, AI Agents...")
    achievements = st.text_input("Key Achievements", placeholder="Won Hackathon 2024, 10k Users...")

# 2. EXPERIENCE & EDUCATION
with tab2:
    col_exp, col_edu = st.columns(2)
    
    with col_exp:
        st.subheader("Work Experience")
        with st.expander("➕ Add Job"):
            j_role = st.text_input("Role")
            j_comp = st.text_input("Company")
            j_dur = st.text_input("Date")
            if st.button("Add Job"):
                st.session_state.experience.append(f"{j_role} at {j_comp} ({j_dur})")
        if st.session_state.experience:
            st.write(st.session_state.experience)
            if st.button("Clear Jobs"): st.session_state.experience = []

    with col_edu:
        st.subheader("Education")
        with st.expander("➕ Add Education"):
            e_deg = st.text_input("Degree")
            e_sch = st.text_input("School")
            if st.button("Add School"):
                st.session_state.education.append(f"{e_deg} at {e_sch}")
        if st.session_state.education:
            st.write(st.session_state.education)

# 3. PROJECTS
with tab3:
    st.subheader("Projects / Products")
    with st.expander("➕ Add Project", expanded=True):
        p_title = st.text_input("Project Title")
        p_desc = st.text_input("Short Description")
        p_tech = st.text_input("Tech Used")
        if st.button("Add Project"):
            st.session_state.projects.append(f"{p_title}: {p_desc} [{p_tech}]")
    
    if st.session_state.projects:
        st.write("### Active List:")
        for p in st.session_state.projects:
            st.markdown(f"- {p}")
        if st.button("Clear Projects"): st.session_state.projects = []

# 4. PUBLISH
with tab4:
    st.info("Note: Due to high traffic, generation may take up to 20 seconds.")
    
    if st.button("✨ GENERATE & PUBLISH LIVE", type="primary"):
        if not GITHUB_TOKEN or not GEMINI_API_KEY:
            st.error("API Keys are missing. Check your secrets file.")
            st.stop()
            
        status = st.status("🚀 Engine Started...", expanded=True)
        
        try:
            # --- STEP 1: AI GENERATION WITH RETRY ---
            model = genai.GenerativeModel('models/gemini-2.5-flash-preview-09-2025')
            css_rules = STYLES[selected_style_name]
            
            prompt = f"""
            Act as a Senior Web Developer. Create a SINGLE HTML file with internal CSS.
            
            ### CONTENT DATA:
            - Mode: {mode}
            - Name: {name}
            - Tagline: {role}
            - Bio: {bio}
            - Logo URL: {logo_url} (If empty, use Name as text logo)
            - Contact: {email}
            - Socials: {socials}
            - Achievements: {achievements}
            - Skills/Services: {skills}
            - Work History: {st.session_state.experience}
            - Education: {st.session_state.education}
            - Projects List: {st.session_state.projects}
            
            ### DESIGN RULES:
            - Theme: {selected_style_name}
            - CSS Logic: {css_rules}
            - Accent Color: {accent_color}
            - Layout: Single Page, Responsive, Flexbox/Grid.
            - FontAwesome: Use CDN for icons.
            
            ### STRUCTURE:
            1. Navbar (Logo + Links)
            2. Hero Section (Name + Tagline + Bio)
            3. Skills/Services Section (Pills or Cards)
            4. Timeline Section (Experience & Education)
            5. Projects Grid (Cards with hover effects)
            6. Footer (Contact & Socials)
            
            Return ONLY raw HTML code.
            """
            
            response = None
            # Retry loop for stability
            for attempt in range(3):
                try:
                    status.write(f"🧠 Designing (Attempt {attempt+1})...")
                    response = model.generate_content(prompt)
                    break 
                except Exception as e:
                    if "429" in str(e):
                        status.write("⚠️ Traffic high, waiting 5s...")
                        time.sleep(5)
                    else:
                        raise e
            
            if not response:
                st.error("Server busy. Please try again.")
                st.stop()

            clean_html = response.text.replace("```html", "").replace("```", "")
            
            # --- STEP 2: GITHUB UPLOAD ---
            status.write("☁️ Deploying to Netlify...")
            
            # Create Unique Filename (e.g. users/hari-dev-821.html)
            url_slug = create_slug(name)
            file_path = f"users/{url_slug}.html"
            
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(GITHUB_REPO_NAME)
            
            try:
                contents = repo.get_contents(file_path)
                repo.update_file(file_path, f"Update {name}", clean_html, contents.sha)
            except:
                repo.create_file(file_path, f"New Site {name}", clean_html)
                
            # --- STEP 3: SUCCESS ---
            live_link = f"{NETLIFY_DOMAIN}/{file_path}"
            status.update(label="🎉 PUBLISHED!", state="complete", expanded=False)
            
            st.balloons()
            st.success("WEBSITE IS LIVE!")
            st.markdown(f"### [👉 Click to View Website]({live_link})")
            st.caption("Note: If you see 'Page Not Found', wait 30 seconds for Netlify to finish building.")

        except Exception as e:
            st.error(f"Error: {e}")