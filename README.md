# AI-Driven Sports Biomechanics Pipeline

## Project Overview
This project implements an automated, AI-native pipeline designed to analyze athletic sprint performance by fusing multimodal data. It correlates high-speed video recordings with time-series resistance data to identify recurring technical flaws in sprinting mechanics across multiple sessions.

The system leverages **Gemini 2.0 Flash** models to perform deep reasoning on biomechanical patterns, following an AI-accelerated coding workflow where all analysis is generated through a single execution pipeline.

---

## Technical Explanation

### 1. MLOps
This project now follows MLOps best practices to ensure reliability, reproducibility, and automated deployment.

#### 1.1 Automated CI/CD Pipeline (GitHub Actions):
The repository is integrated with GitHub Actions to handle the full lifecycle of the application:

* **Continuous Integration (CI):** Every code push triggers an automated suite of pytest unit tests to verify data processing logic and API connectivity.

* **Continuous Deployment (CD):** Once tests pass, the system automatically builds a Docker image and pushes it to Docker Hub, ensuring the latest version is always ready for production.

#### 1.2 Robust Testing Suite (pytest): 

Implemented a professional testing framework to safeguard the analytical logic:

* **Logic Validation**: Verifies that the SprintDataProcessor correctly identifies peak power and braking anomalies even with edge-case data.

* **Environment Mocking:** Uses unittest.mock to simulate Gemini API responses, allowing for cost-effective and fast testing without consuming API quotas.

* **Robustness Checks:** Tests the system's behavior against empty dataframes and missing PDF documentation to prevent runtime crashes.

#### 1.3 Distributed Task Queue:
Implemented **Celery** with **Redis** as a message broker to decouple heavy AI inference from the web server, preventing request timeouts and enabling horizontal scaling.

#### 1.4 Container Orchestration:
Transitioned to a multi-container setup using **Docker Compose**, managing synchronized lifecycles for the Flask Web UI, Celery Worker, and Redis instances.


### 2. Analytical Logic
#### 2.1 Multimodal Fusion:
The pipeline synchronizes `video.mov` files with sensor data (CSV) to observe movement phases and force production patterns.

#### 2.2 Knowledge-Informed Reasoning:
The LLM is provided with foundational biomechanical knowledge extracted from domain-specific PDF documentation to support its analysis of arm mechanics, posture, and asymmetries.

#### 2.3 Resilience Engineering:
To handle API rate limits, the system features a **Checkpoint & Resume** mechanism that prevents redundant processing of previously analyzed runs.

---

## Quick Start (One-Command Execution)

### Professional Docker Compose Execution (Recommended)
The entire distributed system (Web + Worker + Redis) can be launched with a single command:
1. Create a `.env` file with your `GEMINI_API_KEY`.
2. Run the system:
```bash
docker-compose up --build
```
3. Access the UI at http://localhost:5000 to select a performance run (run_01 to run_05).


## Technical Summary
### Problem-Solving Flow
1. Model Discovery: Utilized genai.list_models() to identify the most robust model endpoints available for high-fidelity video understanding.

2. File Handling: Resolved INVALID_ARGUMENT errors by refactoring local file access into a cloud-native Upload-and-Poll pattern using the Google File API to ensure file state is ACTIVE before inference.

3. Quota Management: Managed 429 RESOURCE_EXHAUSTED errors by implementing adaptive throttling (90s-120s cooldowns) and token-minimization strategies such as summarizing CSV data.
