# AI-Driven Sports Biomechanics Pipeline

## Project Overview
This project implements an automated, AI-native pipeline designed to analyze athletic sprint performance by fusing multimodal data. It correlates high-speed video recordings with time-series resistance data to identify recurring technical flaws in sprinting mechanics across multiple sessions.

The system leverages **Gemini 2.0/2.5 Flash** models to perform deep reasoning on biomechanical patterns, following an **AI-accelerated coding workflow** where all analysis is generated through a single execution pipeline.

---

## Technical Architecture & Security Strategy

### 1. LLM Data Protection Framework
As an AI service provider, maintaining data integrity and privacy is paramount. The system adopts the following strategy:

* **Inbound Data Sanitization:** Implementing automated detection for Personally Identifiable Information (PII) to redact sensitive data before it reaches the model context.
* **Middleware Guardrails:** Using semantic filtering to monitor assistant output, ensuring confidential documents or sensitive metrics are not leaked during streaming responses.
* **Source Access Control:** Enforcing strict auditing and "Least Privilege" protocols for all connected data sources and servers to prevent unauthorized data extraction.

### 2. Analytical Logic
* **Multimodal Fusion:** The pipeline synchronizes `video.mov` files with sensor data (CSV) to observe movement phases and force production patterns.
* **Knowledge-Informed Reasoning:** The LLM is provided with foundational biomechanical knowledge extracted from domain-specific PDF documentation to support its analysis of arm mechanics, posture, and asymmetries.
* **Resilience Engineering:** To handle API rate limits, the system features a **Checkpoint & Resume** mechanism that prevents redundant processing of previously analyzed runs.

---

## Setup Instructions

### Prerequisites
* Python 3.10+
* A valid Gemini API Key 

### Installation
It is recommended to install dependencies directly through your project's specific Python interpreter to avoid environment conflicts:

```bash
python -m pip install -U google-genai pandas PyPDF2 tenacity python-dotenv
```

### Environment Setup
Create a .env file in the root directory:
```bash
GEMINI_API_KEY=your_api_key_here
```

### Execution
Run the core pipeline to process all videos and generate the final analysis:

```bash
python src/main.py
```
The result is exported as a structured Markdown report in the output/ directory.

## Technical Summary
### Problem-Solving Flow
1. Model Discovery: Utilized genai.list_models() to identify the most robust model endpoints available for high-fidelity video understanding.

2. File Handling: Resolved INVALID_ARGUMENT errors by refactoring local file access into a cloud-native Upload-and-Poll pattern using the Google File API to ensure file state is ACTIVE before inference.

3. Quota Management: Managed 429 RESOURCE_EXHAUSTED errors by implementing adaptive throttling (90s-120s cooldowns) and token-minimization strategies such as summarizing CSV data.
