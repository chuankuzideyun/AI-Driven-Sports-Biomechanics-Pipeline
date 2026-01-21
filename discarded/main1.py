# ResourceExhausted: 429 You exceeded your current quota
import os
from dotenv import load_dotenv
from processor import SprintDataProcessor
from llm_client import AthleraAIClient

load_dotenv()

def main():
    # 1. Setup - Replace with your real API Key
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found. Please check your .env file.")
        return
        
    client = AthleraAIClient(API_KEY)
    
    runs = ['run_01', 'run_02', 'run_03', 'run_04', 'run_05']
    final_report = "# Athlera Sprint Analysis Global Report\n\n"

    for run in runs:
        print(f"Processing {run}...")
        
        # Define paths for this specific run
        csv_p = f"data/{run}/04_correlated_data.csv"
        json_p = f"data/{run}/02_timestamps.json"
        video_p = f"data/{run}/video.mov"
        
        # Step A: Data Processing
        processor = SprintDataProcessor(csv_p, json_p)
        df = processor.get_synced_data()
        anomalies = processor.detect_anomalies(df)
        
        # Step B: AI Analysis (Simulated PDF texts list)
        pdf_texts = ["Context from Biomechanics PDF 1...", "Context from PDF 2..."]
        analysis = client.analyze_run(video_p, anomalies, pdf_texts)
        
        final_report += f"## Analysis for {run}\n{analysis}\n\n"

    # 2. Output final Markdown
    with open("output/Final_Athlera_Report.md", "w") as f:
        f.write(final_report)
    
    print("Success! Report generated in output folder.")

if __name__ == "__main__":
    main()