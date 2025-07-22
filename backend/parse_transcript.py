# parse_transcript.py

import os
import json
import csv
from pathlib import Path
from dotenv import load_dotenv
from rapidfuzz import fuzz, process
from openai import OpenAI

# ========================
# 🔐 Load API Key
# ========================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========================
# 📋 Predefined Questions
# ========================
PREDEFINED_QUESTIONS = [
    "What is your full name as per Aadhar?",
    "What is your date of birth?",
    "What is the last four digits of your Aadhaar number?",
    "What is your PAN number?",
    "What is your current residential address?",
    "How long have you been residing at this address?",
    "What is your occupation?",
    "What is your approximate annual income?",
    "What is the primary purpose for opening this account?",
    "What is the source of your funds?",
    "What will be the uses of your funds?",
    "What will be the expected annual turnover in this account?",
    "Can you confirm your registered mobile number?",
    "What is your email address?",
    "Are you or any immediate family member a politically exposed person?",
    "Will this account be used for transactions outside the country?",
    "Are you the ultimate beneficial owner of this account?",
    "Do you consent to recording this KYC interaction?",
    "Do you confirm all the information provided is true and correct?"
]

# ========================
# 🤖 LLM-based Extraction
# ========================
def extract_answers_llm(transcript_text):
    prompt = f"""
You are a smart assistant helping parse customer responses from a KYC transcript.

### Task:
Given the transcript below, extract answers for the predefined questions. Match the best response even if the question wording slightly differs.

### Format:
Return output as JSON in this format:
{{
  "Question?": {{
    "parsed_question": "shortened/normalized version of the question",
    "answer": "actual answer extracted"
  }},
  ...
}}

### Predefined Questions:
{json.dumps(PREDEFINED_QUESTIONS, indent=2)}

### Transcript:
{transcript_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for KYC transcript parsing."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw_response = response.choices[0].message.content
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        raw_response = raw_response.strip().strip("```json").strip("```")
        return json.loads(raw_response)

# ========================
# 🧠 Fuzzy Fallback (Optional)
# ========================
def extract_answers_fuzzy(transcript_text, threshold=70):
    answers = {}
    sentences = [s.strip() for s in transcript_text.split("?") if s.strip()]
    for pq in PREDEFINED_QUESTIONS:
        match, score, _ = process.extractOne(pq.lower(), sentences, scorer=fuzz.token_sort_ratio)
        if match and score >= threshold:
            answers[pq] = {
                "parsed_question": match.strip(" .:\n"),
                "answer": "(Extracted manually or assumed)"
            }
        else:
            answers[pq] = {
                "parsed_question": "(Not found)",
                "answer": "(Not found)"
            }
    return answers

# ========================
# 💾 Save Functions
# ========================
def save_to_csv(data, csv_path):
    file_exists = Path(csv_path).exists()
    with open(csv_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["predefined_question", "parsed_question", "answer"])
        if not file_exists:
            writer.writeheader()
        for pq, v in data.items():
            writer.writerow({
                "predefined_question": pq,
                "parsed_question": v.get("parsed_question", "(Not found)"),
                "answer": v.get("answer", "(Not found)")
            })
    print(f"✅ Saved to CSV: {csv_path}")

def save_to_json(data, json_path):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved to JSON: {json_path}")

# ========================
# ▶️ CLI Entry Point
# ========================
if __name__ == "__main__":
    transcript_file = Path("transcript.txt")
    if not transcript_file.exists():
        print("❌ transcript.txt not found!")
    else:
        transcript_text = transcript_file.read_text(encoding="utf-8")
        answers = extract_answers_llm(transcript_text)
        save_to_json(answers, "kyc_answers.json")
        save_to_csv(answers, "kyc_answers.csv")
