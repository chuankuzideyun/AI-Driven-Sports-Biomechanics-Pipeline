from tasks import run_analysis_task

@app.route('/', methods=['POST'])
def index():
    run_id = request.form.get('run_id')
    # ... locate files logic ...
    
    # Trigger task asynchronously
    task = run_analysis_task.delay(run_id, video_p, csv_p, json_p, context)
    
    # Redirect to a status page with the task_id
    return redirect(url_for('task_status', task_id=task.id))

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