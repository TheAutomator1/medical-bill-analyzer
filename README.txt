============================================================
  MEDICAL BILL ANALYZER — SETUP GUIDE
============================================================

STEP 1 — GET A FREE GROQ API KEY
---------------------------------
1. Go to https://console.groq.com
2. Sign up for a free account (no credit card required)
3. Navigate to "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy the key — you will paste it into the app


STEP 2 — INSTALL PYTHON (if not already installed)
----------------------------------------------------
Download Python 3.9 or newer from https://python.org
Make sure to check "Add Python to PATH" during installation


STEP 3 — INSTALL DEPENDENCIES
-------------------------------
Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux)
Navigate to this folder, then run:

    python -m pip install -r requirements.txt


STEP 4 — RUN THE APP
---------------------
In the same terminal, run:

    python app.py


HOW TO USE
----------
1. Paste your Groq API key into the API key field
2. Click "Browse PDF" and select your medical bill PDF
3. Click "Analyze My Bill"
4. Wait ~10-20 seconds for the AI analysis
5. Review the breakdown, red flags, and dispute letter
6. Click "Copy to Clipboard" to copy the full report


NOTES
-----
- The app works with text-based PDFs (not scanned images)
- Your API key is never stored or transmitted anywhere except Groq
- The analysis is for informational purposes only and is not
  a substitute for professional legal or medical advice

============================================================
