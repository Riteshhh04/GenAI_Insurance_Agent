# 🛡️ Smart Insurance Advisor, Claim Helper & Fraud Detector

An intelligent Streamlit-based web application that helps users:
- Get **insurance policy recommendations** based on personal details.
- **Understand and summarize** insurance documents using AI.
- Get **claim filing guidance** for common insurance types.
- **Detect fraud** in insurance documents using a machine learning model.

---

## 🔍 Features

| Module | Description |
|--------|-------------|
| 📝 Policy Recommender | Suggests policies based on age, income, and occupation. |
| 🧠 AI Chatbot | Answers user questions using OpenRouter's AI model. |
| 📄 Document Summarization | Summarizes PDF/TXT insurance documents in simple language. |
| 📋 Claim Filing Guide | Step-by-step claim process for health, term, and retirement plans. |
| 🕵️ Fraud Detection | ML model detects fraudulent insurance documents. |

---

## ⚙️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Integration**: [OpenRouter API](https://openrouter.ai/)
🔹 Using `mistralai/mistral-7b-instruct` model for summarization and Q&A
- **ML Model**: Scikit-learn (`RandomForestClassifier`)
- **PDF Parsing**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **Vectorization**: `TfidfVectorizer`

---

## 📁 Project Structure

```
├── app.py                      # Main Streamlit app
├── train_fraud_detector.py    # Script to train fraud detection model
├── insurance_data.json        # Sample insurance plan data
├── fraud_model.pkl            # Trained ML model (binary classification)
├── vectorizer.pkl             # TF-IDF vectorizer
├── fraud_insurance_data_100.csv # Dataset used for fraud model
└── README.md
```

---
🚀 **Live Demo**  
Check out the deployed app here: [Smart Insurance Advisor (Streamlit)](https://d2fdubtwe5uzkphxaukzsz.streamlit.app/)

---

## 🛠️ Setup Guide

### 1. Clone the Repository

```bash
gh repo clone Riteshhh04/GenAI_Insurance_Agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install manually:

```bash
pip install streamlit pandas scikit-learn joblib requests PyMuPDF
```

### 4. Set Environment Variable for OpenRouter

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Or create a `.env` file:

```
OPENROUTER_API_KEY=your_api_key_here
```

Use `python-dotenv` to load `.env` if needed.

### 5. Run the Application

```bash
streamlit run app.py
```

---

## 📊 Training the Fraud Detection Model

To retrain the ML model:

```bash
python train_fraud_detector.py
```

This will:
- Load `fraud_insurance_data_100.csv`
- Train a `RandomForestClassifier`
- Vectorize text using `TfidfVectorizer`
- Save `fraud_model.pkl` and `vectorizer.pkl`

---

## 📌 Notes

- API key is required for AI features like summarization and chat.
- Documents are parsed locally or passed to AI depending on the feature.
- Fraud detection model is for prototype use. For production, consider:
  - Larger datasets
  - Advanced NLP models (e.g., BERT)
  - Regulatory/legal disclaimers

---


## 👨‍💻 Author

**Ritesh Zambare**  
Connect with me on [LinkedIn](https://www.linkedin.com/in/ritesh-zambare-0265032b0/)  
