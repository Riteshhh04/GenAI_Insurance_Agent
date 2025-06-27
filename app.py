import streamlit as st
import json
import requests
import os
import fitz  # PyMuPDF
import html

OPENROUTER_API_KEY = "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"

# Load insurance data
def load_insurance_data():
    with open("insurance_data.json", "r") as f:
        return json.load(f)

insurance_data = load_insurance_data()

# Recommend plans based on age, income, and occupation
def recommend_plan(age, income, occupation):
    occupation = occupation.lower()
    matched_plans = []

    occupation_map = {
        "student": ["child education", "health", "travel"],
        "farmer": ["crop", "health", "personal accident"],
        "business owner": ["ulip", "fire", "marine", "group"],
        "salaried employee": ["term", "health", "retirement", "critical illness"],
        "freelancer": ["personal accident", "health", "term"],
        "retired": ["retirement", "health", "whole life"]
    }

    preferred_types = occupation_map.get(occupation, [])

    for plan in insurance_data:
        if (
            plan["age_range"][0] <= age <= plan["age_range"][1]
            and plan["income_range"][0] <= income <= plan["income_range"][1]
            and any(pt in plan["type"].lower() for pt in preferred_types)
        ):
            matched_plans.append(plan)

    return matched_plans

# Ask AI helper
def ask_ai(user_question, document_text=None):
    insurance_keywords = ["insurance", "policy", "premium", "claim", "coverage", "term", "retirement", "health", "life"]

    if not any(keyword in user_question.lower() for keyword in insurance_keywords):
        return "⚠️ You can only ask questions related to **insurance**, such as policies, claims, premiums, etc."

    prompt_context = f"The following is an insurance document:\n\n{document_text}\n\n" if document_text else ""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful insurance assistant."},
            {"role": "user", "content": f"{prompt_context}Question: {user_question}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Error: {response.status_code} — {response.text}"

# ───────────── Streamlit UI ─────────────
st.set_page_config(page_title="Smart Insurance Helper", layout="wide")
st.title("💡 Smart Insurance Advisor, Claim Helper & Fraud Detector")

# ───────────── Sidebar: Recommendation ─────────────
with st.sidebar:
    st.header("📋 Get Policy Recommendation")

    occupation = st.selectbox("Select your occupation:", [
        "Student", "Farmer", "Business Owner", "Salaried Employee", "Freelancer", "Retired"
    ])
    age = st.number_input("Enter your age:", min_value=18, max_value=100)
    income = st.number_input("Annual Income (₹):", min_value=100000, max_value=5000000)

    if st.button("Get Recommendations"):
        recommendations = recommend_plan(age, income, occupation)
        if recommendations:
            st.subheader("✅ Recommended Plans for You:")
            for plan in recommendations:
                st.markdown(f"**{plan['type']}** — Coverage: {plan['coverage']}  \n*{plan['description']}*")
        else:
            st.warning("Sorry, no matching plans found. Try adjusting your inputs.")

    st.markdown("---")
    st.header("📄 Claim Filing Guide")

    claim_type = st.selectbox("Choose the insurance type to file a claim:", ["Health Insurance", "Term Insurance", "Retirement Plan"])
    if st.button("Get Claim Filing Steps"):
        if claim_type == "Health Insurance":
            claim_steps = """
            1. Collect your **policy number** and **insurance card**.  
            2. Submit **hospital bills**, **doctor prescriptions**, and **medical reports**.  
            3. Fill out the **claim form** from the insurance website or hospital.  
            4. Submit documents online or via your insurance agent.  
            5. Keep track of your claim status through SMS or email updates.
            """
        elif claim_type == "Term Insurance":
            claim_steps = """
            1. Obtain the **death certificate** of the policyholder.  
            2. Submit **policy document**, **ID proof**, and **death certificate**.  
            3. Fill out the **claim form**.  
            4. Wait for verification and fund transfer.
            """
        elif claim_type == "Retirement Plan":
            claim_steps = """
            1. Submit your **policy number** and **KYC documents**.  
            2. Request for **maturity benefits** from the insurer.  
            3. Provide **bank details** to receive pension funds.  
            4. Choose annuity type (monthly, quarterly, etc.).
            """
        st.markdown(claim_steps)

# ───────────── Main Section: File Upload & Summary ─────────────
st.header("📂 Upload Insurance Document")
uploaded_file = st.file_uploader("📄 Upload insurance document (PDF or TXT)", type=["pdf", "txt"])
document_text = ""
summarized_text = ""

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                document_text += page.get_text()
    elif uploaded_file.type == "text/plain":
        document_text = uploaded_file.read().decode("utf-8")

    if st.button("🧠 Summarize Document"):
        with st.spinner("Generating summary..."):
            summarized_text = ask_ai("Summarize this insurance document in simple terms", document_text)
        st.markdown("### 📌 Document Summary")
        st.markdown(summarized_text)

# ───────────── FAQs Before Chat ─────────────
st.markdown("---")
st.markdown("### 📖 Frequently Asked Questions (FAQs)")

with st.expander("1. What does this insurance document cover?"):
    st.write("You can upload the document and click 'Summarize Document' to get a simple explanation.")

with st.expander("2. How do I file a claim based on this document?"):
    st.write("Use the Claim Filing Guide in the sidebar based on your insurance type.")

with st.expander("3. Can I get help with understanding specific terms?"):
    st.write("Yes! Ask any insurance-related question in the chat below.")

# ───────────── Chat Section ─────────────
st.header("💬 Ask Your Insurance Questions")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

def handle_submit():
    user_question = st.session_state.user_input
    answer = ask_ai(user_question, document_text)
    st.session_state.chat_history.append({"question": user_question, "answer": answer})
    st.session_state.user_input = ""

user_question = st.text_input("Ask me anything about insurance:", key="user_input", on_change=handle_submit)

# Show chat history
if st.session_state.chat_history:
    st.markdown("### 🧾 Chat History")
    for chat in st.session_state.chat_history:
        with st.expander(f"🧑 You: {chat['question']}", expanded=True):
            st.markdown(f"**🤖 Assistant:**\n{chat['answer']}")

# ───────────── Fraud Detection Section ─────────────
st.markdown("---")
st.header("🕵️‍♀️ Insurance Fraud Detection")

uploaded_fraud_file = st.file_uploader("📄 Upload Insurance Document for Fraud Check", type=["pdf", "txt"], key="fraud_upload")
fraud_text = ""

# Load your model and vectorizer only once
@st.cache_resource
def load_model():
    import joblib
    model = joblib.load("fraud_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

model, vectorizer = load_model()

# Process the uploaded document
if uploaded_fraud_file:
    if uploaded_fraud_file.type == "application/pdf":
        with fitz.open(stream=uploaded_fraud_file.read(), filetype="pdf") as doc:
            for page in doc:
                fraud_text += page.get_text()
    elif uploaded_fraud_file.type == "text/plain":
        fraud_text = uploaded_fraud_file.read().decode("utf-8")

    if fraud_text:
        if st.button("🔍 Detect Fraud"):
            with st.spinner("Analyzing document..."):
                vectorized = vectorizer.transform([fraud_text])
                prediction = model.predict(vectorized)[0]
                label = "🚨 Fraudulent Document Detected" if prediction == 1 else "✅ Legitimate Document"
                color = "red" if prediction == 1 else "green"
                st.markdown(f"<h3 style='color:{color}'>{label}</h3>", unsafe_allow_html=True)
