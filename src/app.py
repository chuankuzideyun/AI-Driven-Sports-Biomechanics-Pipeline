import os
import pandas as pd
from flask import Flask, render_template, request
from main import AthleraAnalyzer
from processor import SprintDataProcessor

app = Flask(__name__)

# --- Configuration ---
DATA_ROOT = "data"
PDF_DIR = os.path.join(DATA_ROOT, "biomechanics_pdfs")
analyzer = AthleraAnalyzer()

@app.route('/', methods=['GET', 'POST'])
def index():
    # List available run folders (run_01 to run_05)
    runs = [f"run_0{i}" for i in range(1, 6)]
    
    if request.method == 'POST':
        run_id = request.form.get('run_id')
        run_path = os.path.join(DATA_ROOT, run_id)
        
        # 1. Locate files automatically based on run_id
        video_p = os.path.join(run_path, "video.mov")
        csv_p = os.path.join(run_path, "04_correlated_data.csv")
        json_p = os.path.join(run_path, "02_timestamps.json")
        
        if not all(os.path.exists(f) for f in [video_p, csv_p, json_p]):
            return f"Error: Missing files in {run_id}", 400

        # 2. Extract Data Summary using your existing Processor
        processor = SprintDataProcessor(csv_p, json_p)
        synced_df = processor.get_synced_data()
        anomalies = processor.detect_anomalies(synced_df)
        
        # Format summary for Gemini
        data_summary = "\n".join([f"- Frame {a['frame']}: {a['label']}" for a in anomalies])
        
        # 3. Get PDF Context
        context = analyzer.extract_pdf_knowledge(PDF_DIR)
        
        # 4. Trigger AI Inference
        try:
            # Note: We pass the local path to your existing main.py logic
            report_md = analyzer.run_inference(video_p, data_summary, context)
            return render_template('result.html', report=report_md, run_id=run_id)
        except Exception as e:
            return f"AI Analysis Failed: {str(e)}", 500

    return render_template('index.html', runs=runs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)