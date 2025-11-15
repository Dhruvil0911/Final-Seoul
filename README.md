# Seasoul Skin Analyzer – Modular FastAPI Backend

A production-grade, fully modular FastAPI backend that analyzes facial skin images using **GPT‑4o** and **Gemini 2.0 Flash**, merges their outputs intelligently, and returns a final consolidated structured JSON.

---

## 🚀 Features

* Dual‑LLM image analysis (GPT‑4o + Gemini 2.0 Flash)
* Confidence‑based output synthesis
* Smart primary/secondary/tertiary concern resolution
* Duplicate issues auto‑removed from final metrics
* Weighted numeric merging
* Modular directory structure
* Clean Option‑B ordered response
* Fully typed, commented, production‑ready code
* Single‑model fallback handling

---

## 📁 Project Structure

```
project/
│
├── app.py                    # Main FastAPI entry
│
├── config.py                # Env keys + global config
│
├── core/
│   ├── prompts.py           # GPT + Gemini prompts
│   └── synthesizer.py       # Merging + conflict resolution logic
│
├── services/
│   ├── image_encoder.py     # Image → Base64
│   ├── llm_runner.py        # Runs both LLMs in parallel
│   ├── openai_client.py     # GPT‑4o API wrapper
│   └── gemini_client.py     # Gemini SDK/REST wrapper
│
└── requirements.txt         # Dependencies
```

---

## 🧠 How It Works

### **1. /analyze-skin endpoint:**

* Upload image
* Convert to base64
* Run GPT‑4o & Gemini in parallel
* Parse output JSON
* If both fail → return error
* If one succeeds → finalize that one
* If both succeed → merge via synthesizer

### **2. Synthesizer Logic:**

* Load both model outputs
* Choose higher-confidence model
* Extract primary/secondary/tertiary (top 3 severity)
* Merge attributes (weighted average / string confidence)
* Drop duplicated concerns from metric list
* Apply final ordered output

---

## 🔧 Installation

```bash
pip install -r requirements.txt
```

---

## ▶ Run the Server

### Development mode:

```bash
uvicorn app:app --reload
```

### Production (recommended):

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 🔑 Environment Variables

You must set:

```
OPENAI_API_KEY="your-key"
GOOGLE_API_KEY="your-key"
```

In Linux/macOS:

```bash
export OPENAI_API_KEY="..."
export GOOGLE_API_KEY="..."
```

Windows:

```cmd
set OPENAI_API_KEY=...
set GOOGLE_API_KEY=...
```

---

## 🧪 API Example

### Upload image:

```
POST /analyze-skin
Content-Type: multipart/form-data
file: <image>
```

### Response Structure (Option B ordering):

```
{
  "perceived_skin_age": 45,
  "skin_type": "Normal",
  "skin_type_score": 3,

  "primary_concern": "wrinkles",
  "primary_concern_severity": 3,
  "secondary_concern": "spots",
  "secondary_concern_severity": 3,
  "tertiary_concern": "texture",
  "tertiary_concern_severity": 2,

  "oiliness": 2,
  "pores": 2,
  "dehydration": 1,
  "elasticity": 3,
  ... etc
}
```

---

## 🛠 Deployment Tips

* Use `uvicorn` or `gunicorn` with workers
* Keep API keys in environment, not hardcoded
* Enable CORS for your frontend domain
* Use Reverse Proxy (NGINX) for SSL + routing

---

---

## 🧑‍💻 Author

**Dhruvil Bhaliya**

Modularization, patch cleanup & enhancements by ChatGPT.


