# The generated document only has a title and no content.
import os
import time
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions

# --- Configuration ---
API_KEY = "YOUR_GEMINI_API_KEY"
VIDEO_DIR = "data/videos"
CSV_DIR = "data/csv"
PDF_DIR = "data/biomechanics_pdfs"
OUTPUT_FILE = "output/final_analysis_report.md"

genai.configure(api_key=API_KEY)

class AthleraAnalyzer:
    def __init__(self):
        # Gemini 1.5 Flash is recommended for its high-speed video processing
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_pdf_knowledge(self, pdf_folder):
        knowledge_base = ""
        if not os.path.exists(pdf_folder) or not os.listdir(pdf_folder):
            return "No biomechanics documentation provided."
        for file in os.listdir(pdf_folder):
            if file.endswith(".pdf"):
                path = os.path.join(pdf_folder, file)
                try:
                    reader = PdfReader(path)
                    # Extracting first 3 pages of each PDF to manage context window
                    for i in range(min(3, len(reader.pages))):
                        knowledge_base += reader.pages[i].extract_text() + "\n"
                except Exception as e:
                    print(f"Error reading {file}: {e}")
        return knowledge_base[:8000]

    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        wait=wait_exponential(multiplier=2, min=10, max=60),
        stop=stop_after_attempt(5)
    )
    def run_inference(self, video_path, data_summary, context):
        print(f"Uploading and analyzing: {os.path.basename(video_path)}...")
        
        video_file = genai.upload_file(path=video_path)
        
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)

        prompt = f"""
        Context from Biomechanics Guidelines:
        {context}
        
        Time-Series Data Summary (Anomalies/Metrics):
        {data_summary}
        
        Task:
        Analyze the provided video and data to identify technical sprint mistakes. 
        Focus on: arm mechanics, ground contact, posture, and asymmetries.
        Output the final analysis in professional Markdown format.
        """

        response = self.model.generate_content([video_file, prompt])
        genai.delete_file(video_file.name)
        return response.text

def main():
    analyzer = AthleraAnalyzer()
    
    print("Pre-processing PDF documentation...")
    biomechanics_context = analyzer.extract_pdf_knowledge(PDF_DIR)
    
    reports = []
    runs = ["run_01", "run_02", "run_03", "run_04", "run_05"]

    for run in runs:
        try:
            print(f"\n>>> Processing {run}")
            video_p = os.path.join(VIDEO_DIR, f"{run}.mp4")
            csv_p = os.path.join(CSV_DIR, f"{run}.csv")
            
            # Simple data abstraction to stay within token limits
            df = pd.read_csv(csv_p)
            data_stats = df.describe().to_string()
            
            result = analyzer.run_inference(video_p, data_stats, biomechanics_context)
            reports.append(f"## {run} Performance Analysis\n\n{result}\n\n")
            
            # Rate limit cooling period
            print(f"Cooling down for 30s...")
            time.sleep(30)
            
        except Exception as e:
            print(f"Failed to process {run}: {e}")

    final_output = "# Sprint Performance Comprehensive Report\n\n" + "\n".join(reports)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print(f"\nPipeline execution complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()