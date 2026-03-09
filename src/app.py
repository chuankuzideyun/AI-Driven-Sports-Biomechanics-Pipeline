import os
from flask import Flask, render_template, request, redirect, url_for
from tasks import run_analysis_task
from main import MagicAnalyzer

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
analyzer = MagicAnalyzer()

@app.route('/', methods=['GET', 'POST'])
def index():
    runs = [f"run_0{i}" for i in range(1, 6)]
    
    if request.method == 'POST':
        run_id = request.form.get('run_id')
        
        run_path = os.path.join("data", run_id)
        video_p = os.path.join(run_path, "video.mov")
        csv_p = os.path.join(run_path, "04_correlated_data.csv")
        json_p = os.path.join(run_path, "02_timestamps.json")
        
        if not os.path.exists(video_p):
            return f"Error: Video file not found at {video_p}", 400

        pdf_dir = os.path.join("data", "biomechanics_pdfs")
        context = analyzer.extract_pdf_knowledge(os.path.join("data", "biomechanics_pdfs"))

        task = run_analysis_task.delay(run_id, video_p, csv_p, json_p, context)
        
        return redirect(url_for('task_status', task_id=task.id))

    return render_template('index.html', runs=runs)

@app.route('/status/<task_id>')
def task_status(task_id):
    task = run_analysis_task.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return render_template('result.html', report=task.info['report'], run_id=task.info['run_id'])
    elif task.state == 'FAILURE':
        return f"Analysis Failed: {task.info}", 500
    else:
        # Show a loading page while processing
        return render_template('loading.html', state=task.state, task_id=task_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)