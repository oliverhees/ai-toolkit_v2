# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



from flask import Flask, request
from flask_cors import CORS
from queue import Queue
from services.webhook import send_webhook
import threading
import uuid
import os
import time
import json
from version import BUILD_NUMBER  # Import the BUILD_NUMBER
from app_utils import log_job_status, discover_and_register_blueprints  # Import the discover_and_register_blueprints function
from services.gcp_toolkit import trigger_cloud_run_job
from flask_swagger_ui import get_swaggerui_blueprint

MAX_QUEUE_LENGTH = int(os.environ.get('MAX_QUEUE_LENGTH', 0))

def create_app():
    app = Flask(__name__)

    # Enable CORS for all routes
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # Allow all origins (restrict in production if needed)
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-API-Key", "Authorization"]
        }
    })

    # Create a queue to hold tasks
    task_queue = Queue()
    queue_id = id(task_queue)  # Generate a single queue_id for this worker

    # Function to process tasks from the queue
    def process_queue():
        while True:
            job_id, data, task_func, queue_start_time = task_queue.get()
            queue_time = time.time() - queue_start_time
            run_start_time = time.time()
            pid = os.getpid()  # Get the PID of the actual processing thread
            
            # Log job status as running
            log_job_status(job_id, {
                "job_status": "running",
                "job_id": job_id,
                "queue_id": queue_id,
                "process_id": pid,
                "response": None
            })
            
            response = task_func()
            run_time = time.time() - run_start_time
            total_time = time.time() - queue_start_time

            response_data = {
                "endpoint": response[1],
                "code": response[2],
                "id": data.get("id"),
                "job_id": job_id,
                "response": response[0] if response[2] == 200 else None,
                "message": "success" if response[2] == 200 else response[0],
                "pid": pid,
                "queue_id": queue_id,
                "run_time": round(run_time, 3),
                "queue_time": round(queue_time, 3),
                "total_time": round(total_time, 3),
                "queue_length": task_queue.qsize(),
                "build_number": BUILD_NUMBER  # Add build number to response
            }
            
            # Log job status as done
            log_job_status(job_id, {
                "job_status": "done",
                "job_id": job_id,
                "queue_id": queue_id,
                "process_id": pid,
                "response": response_data
            })

            # Only send webhook if webhook_url has an actual value (not an empty string)
            if data.get("webhook_url") and data.get("webhook_url") != "":
                send_webhook(data.get("webhook_url"), response_data)

            task_queue.task_done()

    # Start the queue processing in a separate thread
    threading.Thread(target=process_queue, daemon=True).start()

    # Decorator to add tasks to the queue or bypass it
    def queue_task(bypass_queue=False):
        def decorator(f):
            from functools import wraps
            @wraps(f)
            def wrapper(*args, **kwargs):
                job_id = str(uuid.uuid4())
                data = request.json if request.is_json else {}
                pid = os.getpid()  # Get PID for non-queued tasks
                start_time = time.time()

                # If running inside a GCP Cloud Run Job instance, execute synchronously
                if os.environ.get("CLOUD_RUN_JOB"):
                    # Get execution name from Google's env var
                    execution_name = os.environ.get("CLOUD_RUN_EXECUTION", "gcp_job")

                    # Log job status as running
                    log_job_status(job_id, {
                        "job_status": "running",
                        "job_id": job_id,
                        "queue_id": execution_name,
                        "process_id": pid,
                        "response": None
                    })

                    # Execute the function directly (no queue)
                    response = f(job_id=job_id, data=data, *args, **kwargs)
                    run_time = time.time() - start_time

                    # Build response object
                    response_obj = {
                        "code": response[2],
                        "id": data.get("id"),
                        "job_id": job_id,
                        "response": response[0] if response[2] == 200 else None,
                        "message": "success" if response[2] == 200 else response[0],
                        "run_time": round(run_time, 3),
                        "queue_time": 0,
                        "total_time": round(run_time, 3),
                        "pid": pid,
                        "queue_id": execution_name,
                        "build_number": BUILD_NUMBER
                    }

                    # Log job status as done
                    log_job_status(job_id, {
                        "job_status": "done",
                        "job_id": job_id,
                        "queue_id": execution_name,
                        "process_id": pid,
                        "response": response_obj
                    })

                    # Send webhook if webhook_url is provided
                    if data.get("webhook_url") and data.get("webhook_url") != "":
                        send_webhook(data.get("webhook_url"), response_obj)

                    return response_obj, response[2]

                if os.environ.get("GCP_JOB_NAME") and data.get("webhook_url"):
                    try:
                        overrides = {
                            'container_overrides': [
                                {
                                    'env': [
                                        # Environment variables to pass to the GCP Cloud Run Job
                                        {
                                            'name': 'GCP_JOB_PATH',
                                            'value': request.path  # Endpoint to call
                                        },
                                        {
                                            'name': 'GCP_JOB_PAYLOAD',
                                            'value': json.dumps(data)  # Payload as a string
                                        },
                                    ]
                                }
                            ],
                            'task_count': 1
                        }

                        # Call trigger_cloud_run_job with the overrides dictionary
                        response = trigger_cloud_run_job(
                            job_name=os.environ.get("GCP_JOB_NAME"),
                            location=os.environ.get("GCP_JOB_LOCATION", "us-central1"),
                            overrides=overrides  # Pass overrides to the job
                        )

                        if not response.get("job_submitted"):
                            raise Exception(f"GCP job trigger failed: {response}")

                        # Extract execution name and short ID for tracking
                        execution_name = response.get("execution_name", "")
                        gcp_queue_id = execution_name.split('/')[-1] if execution_name else "gcp_job"

                        # Prepare the response object
                        response_obj = {
                            "code": 200,
                            "id": data.get("id"),
                            "job_id": job_id,
                            "message": response,
                            "job_name": os.environ.get("GCP_JOB_NAME"),
                            "location": os.environ.get("GCP_JOB_LOCATION", "us-central1"),
                            "pid": pid,
                            "queue_id": gcp_queue_id,
                            "build_number": BUILD_NUMBER
                        }
                        log_job_status(job_id, {
                            "job_status": "submitted",
                            "job_id": job_id,
                            "queue_id": gcp_queue_id,
                            "process_id": pid,
                            "response": response_obj
                        })
                        return response_obj, 200  # Return 200 since it's a submission success

                    except Exception as e:
                        error_response = {
                            "code": 500,
                            "id": data.get("id"),
                            "job_id": job_id,
                            "message": f"GCP Cloud Run Job trigger failed: {str(e)}",
                            "job_name": os.environ.get("GCP_JOB_NAME"),
                            "location": os.environ.get("GCP_JOB_LOCATION", "us-central1"),
                            "pid": pid,
                            "queue_id": "gcp_job",
                            "build_number": BUILD_NUMBER
                        }
                        log_job_status(job_id, {
                            "job_status": "failed",
                            "job_id": job_id,
                            "queue_id": "gcp_job",
                            "process_id": pid,
                            "response": error_response
                        })
                        return error_response, 500

                elif bypass_queue or 'webhook_url' not in data:
                    
                    # Log job status as running immediately (bypassing queue)
                    log_job_status(job_id, {
                        "job_status": "running",
                        "job_id": job_id,
                        "queue_id": queue_id,
                        "process_id": pid,
                        "response": None
                    })
                    
                    response = f(job_id=job_id, data=data, *args, **kwargs)
                    run_time = time.time() - start_time
                    
                    response_obj = {
                        "code": response[2],
                        "id": data.get("id"),
                        "job_id": job_id,
                        "response": response[0] if response[2] == 200 else None,
                        "message": "success" if response[2] == 200 else response[0],
                        "run_time": round(run_time, 3),
                        "queue_time": 0,
                        "total_time": round(run_time, 3),
                        "pid": pid,
                        "queue_id": queue_id,
                        "queue_length": task_queue.qsize(),
                        "build_number": BUILD_NUMBER  # Add build number to response
                    }
                    
                    # Log job status as done
                    log_job_status(job_id, {
                        "job_status": "done",
                        "job_id": job_id,
                        "queue_id": queue_id,
                        "process_id": pid,
                        "response": response_obj
                    })
                    
                    return response_obj, response[2]
                else:
                    if MAX_QUEUE_LENGTH > 0 and task_queue.qsize() >= MAX_QUEUE_LENGTH:
                        error_response = {
                            "code": 429,
                            "id": data.get("id"),
                            "job_id": job_id,
                            "message": f"MAX_QUEUE_LENGTH ({MAX_QUEUE_LENGTH}) reached",
                            "pid": pid,
                            "queue_id": queue_id,
                            "queue_length": task_queue.qsize(),
                            "build_number": BUILD_NUMBER  # Add build number to response
                        }
                        
                        # Log the queue overflow error
                        log_job_status(job_id, {
                            "job_status": "done",
                            "job_id": job_id,
                            "queue_id": queue_id,
                            "process_id": pid,
                            "response": error_response
                        })
                        
                        return error_response, 429
                    
                    # Log job status as queued
                    log_job_status(job_id, {
                        "job_status": "queued",
                        "job_id": job_id,
                        "queue_id": queue_id,
                        "process_id": pid,
                        "response": None
                    })
                    
                    task_queue.put((job_id, data, lambda: f(job_id=job_id, data=data, *args, **kwargs), start_time))
                    
                    return {
                        "code": 202,
                        "id": data.get("id"),
                        "job_id": job_id,
                        "message": "processing",
                        "pid": pid,
                        "queue_id": queue_id,
                        "max_queue_length": MAX_QUEUE_LENGTH if MAX_QUEUE_LENGTH > 0 else "unlimited",
                        "queue_length": task_queue.qsize(),
                        "build_number": BUILD_NUMBER  # Add build number to response
                    }, 202
            return wrapper
        return decorator

    app.queue_task = queue_task

    # Serve OpenAPI spec
    @app.route('/static/openapi.yaml')
    def serve_openapi_spec():
        from flask import send_file
        import os
        # Use absolute path from app root
        spec_path = os.path.join(os.path.dirname(__file__), 'static', 'openapi.yaml')
        return send_file(spec_path, mimetype='application/x-yaml')

    # Register special route for Next.js root asset paths first
    from routes.v1.media.feedback import create_root_next_routes
    create_root_next_routes(app)
    
    # Use the discover_and_register_blueprints function to register all blueprints
    discover_and_register_blueprints(app)

    # Configure Swagger UI with static OpenAPI spec
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/openapi.yaml'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "AI Toolkit API",
            'defaultModelsExpandDepth': -1  # Hide models section by default
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)