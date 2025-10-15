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
    """
    Loop an audio file multiple times
    ---
    tags:
      - Audio
    summary: Loop Audio File
    description: |
      Repeat an audio file a specified number of times efficiently.

      **Features:**
      - Download audio once, loop 1-100 times
      - No re-encoding (uses FFmpeg concat demuxer)
      - Output format: MP3
      - Supports webhook for async processing
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - audio_url
            - loop_count
          properties:
            audio_url:
              type: string
              format: uri
              example: "https://example.com/audio.mp3"
              description: URL of the audio file to loop
            loop_count:
              type: integer
              minimum: 1
              maximum: 100
              example: 5
              description: Number of times to repeat the audio (1-100)
            webhook_url:
              type: string
              format: uri
              example: "https://your-app.com/webhook"
              description: Optional webhook URL for async processing
            id:
              type: string
              example: "audio-loop-123"
              description: Custom identifier for tracking
    responses:
      200:
        description: Success - Audio looped
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            response:
              type: string
              example: "file:///app/storage/output.mp3"
              description: URL of the looped audio file
            message:
              type: string
              example: "success"
      202:
        description: Accepted for async processing
      400:
        description: Bad Request - Invalid parameters
      401:
        description: Unauthorized - Invalid API key
      500:
        description: Internal Server Error
    security:
      - ApiKeyAuth: []
    """
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
