import pandas as pd
import json
import numpy as np

class SprintDataProcessor:
    def __init__(self, csv_path, json_path):
        self.csv_path = csv_path
        self.json_path = json_path

    def get_synced_data(self):
        """Merges frame-level timestamps with 1080 Motion telemetry."""
        df_metrics = pd.read_csv(self.csv_path)
        with open(self.json_path, 'r') as f:
            video_meta = json.load(f)
        
        synced_rows = []
        for frame_info in video_meta['timestamps']:
            frame_idx = frame_info['frame_number']
            ts = frame_info['timestamp_sec']
            
            # Find closest index in CSV based on 'Time' column
            closest_idx = (df_metrics['Time'] - ts).abs().idxmin()
            row = df_metrics.iloc[closest_idx].to_dict()
            row['frame_number'] = frame_idx
            synced_rows.append(row)
            
        return pd.DataFrame(synced_rows)

    def detect_anomalies(self, df):
        """Identifies technical indicators like braking forces or peak power."""
        anomalies = []
        
        # Guard clause: If the dataframe is empty, return empty list immediately
        if df.empty:
            return anomalies
        
        # 1. Braking Phase
        braking = df[(df['Speed'] > 3) & (df['Acceleration'] < -1.5)]
        if not braking.empty:
            peak_braking = braking.loc[braking['Acceleration'].idxmin()]
            anomalies.append({
                "time": peak_braking['Time'],
                "frame": int(peak_braking['frame_number']),
                "label": "Significant Braking Force",
                "description": f"Speed: {peak_braking['Speed']:.2f} m/s, Acc: {peak_braking['Acceleration']:.2f} m/s²"
            })

        # 2. Peak Power Output
        # Safe check before calling idxmax
        if not df['Power'].empty:
            peak_p_row = df.loc[df['Power'].idxmax()]
            anomalies.append({
                "time": peak_p_row['Time'],
                "frame": int(peak_p_row['frame_number']),
                "label": "Peak Power Output",
                "description": f"Power: {peak_p_row['Power']:.1f} W"
            })
        
        return anomalies