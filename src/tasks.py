from celery_app import celery_instance
from main import MagicAnalyzer
from processor import SprintDataProcessor
import os

analyzer = MagicAnalyzer()

@celery_instance.task(bind=True)
def run_analysis_task(self, run_id, video_p, csv_p, json_p, context):
    """Background task for Biomechanics analysis."""
    # 1. Update state to 'PROCESSING'
    self.update_state(state='PROGRESS', meta={'status': 'Syncing data...'})
    
    processor = SprintDataProcessor(csv_p, json_p)
    synced_df = processor.get_synced_data()
    anomalies = processor.detect_anomalies(synced_df)
    data_summary = "\n".join([f"- Frame {a['frame']}: {a['label']}" for a in anomalies])

    # 2. Run Gemini Inference
    self.update_state(state='PROGRESS', meta={'status': 'Gemini is reasoning...'})
    report = analyzer.run_inference(video_p, data_summary, context)
    
    return {'report': report, 'run_id': run_id}