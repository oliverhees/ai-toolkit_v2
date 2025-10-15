from flask import Blueprint
from app_utils import *
import logging
from services.v1.audio.loop import process_audio_loop
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_audio_loop_bp = Blueprint("v1_audio_loop", __name__)
logger = logging.getLogger(__name__)


@v1_audio_loop_bp.route("/v1/audio/loop", methods=["POST"])
@authenticate
@validate_payload(
    {
        "type": "object",
        "properties": {
            "audio_url": {"type": "string", "format": "uri"},
            "loop_count": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Number of times to loop the audio (1-100)"
            },
            "webhook_url": {"type": "string", "format": "uri"},
            "id": {"type": "string"},
        },
        "required": ["audio_url", "loop_count"],
        "additionalProperties": False,
    }
)
@queue_task_wrapper(bypass_queue=False)
def loop_audio(job_id, data):
    audio_url = data["audio_url"]
    loop_count = data["loop_count"]
    webhook_url = data.get("webhook_url")
    id = data.get("id")

    logger.info(
        f"Job {job_id}: Received loop-audio request for {audio_url} with {loop_count} loops"
    )

    try:
        output_file = process_audio_loop(audio_url, loop_count, job_id)
        logger.info(f"Job {job_id}: Audio loop process completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(
            f"Job {job_id}: Looped audio uploaded to cloud storage: {cloud_url}"
        )

        return cloud_url, "/v1/audio/loop", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during audio loop process - {str(e)}")
        return str(e), "/v1/audio/loop", 500
