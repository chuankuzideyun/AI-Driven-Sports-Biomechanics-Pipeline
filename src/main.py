import os
import time
import pandas as pd
from PyPDF2 import PdfReader
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

from google import genai
from google.genai import types
import google.api_core.exceptions

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

DATA_ROOT = "data"
PDF_DIR = os.path.join(DATA_ROOT, "biomechanics_pdfs")
OUTPUT_FILE = "output/final_analysis_report.md"


class AthleraAnalyzer:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=API_KEY)
            # Keeping the 2.0-flash model as requested
            self.model_name = "gemini-3-flash-preview" 
            print(f"Gemini client initialized with {self.model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {e}")

    def extract_pdf_knowledge(self, pdf_folder):
        knowledge = ""
        if not os.path.exists(pdf_folder) or not os.listdir(pdf_folder):
            return "No biomechanics documentation provided."

        for file in os.listdir(pdf_folder):
            if file.endswith(".pdf"):
                try:
                    reader = PdfReader(os.path.join(pdf_folder, file))
                    # Extract text from first two pages for context
                    for i in range(min(2, len(reader.pages))):
                        text = reader.pages[i].extract_text()
                        if text:
                            knowledge += text + "\n"
                except Exception as e:
                    print(f"Error reading {file}: {e}")

        # Final check: if files existed but no text was extracted
        return knowledge[:5000] if knowledge else "No biomechanics documentation provided."

    @retry(
        retry=retry_if_exception_type((
            google.api_core.exceptions.ResourceExhausted, 
            google.api_core.exceptions.ServiceUnavailable
        )),
        wait=wait_exponential(multiplier=2, min=15, max=90),
        stop=stop_after_attempt(3),
    )
    def run_inference(self, video_path, data_summary, context):
        print(f"Uploading video: {video_path}")
        
        # FIX: Using 'file' argument instead of 'path' for this SDK version
        uploaded_file = self.client.files.upload(file=video_path)
        
        # Poll file state until it is processed
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(5)
            uploaded_file = self.client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
            raise RuntimeError("Video processing failed on server.")

        print("Running biomechanics inference...")
        
        # Construct multimodal contents
        prompt_text = f"""
Role: Senior Biomechanics Coach

Biomechanics References:
{context}

Sensor Data Summary:
{data_summary}

Task:
Analyze the sprint mechanics in the video.
Identify technical flaws, inefficiencies, and injury risks.
Correlate sensor data with visual movement patterns.
Provide professional coaching cues.
Output in Markdown format.
"""
        contents = [
            types.Part.from_uri(
                file_uri=uploaded_file.uri,
                mime_type="video/quicktime",
            ),
            types.Part.from_text(text=prompt_text)
        ]

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
        )

        # Cleanup remote file
        self.client.files.delete(name=uploaded_file.name)

        return response.text


def main():
    analyzer = AthleraAnalyzer()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Athlera Sprint Performance Report\n\n")

    print("Step 1: Extracting PDF knowledge...")
    biomechanics_context = analyzer.extract_pdf_knowledge(PDF_DIR)

    run_folders = ["run_01", "run_02", "run_03", "run_04", "run_05"]

    for run_id in run_folders:
        try:
            print(f"\n>>> Analyzing {run_id}...")

            run_path = os.path.join(DATA_ROOT, run_id)
            if not os.path.exists(os.path.join(run_path, "video.mov")):
                run_path = os.path.join(run_path, run_id)

            video_p = os.path.join(run_path, "video.mov")
            csv_p = os.path.join(run_path, "04_correlated_data.csv")

            if not os.path.exists(video_p) or not os.path.exists(csv_p):
                print(f"Skipping {run_id}: missing files")
                continue

            df = pd.read_csv(csv_p)
            data_stats = (
                f"Columns: {list(df.columns)}\n"
                f"Summary:\n{df.iloc[:, 1:4].describe().to_string()}"
            )

            result = analyzer.run_inference(video_p, data_stats, biomechanics_context)

            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"## Analysis: {run_id}\n\n{result}\n\n---\n\n")

            # Updated cooldown to 90 seconds to reset Free Tier token-per-minute limits
            print("Success. Cooling down 90s for quota protection...")
            time.sleep(90)

        except Exception as e:
            print(f"Error in {run_id}: {e}")

    print(f"\nPipeline complete. Final report: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()