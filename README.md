        AI-Powered UFDR Analysis Tool

> **"From complex data to simple clear answers with AI"**

![Project Status](https://img.shields.io/badge/Status-Prototype-cyan) !
[Google Tech] (https://img.shields.io/badge/Powered%20By-TensorFlow.js-orange) !
[License](https://img.shields.io/badge/License-MIT-blue)

## 📄 Abstract

Digital investigations are currently slowed by massive, complex UFDR (Universal Forensic Extraction Device) reports that require labor-intensive manual review. This creates bottlenecks and increases the risk of overlooking critical evidence.

**ForenX** is an AI-driven pipeline designed to enable rapid, accurate extraction of actionable insights. It automates UFDR parsing, normalizes timestamps, and uses NLP to elevate key entities, events, and relationships. The outcome is hours saved per case, reduced human error, and legally defensible reporting suitable for law enforcement.

---

## 💡 The Solution

ForenX streamlines digital forensic investigations by automatically parsing, analyzing, and summarizing complex UFDR reports using advanced AI techniques.

### Key Features
1.  **🛡️ Secure Biometric Login:** Client-side facial recognition (Face ID) ensures only authorized personnel can access sensitive case files.
2.  **🧠 Intelligent Entity Extraction (NER):** Uses LLMs (Gemma 2B) to identify names, dates, locations, and organizations.
3.  **📂 Automated Ingestion:** Drag-and-drop parsing of forensic archives.
4.  **⏱️ Timeline Normalization:** Unifies timestamps from different devices/apps into a single master timeline.
5.  **📊 Interactive Dashboard:** Cyber-aesthetic UI for visualizing evidence clusters.
6.  **📑 Automated Reporting:** Exports summarized, legally defensible reports.

---

## 🔧 Google Technologies Used

This solution leverages **Google Technologies** across its security and intelligence stack:

1.  **Google GenAI SDK:** We utilize the `google-genai` library to interface with Google's latest generative models for high-level evidence summarization and pattern matching.
2.  **Gemma 2B (via Ollama):** We deploy **Google's Gemma 2B** open model locally using Ollama for privacy-preserving, on-device analysis of sensitive text logs.
3.  **TensorFlow.js:** We use the TensorFlow.js engine (via `face-api.js`) to execute real-time, client-side biometric authentication.

---

## 🚀 Hybrid AI Architecture

**Hybrid AI Architecture:** Combines **Google's GenAI** (cloud-based powerful models) with **Gemma 2B** (local, privacy-preserving inference via Ollama) to handle both high-complexity analysis and sensitive, offline-capable workflows. This dual-model approach ensures:
- High-complexity cases leverage Google's powerful cloud models for advanced reasoning
- Sensitive investigations use local Gemma 2B for complete data privacy and offline capability
- Seamless fallback mechanisms for reliability and redundancy

## 🏗️ Architecture & Tech Stack

### Architecture Diagram
**Frontend** ↔ **Flask Backend** ↔ **Ollama (Gemma 2B)** ↔ **Database**

### Full Tech Stack
*   **Frontend:** HTML5, Tailwind CSS, JavaScript
*   **Biometrics:** Google TensorFlow.js (Client-side)
*   **Generative AI:**
    *   **Google GenAI** (Cloud Inference)
    *   **Gemma 2B** (Local Inference via Ollama)
*   **Backend:** Flask (Python)
*   **Database Connectivity:** MySQL Connector / SQLite (via SQLAlchemy)
*   **Utilities:** Pydantic (Data Validation), Requests (API calls)

---

## 🔄 Process Flow

1.  **User Access:** Investigator accesses portal → System triggers **Biometric Face Scan**.
2.  **Upload:** Authenticated user uploads forensic data.
3.  **Processing Pipeline:**
    *   **Ingestion:** Parse files and normalize data.
    *   **AI Analysis:** Send text logs to **Gemma 2B / Google GenAI** for entity extraction and summary.
4.  **Output:** System generates a Knowledge Graph & Triage Score.
5.  **Review:** Investigator views the Timeline and downloads the Final Report.

---

## ⚡ Setup Instructions

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/ForenX.git
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run Application:**
    ```bash
    python app.py
    ```
Note : We have utilised the reference.jpeg image as the real agent that drives the face recognition to demonstrate the prospect of facial recognition and its satisfying working
---

## ⚠️ Credits & Acknowledgments

**Crucial Attribution for Facial Recognition Models:**

> **The face detection and recognition capabilities in this project are powered by [face-api.js](https://github.com/justadudewhohacks/face-api.js), created by Vincent Mühler.**
>
> We gratefully acknowledge his work in making TensorFlow.js accessible for browser-based computer vision. The model weights located in our `static/models/` directory are sourced directly from his repository and are used here under the MIT License to demonstrate secure biometric authentication.

---

*Submitted for TechSprint GDG on Campus Dr. AIT*
