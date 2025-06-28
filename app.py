import streamlit as st
import json
import requests
import os
import fitz  # PyMuPDF

# Set page config at the top
st.set_page_config(page_title="Smart Insurance App", layout="wide")

# Routing
page = st.query_params.get("page", "main")

# Load data
@st.cache_resource
def load_insurance_data():
    with open("insurance_data.json", "r") as f:
        return json.load(f)

insurance_data = load_insurance_data()

# OpenRouter API key (you can use os.getenv for production)
OPENROUTER_API_KEY = "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"


# GenAI helper
def ask_ai(user_question, document_text=None):
    insurance_keywords = ["insurance", "policy", "premium", "claim", "coverage", "term", "retirement", "health", "life"]
    if not any(k in user_question.lower() for k in insurance_keywords):
        return "⚠️ Please ask insurance-related questions only."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    context = f"The following is an insurance document:\n\n{document_text}\n\n" if document_text else ""
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful insurance assistant."},
            {"role": "user", "content": f"{context}Question: {user_question}"}
        ]
    }

    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else f"Error: {res.status_code}"

# Recommendation logic
def recommend_plan_expanded(age, income, occupation, health_condition, marital_status, dependents, risk_appetite):
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

    risk_map = {
        "low": ["term", "endowment", "whole life"],
        "medium": ["health", "retirement", "critical illness"],
        "high": ["ulip", "investment-linked"]
    }

    preferred_types = set(occupation_map.get(occupation, []))
    preferred_types.update(risk_map.get(risk_appetite.lower(), []))

    if "Diabetes" in health_condition or "Heart Disease" in health_condition or "Cancer" in health_condition:
        preferred_types.add("critical illness")
    if dependents > 0:
        preferred_types.add("family floater")
    if marital_status in ["Married", "Widowed"]:
        preferred_types.add("term with spouse add-on")

    for plan in insurance_data:
        if (
            plan["age_range"][0] <= age <= plan["age_range"][1]
            and plan["income_range"][0] <= income <= plan["income_range"][1]
            and any(pt in plan["type"].lower() for pt in preferred_types)
        ):
            matched_plans.append(plan)

    return matched_plans

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📋 Get Insurance Recommendation")

    occupation = st.selectbox("Occupation:", ["Student", "Farmer", "Business Owner", "Salaried Employee", "Freelancer", "Retired"], key="occupation_sidebar")
    age = st.number_input("Age:", min_value=18, max_value=100, step=1, key="age_sidebar")
    income = st.number_input("Annual Income (₹):", min_value=100000, max_value=5000000, step=10000, key="income_sidebar")
    health_condition = st.multiselect("Pre-existing Conditions:", ["None", "Diabetes", "Heart Disease", "Asthma", "Cancer"], key="health_sidebar")
    marital_status = st.selectbox("Marital Status:", ["Single", "Married", "Divorced", "Widowed"], key="marital_sidebar")
    dependents = st.slider("Number of Dependents:", 0, 5, 0, key="dependents_sidebar")
    risk_appetite = st.selectbox("Risk Preference:", ["Low", "Medium", "High"], key="risk_sidebar")

    if st.button("Get Recommendations", key="recommend_button"):
        results = recommend_plan_expanded(age, income, occupation, health_condition, marital_status, dependents, risk_appetite)
        if results:
            st.subheader("✅ Plans for You:")
            for plan in results:
                st.markdown(f"**{plan['type']}** — Coverage: {plan['coverage']}  \n*{plan['description']}*")
        else:
            st.warning("No matching plans found.")

    st.markdown("---")
    if st.button("🔍 Go to Fraud Detection & Claim Filling Guide", key="go_to_fraud"):
        st.query_params["page"] = "fraud"

# ---------------- Main Page ----------------
if page == "main":
    st.title("💡 Smart Insurance Advisor & Claim Helper")

    # Upload + summarize
    st.header("📂 Upload Insurance Document")
    uploaded_file = st.file_uploader("📄 Upload PDF or TXT", type=["pdf", "txt"])
    document_text = ""

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                for page in doc:
                    document_text += page.get_text()
        elif uploaded_file.type == "text/plain":
            document_text = uploaded_file.read().decode("utf-8")

        if st.button("🧠 Summarize Document"):
            with st.spinner("Summarizing..."):
                summary = ask_ai("Summarize this insurance document in simple terms", document_text)
            st.markdown("### 📌 Summary")
            st.markdown(summary)

    # FAQs
    st.markdown("---")
    st.markdown("### 📖 Frequently Asked Questions")

    with st.expander("1. What does this insurance document cover?"):
        st.write("Upload your document and click 'Summarize Document'.")

    with st.expander("2. How do I file a claim?"):
        st.write("Use the claim filing guide in the sidebar based on your policy type.")

    with st.expander("3. Can I ask questions?"):
        st.write("Yes! Ask insurance-related questions using the AI chat below.")

    # Chatbot
    st.header("💬 Ask Your Insurance Questions")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def handle_submit():
        question = st.session_state.user_input
        answer = ask_ai(question, document_text)
        st.session_state.chat_history.append({"question": question, "answer": answer})
        st.session_state.user_input = ""

    st.text_input("Ask a question:", key="user_input", on_change=handle_submit)

    if st.session_state.chat_history:
        st.markdown("### 🧾 Chat History")
        for chat in st.session_state.chat_history:
            with st.expander(f"🧑 You: {chat['question']}", expanded=True):
                st.markdown(f"**🤖 Assistant:** {chat['answer']}")

# ---------------- Fraud Detection Page ----------------
elif page == "fraud":
    st.title("🕵️ Insurance Fraud Detection")

    uploaded_fraud_file = st.file_uploader("📄 Upload Insurance Document for Fraud Check", type=["pdf", "txt"], key="fraud_upload")
    fraud_text = ""

    @st.cache_resource
    def load_model():
        import joblib
        model = joblib.load("fraud_model.pkl")
        vectorizer = joblib.load("vectorizer.pkl")
        return model, vectorizer

    model, vectorizer = load_model()

    if uploaded_fraud_file:
        if uploaded_fraud_file.type == "application/pdf":
            with fitz.open(stream=uploaded_fraud_file.read(), filetype="pdf") as doc:
                for page in doc:
                    fraud_text += page.get_text()
        elif uploaded_fraud_file.type == "text/plain":
            fraud_text = uploaded_fraud_file.read().decode("utf-8")

        if fraud_text and st.button("🔍 Detect Fraud"):
            with st.spinner("Analyzing document..."):
                vectorized = vectorizer.transform([fraud_text])
                prediction = model.predict(vectorized)[0]
                label = "🚨 Fraudulent Document Detected" if prediction == 1 else "✅ Legitimate Document"
                color = "red" if prediction == 1 else "green"
                st.markdown(f"<h3 style='color:{color}'>{label}</h3>", unsafe_allow_html=True)

                # Optional: Highlight suspicious words if fraudulent
                if prediction == 1 and hasattr(model, "coef_"):
                    top_words = []
                    try:
                        import numpy as np
                        coef = model.coef_[0]
                        top_indices = np.argsort(coef)[-10:]
                        top_words = [vectorizer.get_feature_names_out()[i] for i in top_indices]
                    except:
                        top_words = []

                    if top_words:
                        st.markdown("#### 🔍 Possible Suspicious Terms:")
                        highlighted = []
                        for word in top_words:
                            if word.lower() in fraud_text.lower():
                                highlighted.append(f"`{word}`")
                        if highlighted:
                            st.write("These words may have influenced the fraud detection:")
                            st.markdown(", ".join(highlighted))
                        else:
                            st.write("No top suspicious words found in the visible document.")

    # 📝 Claim Filing Guide Below
    # 📝 Claim Filing Guide Below
st.markdown("---")
st.header("📄 Claim Filing Guide")

claim_type = st.selectbox("Choose the insurance type to file a claim:", [
    "Health Insurance", "Term Insurance", "Retirement Plan", "Vehicle Insurance",
    "Travel Insurance", "Home Insurance", "Crop Insurance"
], key="claim_type_fraud")

claim_mode = st.radio("Claim Mode:", ["Cashless", "Reimbursement"], key="claim_mode_fraud")

if st.button("Get Claim Filing Steps", key="claim_button_fraud"):
    if claim_type == "Health Insurance":
        if claim_mode == "Cashless":
            steps = """
            1. Get admitted to a **network hospital** listed by your insurer.  
            2. Submit **pre-authorization form** at the hospital desk.  
            3. Hospital will coordinate with the **TPA (Third Party Administrator)**.  
            4. Once approved, **bills will be settled directly** with the hospital.  
            5. Keep all bills and discharge summary for future reference.

            🔗 [Example: ICICI Lombard Health Claim](https://www.icicilombard.com/health-insurance/claims)  
            📄 [Claim Form (PDF)](https://www.icicilombard.com/docs/default-source/claim-forms/health-claim-form.pdf)  
            ☎️ **Helpline:** 1800 2666
            """
        else:
            steps = """
            1. Pay all hospital bills upfront.  
            2. Collect **original bills**, **prescriptions**, and **discharge summary**.  
            3. Download and fill the **health reimbursement form**.  
            4. Submit the form and documents via courier/email to the insurer.  
            5. Track the claim via email or portal.

            🔗 [HDFC ERGO Health Reimbursement Guide](https://www.hdfcergo.com/claims/health-insurance-claims)  
            📄 [Claim Form (PDF)](https://www.hdfcergo.com/documents/20121/273982/Health+Claim+Form.pdf)  
            ☎️ **Helpline:** 022 6234 6234
            """

    elif claim_type == "Term Insurance":
        steps = """
        1. Notify the insurer about the death of the policyholder.  
        2. Submit the **original death certificate**, **policy document**, **nominee ID proof**, and **medical records** (if applicable).  
        3. Download and fill the death claim form.  
        4. Submit documents online or through a branch.  
        5. Wait for verification and fund release.

        🔗 [HDFC Life Term Claim](https://www.hdfclife.com/customer-service/claims)  
        📄 [Death Claim Form (PDF)](https://www.hdfclife.com/content/dam/hdfclifeinsurancecompany/customer-service/download-claim-forms/individual-claims/forms/death-claim-form.pdf)  
        ☎️ **Helpline:** 1860 267 9999
        """

    elif claim_type == "Retirement Plan":
        steps = """
        1. Download and fill the **pension claim form** or maturity request form.  
        2. Submit **policy documents**, **KYC**, **bank account proof**, and **annuity preference**.  
        3. Receive pension in your selected mode (monthly/quarterly/lump sum).  
        4. Optionally link Aadhaar for faster processing.

        📄 Check with your pension provider (LIC, HDFC, SBI, etc.)  
        ☎️ Call the respective helpline for plan-specific steps.
        """

    elif claim_type == "Vehicle Insurance":
        steps = """
        1. Report the incident to your insurer within 24–48 hours.  
        2. File an **FIR** for theft or third-party damage (if applicable).  
        3. Submit **driving license**, **vehicle RC**, **photos of damage**, and **claim form**.  
        4. Surveyor will inspect your vehicle.  
        5. Post-approval, repair bills will be settled or reimbursed.

        🔗 [Bajaj Allianz Motor Claim Process](https://www.bajajallianz.com/claim-assistance/motor-insurance-claim-process.html)  
        📄 [Motor Claim Form (PDF)](https://www.bajajallianz.com/content/dam/bagic/pdf/motor-insurance/motor-claim-form.pdf)  
        ☎️ **Helpline:** 1800 209 5858
        """

    elif claim_type == "Travel Insurance":
        steps = """
        1. Notify insurer immediately after the incident (loss, medical emergency, etc.).  
        2. Submit **boarding pass**, **passport**, **ticket copy**, and **bills/invoices**.  
        3. Fill the **travel claim form** with supporting documents.  
        4. Report baggage loss or theft to airport/authorities for documentation.  
        5. Track claim status online.

        📄 Check your insurer's travel claim page (e.g., Tata AIG, Bajaj Allianz, HDFC ERGO)  
        ☎️ International helplines available on each insurer’s site.
        """

    elif claim_type == "Home Insurance":
        steps = """
        1. Notify insurer about any damage (fire, theft, flood, etc.).  
        2. File an **FIR** in case of burglary or fire report for accidental damage.  
        3. Submit **photos**, **repair estimates**, and **property ownership proof**.  
        4. Surveyor will assess on-site.  
        5. Claim settled based on policy terms.

        🔗 [New India Assurance Home Claim](https://newindia.co.in/portal/claims)  
        ☎️ **Helpline:** 1800 209 1415
        """

    elif claim_type == "Crop Insurance":
        steps = """
        1. Inform your insurer or agriculture officer within 72 hours of crop loss.  
        2. Submit your **land ownership proof**, **sowing declaration**, and **crop loss report**.  
        3. Government-appointed surveyor will inspect fields (sometimes via drone).  
        4. Claim amount is credited directly to the farmer's bank account.

        🔗 [PMFBY (Crop Insurance) Portal](https://pmfby.gov.in/)  
        ☎️ **Toll-Free Farmer Helpline:** 1800 180 1551
        """

    st.markdown("### 📋 Claim Filing Steps")
    st.markdown(steps)

st.markdown("---")  # Clear markdown block before showing the button


if st.button("⬅️ Back to Advisor", key="back_button"):
    st.query_params["page"] = "main"

