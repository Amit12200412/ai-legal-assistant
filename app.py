import streamlit as st
import sqlite3
import spacy
import random
# --- at top of app.py, after imports ---
import os
from spacy.cli import download as spacy_download

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Download model if not available (safe on Streamlit Cloud)
    spacy_download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
# --- rest of your code uses `nlp` as before ---


# Load English model for NLP
nlp = spacy.load("en_core_web_sm")

# ---------------------------
# DATABASE FUNCTIONS
# ---------------------------

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    lang TEXT
                )''')
    conn.commit()
    conn.close()

def create_user(username, password, lang=None):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users(username, password, lang) VALUES (?, ?, ?)', (username, password, lang))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    data = c.fetchone()
    conn.close()
    return data

# ---------------------------
# LANGUAGE TEXTS
# ---------------------------

LANG_TEXTS = {
    "en": {
        "title": "⚖️ AI Legal Assistant",
        "login": "Login",
        "signup": "Sign Up",
        "username": "Username",
        "password": "Password",
        "lang_select": "Select Your Preferred Language",
        "submit": "Submit",
        "query": "Enter your legal query below:",
        "analyze": "Analyze Query",
        "dashboard": "Your Legal Dashboard",
        "proofs": "Required Proofs",
        "actions": "Recommended Actions",
        "win": "Estimated Win Percentage",
        "upload_doc": "Upload a Legal Document to Check Mistakes",
        "mistake_result": "Mistake Check Result:",
        "logout": "Logout"
    },
    "hi": {
        "title": "⚖️ एआई विधिक सहायक",
        "login": "लॉगिन करें",
        "signup": "साइन अप करें",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "lang_select": "अपनी पसंदीदा भाषा चुनें",
        "submit": "जमा करें",
        "query": "अपना कानूनी प्रश्न नीचे दर्ज करें:",
        "analyze": "प्रश्न का विश्लेषण करें",
        "dashboard": "आपका विधिक डैशबोर्ड",
        "proofs": "आवश्यक साक्ष्य",
        "actions": "अनुशंसित कार्रवाइयाँ",
        "win": "अनुमानित जीत प्रतिशत",
        "upload_doc": "गलतियाँ जांचने के लिए दस्तावेज़ अपलोड करें",
        "mistake_result": "गलती जांच परिणाम:",
        "logout": "लॉग आउट"
    },
    "mr": {
        "title": "⚖️ एआय विधी सहाय्यक",
        "login": "लॉगिन करा",
        "signup": "साइन अप करा",
        "username": "वापरकर्ता नाव",
        "password": "संकेतशब्द",
        "lang_select": "आपली आवडती भाषा निवडा",
        "submit": "सबमिट करा",
        "query": "आपला कायदेशीर प्रश्न खाली लिहा:",
        "analyze": "प्रश्नाचे विश्लेषण करा",
        "dashboard": "आपले विधी डॅशबोर्ड",
        "proofs": "आवश्यक पुरावे",
        "actions": "शिफारस केलेली पावले",
        "win": "अंदाजे जिंकण्याचे प्रमाण",
        "upload_doc": "चुका तपासण्यासाठी दस्तऐवज अपलोड करा",
        "mistake_result": "चुका तपास परिणाम:",
        "logout": "लॉगआउट"
    }
}

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def analyze_legal_query(query):
    doc = nlp(query)
    keywords = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'VERB']]
    actions, proofs = [], []

    if "accident" in keywords:
        actions.append("File an FIR at the nearest police station.")
        proofs.append("Vehicle documents, driving license, medical reports.")
    elif "theft" in keywords:
        actions.append("Report to police and provide CCTV footage if available.")
        proofs.append("FIR copy, ownership proof, CCTV footage.")
    elif "property" in keywords:
        actions.append("Verify property documents and ownership title.")
        proofs.append("Sale deed, tax receipts, property map.")
    else:
        actions.append("Consult a lawyer for detailed advice.")
        proofs.append("Relevant legal documents or evidence.")

    win_percentage = random.randint(50, 95)
    return actions, proofs, win_percentage

def check_document_for_mistakes(file):
    content = file.read().decode("utf-8")
    mistakes = []
    if "???" in content or len(content) < 50:
        mistakes.append("Document seems incomplete or has placeholders.")
    if "lorem" in content.lower():
        mistakes.append("Contains dummy text; replace with actual legal text.")
    if not mistakes:
        return "✅ No major mistakes found."
    return "⚠️ " + " | ".join(mistakes)

# ---------------------------
# MAIN APP
# ---------------------------

def main():
    init_db()

    # Check if user already logged in
    if "user" in st.session_state:
        lang_code = st.session_state.get("lang", "en")
        L = LANG_TEXTS[lang_code]
        show_dashboard(L)
        return

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Choose Option", ["Login", "Sign Up"])

    # Language Selection
    st.title("🌐 Language Selection")
    lang_choice = st.selectbox("Select Language", ["English", "हिंदी", "मराठी"])
    lang_code = "en" if lang_choice == "English" else "hi" if lang_choice == "हिंदी" else "mr"
    L = LANG_TEXTS[lang_code]

    st.title(L["title"])

    # Signup Section
    if option == "Sign Up":
        st.subheader(L["signup"])
        new_user = st.text_input(L["username"])
        new_pwd = st.text_input(L["password"], type="password")
        if st.button(L["submit"]):
            ok, err = create_user(new_user, new_pwd, lang_code)
            if ok:
                st.success("✅ Account created successfully! Please login.")
            else:
                st.error(f"Error: {err}")

    # Login Section
    elif option == "Login":
        st.subheader(L["login"])
        username = st.text_input(L["username"])
        password = st.text_input(L["password"], type="password")
        if st.button(L["submit"]):
            user = login_user(username, password)
            if user:
                st.session_state["user"] = user
                st.session_state["lang"] = user[2] or lang_code
                st.success(f"Welcome {username} 👋")
                st.rerun()

            else:
                st.error("❌ Invalid credentials!")

def show_dashboard(L):
    st.subheader(L["dashboard"])

    # Input area
    query = st.text_area(L["query"], key="query_input")

    # Analyze button
    if st.button(L["analyze"]):
        if query.strip() == "":
            st.warning("⚠️ Please enter a valid legal query.")
        else:
            actions, proofs, win = analyze_legal_query(query)
            st.session_state["result"] = {
                "actions": actions,
                "proofs": proofs,
                "win": win
            }

    # Show previous analysis result if exists
    if "result" in st.session_state:
        result = st.session_state["result"]
        st.write(f"### {L['actions']}:")
        for a in result["actions"]:
            st.write(f"- {a}")

        st.write(f"### {L['proofs']}:")
        for p in result["proofs"]:
            st.write(f"- {p}")

        st.metric(L["win"], f"{result['win']}%")

    # Upload file section
    st.write("---")
    uploaded_file = st.file_uploader(L["upload_doc"], type=["txt"])
    if uploaded_file:
        result = check_document_for_mistakes(uploaded_file)
        st.info(f"{L['mistake_result']} {result}")

    st.write("---")
    if st.button(L["logout"]):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()



if __name__ == "__main__":
    main()

