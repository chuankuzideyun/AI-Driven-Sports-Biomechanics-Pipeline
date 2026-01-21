# 404 models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.
import os
import time
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions
from dotenv import load_dotenv

# --- Configuration (Verified with your folder structure) ---
load_dotenv() 
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Error: GEMINI_API_KEY not found in .env file. Please check your .env file content.")

genai.configure(api_key=API_KEY)

DATA_ROOT = "data"
PDF_DIR = os.path.join(DATA_ROOT, "biomechanics_pdfs")
OUTPUT_FILE = "output/final_analysis_report.md"

genai.configure(api_key=API_KEY)

class AthleraAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')

    def extract_pdf_knowledge(self, pdf_folder):
        knowledge_base = ""
        if not os.path.exists(pdf_folder):
            print(f"Warning: PDF folder not found at {pdf_folder}")
            return "No biomechanics docs."
        
        for file in os.listdir(pdf_folder):
            if file.endswith(".pdf"):
                try:
                    reader = PdfReader(os.path.join(pdf_folder, file))
                    for i in range(min(2, len(reader.pages))):
                        knowledge_base += reader.pages[i].extract_text() + "\n"
                except Exception as e:
                    print(f"Error reading PDF {file}: {e}")
        return knowledge_base[:5000]

    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        wait=wait_exponential(multiplier=2, min=15, max=90),
        stop=stop_after_attempt(3)
    )
    def run_inference(self, video_path, data_summary, context):
        print(f"Uploading video: {video_path}...")
        video_file = genai.upload_file(path=video_path)
        
        while video_file.state.name == "PROCESSING":
            time.sleep(5)
            video_file = genai.get_file(video_file.name)

        prompt = f"""
        Role: Senior Biomechanics Coach.
        Guidelines: {context}
        Data Summary: {data_summary}
        Task: Analyze the video for technical sprint flaws. Output Markdown.
        """

        response = self.model.generate_content([video_file, prompt])
        genai.delete_file(video_file.name)
        return response.text

def main():
    analyzer = AthleraAnalyzer()
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Athlera Sprint Performance Report\n\n")

    print("Step 1: Extracting PDF knowledge...")
    biomechanics_context = analyzer.extract_pdf_knowledge(PDF_DIR)
    
    # Updated to match your folder list
    run_folders = ["run_01", "run_02", "run_03", "run_04", "run_05"]

    for run_id in run_folders:
        try:
            print(f"\n>>> Analyzing {run_id}...")
            
            # Constructing paths based on your image
            # Note: run_03 has a nested run_03 subfolder in your image, 
            # we will handle the standard 'data/run_XX/file' structure.
            run_path = os.path.join(DATA_ROOT, run_id)
            
            # If your structure has run_03/run_03/video.mov, we check for that:
            if not os.path.exists(os.path.join(run_path, "video.mov")):
                run_path = os.path.join(run_path, run_id)

            video_p = os.path.join(run_path, "video.mov")
            csv_p = os.path.join(run_path, "04_correlated_data.csv")

            if not os.path.exists(video_p) or not os.path.exists(csv_p):
                print(f"Skipping {run_id}: Missing video.mov or csv file.")
                continue

            df = pd.read_csv(csv_p)
            # Taking a slice of data to represent the run
            data_stats = f"Columns: {list(df.columns)}. Summary: {df.iloc[:, 1:4].describe().to_string()}"
            
            result = analyzer.run_inference(video_p, data_stats, biomechanics_context)
            
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"## Analysis: {run_id}\n\n{result}\n\n---\n\n")
            
            print(f"Success! Waiting 45s for quota...")
            time.sleep(45)
            
        except Exception as e:
            print(f"Error in {run_id}: {e}")

    print(f"\nDone. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()