import google.generativeai as genai
import os

class AthleraAIClient:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash') # Using latest for best video support

    def analyze_run(self, video_path, anomalies, pdf_texts):
        """Sends video and data clues to Gemini for biomechanical reasoning."""
        
        # Upload video to Gemini's temporary storage
        video_file = genai.upload_file(path=video_path)
        
        # Construct the Prompt with data evidence
        data_clues = "\n".join([f"- Frame {a['frame']}: {a['label']} ({a['description']})" for a in anomalies])
        
        prompt = f"""
        Role: You are a high-performance sprint coach.
        Task: Analyze the attached video for technical flaws using the provided biomechanics PDFs as reference.
        
        Data-Driven Clues from 1080 Motion:
        {data_clues}
        
        Instructions:
        1. Watch the video, specifically at the frames mentioned above.
        2. Identify repeated technical errors (e.g., heel striking, low knee drive, posture collapse).
        3. Reference specific concepts from the biomechanics PDFs.
        4. Output in Markdown format.
        """

        response = self.model.generate_content([video_file, prompt, *pdf_texts])
        return response.text