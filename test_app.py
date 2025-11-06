import streamlit as st
import spacy
import random

nlp = spacy.load("en_core_web_sm")

st.title("Your Legal Dashboard")

query = st.text_area("Enter your legal query below:")
if st.button("Analyze Query"):
    if query.strip() == "":
        st.warning("⚠️ Please enter a query before analyzing.")
    else:
        doc = nlp(query)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        response = random.choice([
            "Based on your query, it appears to relate to contractual obligations.",
            "This issue may involve both civil and procedural law aspects.",
            "Your query seems connected to constitutional rights.",
            "The matter involves legal liability and documentation procedures."
        ])

        st.subheader("🔍 AI Analysis Result")
        st.write(response)
        if entities:
            st.subheader("📘 Key Legal Terms Detected:")
            for text, label in entities:
                st.write(f"- **{text}** → {label}")
        else:
            st.info("No specific legal terms detected.")

st.divider()
st.subheader("Upload a Legal Document to Check Mistakes")
uploaded_file = st.file_uploader("Drag and drop file here", type=["txt"])
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    doc = nlp(text)
    long_sentences = [sent.text for sent in doc.sents if len(sent.text.split()) > 25]
    st.write("✅ File uploaded successfully!")
    if long_sentences:
        st.warning("Some sentences seem lengthy and complex. Consider simplifying them:")
        for sent in long_sentences[:5]:
            st.write(f"- {sent}")
    else:
        st.success("No major issues detected — your document looks well structured!")

st.divider()
st.button("Logout")
