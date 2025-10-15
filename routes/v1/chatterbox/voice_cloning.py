# Copyright (c) 2025 NetzPrinz aka Oliver Hees
# Based on no-code-architects-toolkit by Stephen G. Pope
#
# Chatterbox TTS Integration - Voice Cloning API Endpoint

from flask import Blueprint
from app_utils import *
import logging
from services.v1.chatterbox.tts import process_voice_cloning
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_chatterbox_voice_cloning_bp = Blueprint("v1_chatterbox_voice_cloning", __name__)
logger = logging.getLogger(__name__)


@v1_chatterbox_voice_cloning_bp.route("/v1/chatterbox/voice-cloning", methods=["POST"])
@authenticate
@validate_payload(
    {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "minLength": 1,
                "maxLength": 5000,
                "description": "Text to convert to speech with cloned voice"
            },
            "voice_audio_url": {
                "type": "string",
                "format": "uri",
                "description": "URL of reference voice audio for cloning"
            },
            "language": {
                "type": "string",
                "default": "en",
                "description": "Language code (e.g., en, de, es, fr, it)"
            },
            "model_type": {
                "type": "string",
                "enum": ["english", "multilingual"],
                "default": "multilingual",
                "description": "Model type to use"
            },
            "emotion_intensity": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 2.0,
                "default": 1.0,
                "description": "Emotion exaggeration level"
            },
            "webhook_url": {
                "type": "string",
                "format": "uri",
                "description": "Webhook URL for async processing"
            },
            "id": {
                "type": "string",
                "description": "Custom identifier for the request"
            },
        },
        "required": ["text", "voice_audio_url"],
        "additionalProperties": False,
    }
)
@queue_task_wrapper(bypass_queue=False)
def clone_voice(job_id, data):
    """
    Generate speech with voice cloning using Chatterbox TTS
    ---
    tags:
      - Chatterbox TTS
    summary: Voice Cloning
    description: |
      Clone a voice from a reference audio sample and generate speech with that voice.

      **Features:**
      - Zero-shot voice cloning from single audio sample
      - Cross-lingual voice cloning (clone voice in any supported language)
      - Maintains voice characteristics (tone, pitch, accent)
      - High-fidelity cloning results
      - GPU-accelerated processing

      **Reference Audio Requirements:**
      - Format: WAV, MP3, FLAC, or other common formats
      - Duration: 3-30 seconds recommended
      - Quality: Clear speech without background noise
      - Content: Single speaker only

      **Supported Languages:**
      en, de, es, fr, it, pt, pl, tr, ru, nl, cs, ar, zh, ja, ko, hu, hi, and more
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - text
            - voice_audio_url
          properties:
            text:
              type: string
              minLength: 1
              maxLength: 5000
              example: "Hello! This is a demonstration of voice cloning technology."
              description: Text to convert to speech using cloned voice (1-5000 characters)
            voice_audio_url:
              type: string
              format: uri
              example: "https://example.com/reference-voice.wav"
              description: URL of reference voice audio file for cloning (3-30 seconds recommended)
            language:
              type: string
              default: "en"
              example: "en"
              description: Language code for the text (e.g., en, de, es, fr, it, pt, ja, zh, ko)
            model_type:
              type: string
              enum: [english, multilingual]
              default: "multilingual"
              example: "multilingual"
              description: Model type (multilingual recommended for voice cloning)
            emotion_intensity:
              type: number
              format: float
              minimum: 0.0
              maximum: 2.0
              default: 1.0
              example: 1.0
              description: Emotion exaggeration level (0.0 = neutral, 1.0 = normal, 2.0 = maximum)
            webhook_url:
              type: string
              format: uri
              example: "https://your-app.com/webhook"
              description: Optional webhook URL for asynchronous processing notification
            id:
              type: string
              example: "voice-clone-123"
              description: Custom identifier for tracking this request
    responses:
      200:
        description: Successful synchronous response (no webhook_url provided)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            id:
              type: string
              example: "voice-clone-123"
            job_id:
              type: string
              example: "550e8400-e29b-41d4-a716-446655440000"
            response:
              type: string
              format: uri
              example: "https://storage.example.com/cloned-voice-audio.wav"
              description: URL of the generated audio file with cloned voice
            message:
              type: string
              example: "success"
            run_time:
              type: number
              example: 3.456
            queue_time:
              type: number
              example: 0
            total_time:
              type: number
              example: 3.456
            pid:
              type: integer
              example: 12345
            queue_id:
              type: integer
              example: 67890
            queue_length:
              type: integer
              example: 0
            build_number:
              type: string
              example: "1.0.123"
      202:
        description: Accepted for asynchronous processing (webhook_url provided)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 202
            id:
              type: string
              example: "voice-clone-123"
            job_id:
              type: string
              example: "550e8400-e29b-41d4-a716-446655440000"
            message:
              type: string
              example: "processing"
            pid:
              type: integer
              example: 12345
            queue_id:
              type: integer
              example: 67890
            max_queue_length:
              type: string
              example: "unlimited"
            queue_length:
              type: integer
              example: 1
            build_number:
              type: string
              example: "1.0.123"
      400:
        description: Bad Request - Invalid parameters
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            message:
              type: string
              example: "Invalid request: 'voice_audio_url' is a required property"
      401:
        description: Unauthorized - Invalid or missing API key
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 401
            message:
              type: string
              example: "Invalid or missing API key"
      429:
        description: Too Many Requests - Queue limit reached
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 429
            message:
              type: string
              example: "MAX_QUEUE_LENGTH (100) reached"
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 500
            message:
              type: string
              example: "Error downloading reference audio: Connection timeout"
    security:
      - ApiKeyAuth: []
    """
    text = data["text"]
    voice_audio_url = data["voice_audio_url"]
    language = data.get("language", "en")
    model_type = data.get("model_type", "multilingual")
    emotion_intensity = data.get("emotion_intensity", 1.0)

    logger.info(
        f"Job {job_id}: Received voice cloning request for text: {text[:50]}... with reference audio: {voice_audio_url}"
    )

    try:
        output_file = process_voice_cloning(
            text=text,
            voice_audio_url=voice_audio_url,
            job_id=job_id,
            language=language,
            emotion_intensity=emotion_intensity,
            model_type=model_type
        )
        logger.info(f"Job {job_id}: Voice cloning completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(
            f"Job {job_id}: Cloned voice audio uploaded to cloud storage: {cloud_url}"
        )

        return cloud_url, "/v1/chatterbox/voice-cloning", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during voice cloning - {str(e)}")
        return str(e), "/v1/chatterbox/voice-cloning", 500
