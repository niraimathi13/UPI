import streamlit as st
import fitz 
import pandas as pd
import google.generativeai as genai
st.set_page_config(page_title="Financial Statement Analyzer",layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.pexels.com/photos/6985045/pexels-photo-6985045.jpeg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;}
    </style>
    """,unsafe_allow_html=True)
st.markdown("""
    <style>
    [data-testid="stSidebar"] {background-color: #F0FFFF;}
    [data-testid="stSidebar"] * {color: DeepPink;}
    </style>
    """,unsafe_allow_html=True)
st.title("📊 Personal UPI Usage and Financial Analyzer using LLMs")
with st.sidebar:
    st.header("ℹ️ About this App")
    st.write("""
    This tool helps you analyze your financial transactions by uploading your Bank or UPI statements.
    It supports PDF, CSV, Excel, JSON, and TXT file formats.
    Powered by Google's Gemini LLM, it provides spending patterns, savings insights, risk detection, and more.""")
    st.markdown("---")
    st.header("🚀 Instructions")
    st.write("""
    1. Enter your **Google API Key** (from [AI Studio](https://aistudio.google.com)).
    2. Upload your statement file.
    3. Explore the grouped insights.""")
api_key=st.text_input("🔑 Enter your Google API Key:",type="password")
if api_key:
    genai.configure(api_key=api_key)
    model=genai.GenerativeModel("gemini-1.5-flash")  
    def extract_text_from_pdf(file):
        doc=fitz.open(stream=file.read(),filetype="pdf")
        text="".join(page.get_text("text") for page in doc)
        return text
    def extract_text_from_csv(file):
        df=pd.read_csv(file)
        return df.to_string(index=False)
    def extract_text_from_excel(file):
        df=pd.read_excel(file)
        return df.to_string(index=False)
    def extract_text_from_json(file):
        df=pd.read_json(file)
        return df.to_string(index=False)
    def extract_text_from_txt(file):
        return file.read().decode("utf-8")
    PROMPTS=[
        "Summarize the total income (credits) and total expenses (debits).",
        "Identify the top spending patterns and categories where most money is spent.",
        "Provide time-based spending trends (weekly or monthly).",
        "Give a category-wise spending summary (Food, Shopping, Bills, etc.).",
        "Identify wasteful or duplicate transactions.",
        "Suggest a monthly budget plan based on this statement.",
        "Give suggestions to reduce unnecessary spending.",
        "Provide 3 personalized financial advice tips based on this statement.",
        "Calculate the savings rate as a percentage of total income.",
        "List recurring payments such as subscriptions or EMI with frequency and amounts.",
        "Highlight any unusual transactions that don't match your normal spending habits.",
        "Compare current month spending with previous months and identify increases.",
        "Provide insights on cash flow management and maintaining liquidity.",
        "Identify potential areas for investment based on available savings.",
        "Give tips to manage debt and avoid overspending during festivals or sales.",
        "Assess how current spending affects long-term financial goals."]
    def ask_llm(prompt,text):
        query=f"Here is a financial statement:\n{text}\n\nQuestion: {prompt}"
        response=model.generate_content(query)
        return response.text.strip()
    uploaded_file=st.file_uploader("Upload your Bank/UPI Statement (PDF, CSV, Excel, JSON, TXT)",type=["pdf","csv","xlsx","xls","json","txt"])
    if uploaded_file:
        file_type=uploaded_file.type
        text_data=""
        if file_type=="application/pdf":
            text_data=extract_text_from_pdf(uploaded_file)
        elif file_type=="text/csv":
            text_data=extract_text_from_csv(uploaded_file)
        elif file_type in ["application/vnd.ms-excel","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            text_data=extract_text_from_excel(uploaded_file)
        elif file_type=="application/json":
            text_data=extract_text_from_json(uploaded_file)
        elif file_type=="text/plain":
            text_data=extract_text_from_txt(uploaded_file)
        if text_data:
            st.success("✅ File processed successfully!")
        else:
            st.error("⚠️ Could not extract text from file.")
            st.stop()
        st.subheader("🔎 Financial Insights & Recommendations (Gemini)")
        for i,p in enumerate(PROMPTS,start=1):
            with st.spinner(f"Analyzing: {p}"):
                answer=ask_llm(p,text_data)
            st.markdown(f"**{i}. {p}**")
            st.write(answer)
            st.markdown("---")