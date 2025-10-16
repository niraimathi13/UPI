import os
import streamlit as st
import PyPDF2
import google.generativeai as genai
import re
import json
st.set_page_config(page_title="Personal Finance Assistant",page_icon="",layout="wide")
st.markdown("""
<style>
body, .main {
    background: linear-gradient(115deg, #F9F871 0%, #CFDEF3 40%, #A1C4FD 100%);
}
.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #fff;
    background: linear-gradient(90deg, #ee098a 0%, #ffc837 35%, #43e97b 85%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 8px 0 2px 0;
    text-shadow: 0px 2px 15px #38f9d740;
}
.sub-title {
    text-align: center;
    font-size: 25px;
    font-weight: 500;
    color: #444;
    margin-bottom: 18px;
    background: linear-gradient(90deg, #ffaf85 0%, #ffc837 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-bottom: 8px;
}
.stButton button {
    background: linear-gradient(90deg,#43e97b 0%,#38f9d7 51%,#ffaf85 100%);
    color: #fff;
    font-size: 23px;
    font-weight: 700;
    padding: 16px 42px;
    border-radius: 14px;
    border: none;
    box-shadow: 0px 10px 28px #ee098a25;
    transition: .15s;
}
.stButton button:hover {
    background: linear-gradient(90deg,#ffc837 0%,#ee098a 100%);
    box-shadow: 0px 4px 20px #ffc83790;
    filter: brightness(1.07);
    scale: 1.11;
}
.result-card {
    background: linear-gradient(101deg, #e3ffe7 0%, #d9e7ff 84%);
    border-radius: 21px;
    padding: 25px 27px;
    margin: 23px 0;
    box-shadow: 0 7px 27px 0 #ffb6b9aa;
    border: 2px solid #f6ffc9;
    backdrop-filter: blur(7px);
    animation: fadein 0.8s;
    font-size: 20px;
    color: #213;
}
.success-banner {
    background: linear-gradient(92deg, #43e97b 0%, #38f9d7 60%, #ffc837 100%);
    color: #222;
    padding: 19px 20px;
    border-radius: 20px;
    text-align: center;
    font-size: 27px;
    font-weight: bold;
    letter-spacing: 1.5px;
    margin-top: 18px;
    margin-bottom: 13px;
    box-shadow: 0px 8px 32px #43e97b70;
    animation: popin 0.4s;
}
@keyframes fadein {
  0% { opacity: 0; transform: translateY(12px);}
  80% { opacity: .96; }
  100% { opacity: 1; transform: translateY(0);}
}
@keyframes popin {
  0% { opacity: 0; scale: .7;}
  100% { opacity: 1; scale: 1;}
}
.stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: #ee098a;
    text-shadow: 0 2px 8px #ffc83766;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, #ee098a 0%, #43e97b 100%);
}
/* Fireworks */
.fireworks {
  position: fixed;
  left: 50%;
  bottom: 0;
  width: 5px;
  height: 20px;
  background: transparent;
  border-radius: 50%;
  box-shadow:
      0px 0px 10px 5px #ff0,
      4px -8px 10px 3px #f00,
      -6px -5px 10px 3px #0ff,
      7px -3px 10px 5px #0f0,
      -8px -10px 10px 5px #00f;
  animation: explode 2s ease-out infinite;
}
@keyframes explode {
  0% { transform: translateY(0px) scale(0.3); opacity: 1; }
  40% { transform: translateY(-250px) scale(1.1); opacity: 0.8; }
  70% { transform: translateY(-340px) scale(1.3); opacity: 0.6; }
  100% { transform: translateY(-400px) scale(0.5); opacity: 0; }
}
/* Confetti */
.confetti-piece {
  position: absolute;
  top: 0;
  width: 10px;
  height: 25px;
  background-color: hsl(calc(var(--i) * 20), 100%, 50%);
  animation: fall 2.5s linear infinite;
}
@keyframes fall {
  0% { transform: translateY(0px) rotate(0deg); opacity: 1;}
  100% { transform: translateY(600px) rotate(360deg); opacity: 0;}
}
.confetti {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1000;
}
</style>
""",unsafe_allow_html=True)
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)
with st.sidebar:
    st.header("ℹ️ About this App")
    st.write("""
    This tool helps you analyze your financial transactions by uploading your Bank or UPI statements.
    Powered by Google's Gemini LLM, it provides spending patterns, savings insights, risk detection, and more.""")
    st.markdown("---")
    st.header("🚀 Instructions")
    st.write("""
    1. Upload your statement file.
    2. Explore the grouped insights.""")
st.markdown('<h1 class="main-title"> Personal Finance Assistant</h1>',unsafe_allow_html=True)
uploaded_file=st.file_uploader("Upload PDF File",type=["pdf"],help="Only PDF files are supported")
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()
def extract_json_answers(response_text):
    try:
        data=json.loads(response_text)
        if isinstance(data,list) and len(data)==16:
            return data
    except:
        pass
    match=re.search(r"``````", response_text)
    if match:
        try:
            data=json.loads(match.group(1))
            if isinstance(data,list) and len(data)==16:
                return data
        except:
            pass
    match=re.search(r"(\[[\s\S]*?\])",response_text)
    if match:
        try:
            data=json.loads(match.group(1))
            if isinstance(data,list) and len(data)==16:
                return data
        except:
            pass
    return None
def analyze_financial_data(text):
    questions=[
        "Summarize the total income (credits) and total expenses (debits).",
        "Identify the top spending patterns and categories where most money is spent.",
        "Provide time-based spending trends (weekly or monthly).",
        "Give a category-wise summary (Food, Shopping, Bills, etc.).",
        "Identify wasteful or duplicate transactions.",
        "Suggest a monthly budget plan based on the statement.",
        "Give suggestions to reduce unnecessary spending.",
        "Provide 3 personalized tips.",
        "Calculate the savings rate as a percentage of total income.",
        "List recurring payments like subscriptions or EMI with frequency and amounts.",
        "Highlight unusual transactions.",
        "Compare current month spending with previous months.",
        "Provide insights on cash flow and liquidity.",
        "Suggest investment opportunities.",
        "Give tips on debt management and avoiding overspending during festivals.",
        "Assess how current spending affects long-term goals."
    ]
    model=genai.GenerativeModel("gemini-2.0-flash")
    prompt=(
        "Analyze the following Paytm transaction history and answer these 16 questions each in one concise paragraph:\n"
        + "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)]) +
        "\n---\nRespond ONLY as a JSON array of 16 answer strings, one for each question, nothing else.\n\n"
        "Paytm Transaction History:\n" + text
    )
    response=model.generate_content(prompt)
    return response.text if response else "Error processing financial data."
if uploaded_file is not None:
    file_path=f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("File uploaded successfully!")
    with st.spinner("Extracting text from the document..."):
        extracted_text=extract_text_from_pdf(file_path)
    if not extracted_text:
        st.error("Failed to extract text. Ensure the document is not a scanned image PDF.")
    else:
        progress_bar=st.progress(0)
        with st.spinner("AI is analyzing your financial data..."):
            response_text=analyze_financial_data(extracted_text)
        progress_bar.progress(100)
        st.subheader("Financial Insights Report")
        st.markdown(f'<div class="result-card"><b>Financial Report for {uploaded_file.name}</b></div>',unsafe_allow_html=True)
        answers=extract_json_answers(response_text)
        questions=[
            "Summarize the total income (credits) and total expenses (debits).",
            "Identify the top spending patterns and categories where most money is spent.",
            "Provide time-based spending trends (weekly or monthly).",
            "Give a category-wise summary (Food, Shopping, Bills, etc.).",
            "Identify wasteful or duplicate transactions.",
            "Suggest a monthly budget plan based on the statement.",
            "Give suggestions to reduce unnecessary spending.",
            "Provide 3 personalized tips.",
            "Calculate the savings rate as a percentage of total income.",
            "List recurring payments like subscriptions or EMI with frequency and amounts.",
            "Highlight unusual transactions.",
            "Compare current month spending with previous months.",
            "Provide insights on cash flow and liquidity.",
            "Suggest investment opportunities.",
            "Give tips on debt management and avoiding overspending during festivals.",
            "Assess how current spending affects long-term goals."
        ]
        if answers:
            for idx, (q, ans) in enumerate(zip(questions,answers),1):
                st.markdown(f"**{idx}. {q}**")
                st.write(ans)
            st.markdown('<div class="success-banner">🔥 Analysis Completed! Plan your finances wisely. </div>',unsafe_allow_html=True)
            st.balloons()
            st.markdown("""
            <div class="fireworks"></div>
            <div class="fireworks"></div>
            <div class="fireworks"></div>
            """,unsafe_allow_html=True)
            st.markdown("""
            <div class="confetti">
              """ + "".join([f"<div class='confetti-piece' style='--i:{i}; left:{i*5}%; animation-delay:{i*0.3}s; background-color:hsl({i*18}, 100%, 60%);'></div>" for i in range(20)]) + """
            </div>
            """,unsafe_allow_html=True)
        else:
            st.error("Could not extract valid JSON answers from AI response. Showing raw output:")
            st.write(response_text)

    os.remove(file_path)
