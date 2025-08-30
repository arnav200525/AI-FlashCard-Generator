from flask import Flask, render_template, request
import google.generativeai as genai
import pdfplumber

def extraction(pdf_name):
    with pdfplumber.open(pdf_name) as p:
        for page in p.pages:
            text = page.extract_text()
    return text

genai.configure(api_key=" YOUR-API-KEY ") 
model = genai.GenerativeModel(model_name="models/gemma-3-27b-it")

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def flash():
    f_output = []
    if request.method == "POST":
        pdf = request.files["pdffile"]
        n_cards = request.form["n_cards"]
        pdf_text = extraction(pdf)

        if n_cards == "":
            n_cards = 10

        prompt = f"""
            Generate {n_cards} flashcards (Q&A pairs) from the following text: {pdf_text}
    
            Strickly follow following format:
            Q: <question>
            A: <answer>

            Note : Don't give me any sentence before generating flashcards, generate directly.
            """
        response = model.generate_content(prompt)
        lines = response.text.split("\n")
        question = ""
        answer = ""
        for line in lines:
            if line.startswith("Q:"):
                question = line.replace("Q:", "")
            elif line.startswith("A:"):
                answer = line.replace("A:", "")
                if question and answer:
                    f_output.append({"q": question, "a": answer})
                    question = ""
                    answer = ""
    return render_template("index.html", flashcard = f_output)

app.run(debug=True)