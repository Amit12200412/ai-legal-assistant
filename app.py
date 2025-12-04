# app.py
import streamlit as st
import sqlite3
import hashlib
import spacy
import random
from datetime import datetime
from fpdf import FPDF
import io
import base64
import json

# -----------------------------
# Config / Constants
# -----------------------------
DB_PATH = "users.db"
SPACY_MODEL = "en_core_web_sm"

# -----------------------------
# JSON Safe Loader (ADDED)
# -----------------------------
def safe_json_loads(text):
    """Prevents JSON crashes from invalid DB entries."""
    if not text or (isinstance(text, str) and text.strip() == ""):
        return []
    try:
        return json.loads(text)
    except Exception:
        return text  # return original string if invalid JSON

# -----------------------------
# Load NLP
# -----------------------------
nlp = spacy.load(SPACY_MODEL)

# -----------------------------
# Multi-language texts (EN/HI/MR)
# -----------------------------
LANG_TEXTS = {
    "en": {
        "app_title": "⚖️ AI Legal Assistant",
        "login": "Login",
        "signup": "Sign Up",
        "username": "Username",
        "password": "Password",
        "create_account": "Create Account",
        "submit": "Submit",
        "logout": "Logout",
        "nav_menu": "Navigation",
        "legal_query": "Enter your legal query",
        "analyze": "Analyze",
        "generate_doc": "Generate Document",
        "doc_type": "Document Type",
        "name": "Your Name",
        "address": "Your Address",
        "mobile": "Mobile Number",
        "against": "Against Whom (Name / Company)",
        "details": "Incident Details (editable)",
        "download_pdf": "Download PDF",
        "history": "History",
        "upload_doc": "Upload a TXT Document",
        "check_doc": "Check Document",
        "chatbot": "Chatbot",
        "suggestions": "Query Suggestions",
        "category": "Category",
        "filter_suggestions": "Filter suggestions",
        "dark_mode": "Dark Mode",
        "language": "Language"
    },
    "hi": {
        "app_title": "⚖️ एआई विधिक सहायक",
        "login": "लॉगिन",
        "signup": "साइन अप",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "create_account": "खाता बनाएँ",
        "submit": "जमा करें",
        "logout": "लॉग आउट",
        "nav_menu": "नेविगेशन",
        "legal_query": "अपना कानूनी प्रश्न दर्ज करें",
        "analyze": "विश्लेषण करें",
        "generate_doc": "दस्तावेज़ बनाएँ",
        "doc_type": "दस्तावेज़ प्रकार",
        "name": "आपका नाम",
        "address": "आपका पता",
        "mobile": "मोबाइल नंबर",
        "against": "जिसके खिलाफ (नाम / कंपनी)",
        "details": "घटना का विवरण (संपादन योग्य)",
        "download_pdf": "PDF डाउनलोड करें",
        "history": "इतिहास",
        "upload_doc": "TXT दस्तावेज़ अपलोड करें",
        "check_doc": "दस्तावेज़ जांचें",
        "chatbot": "चैटबॉट",
        "suggestions": "प्रश्न सुझाव",
        "category": "श्रेणी",
        "filter_suggestions": "सुझाव फ़िल्टर करें",
        "dark_mode": "डार्क मोड",
        "language": "भाषा"
    },
    "mr": {
        "app_title": "⚖️ एआय विधी सहाय्यक",
        "login": "⚖️ एआई विधिक सहाय्यक",
        "signup": "साइन अप",
        "username": "वापरकर्ता नाव",
        "password": "पासवर्ड",
        "create_account": "खाते तयार करा",
        "submit": "सबमिट करा",
        "logout": "लॉगआउट",
        "nav_menu": "नेव्हिगेशन",
        "legal_query": "आपला कायदेशीर प्रश्न लिहा",
        "analyze": "विश्लेषण करा",
        "generate_doc": "दस्तऐवज तयार करा",
        "doc_type": "दस्तऐवज प्रकार",
        "name": "आपले नाव",
        "address": "आपला पत्ता",
        "mobile": "मोबाईल क्रमांक",
        "against": "ज्यांच्याविरुद्ध (नाव / कंपनी)",
        "details": "घटनेचे तपशील (संपादन करण्यायोग्य)",
        "download_pdf": "PDF डाउनलोड करा",
        "history": "इतिहास",
        "upload_doc": "TXT दस्तऐवज अपलोड करा",
        "check_doc": "दस्तऐवज तपासा",
        "chatbot": "चॅटबॉट",
        "suggestions": "प्रश्न सूचना",
        "category": "वर्ग",
        "filter_suggestions": "सूचना फिल्टर करा",
        "dark_mode": "डार्क मोड",
        "language": "भाषा"
    }
}

# -----------------------------
# IPC mapping for detection
# -----------------------------
IPC_SECTIONS = {
    "theft": ("IPC 378", "Theft — punishment may extend to 3 years and/or fine."),
    "murder": ("IPC 302", "Murder — punishment may include life imprisonment or death."),
    "fraud": ("IPC 420", "Cheating and dishonesty."),
    "accident": ("IPC 279", "Rash driving or negligent conduct causing danger."),
    "assault": ("IPC 351", "Assault or criminal force."),
    "rape": ("IPC 376", "Rape — severe sexual offence."),
    "property": ("Civil Property Matter", "Disputes related to property, title and ownership.")
}

# -----------------------------
# Utilities: DB initialization
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # users
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            lang TEXT
        )
        """
    )
    # history (queries)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            query TEXT,
            actions TEXT,
            proofs TEXT,
            win INTEGER,
            ipc TEXT,
            ts TEXT
        )
        """
    )
    # pdf storage (filename, bytes, metadata)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            filename TEXT,
            file blob,
            doc_type TEXT,
            created_at TEXT
        )
        """
    )
    # chatbot logs (optional)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            message TEXT,
            ts TEXT
        )
        """
    )
    conn.commit()
    conn.close()

# -----------------------------
# Auth helpers
# -----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str, lang: str = "en"):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password, lang) VALUES (?, ?, ?)",
                  (username, hash_password(password), lang))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def login_user(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, lang FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    row = c.fetchone()
    conn.close()
    return row

# -----------------------------
# Persisting helpers
# -----------------------------
def save_history(username, query, actions, proofs, win, ipc):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # ensure we store JSON strings for lists
    try:
        actions_json = json.dumps(actions)
    except:
        actions_json = json.dumps([str(actions)])
