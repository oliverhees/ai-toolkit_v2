# Copyright (c) 2025 NetzPrinz aka Oliver Hees
# Based on no-code-architects-toolkit by Stephen G. Pope
#
# Chatterbox TTS Integration - Text-to-Speech API Endpoint

from flask import Blueprint
from app_utils import *
import logging
from services.v1.chatterbox.tts import process_text_to_speech
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_chatterbox_text_to_speech_bp = Blueprint("v1_chatterbox_text_to_speech", __name__)
logger = logging.getLogger(__name__)


@v1_chatterbox_text_to_speech_bp.route("/v1/chatterbox/text-to-speech", methods=["POST"])
@authenticate
@validate_payload(
    {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "minLength": 1,
                "maxLength": 5000,
                "description": "Text to convert to speech"
            },
            "language": {
                "type": "string",
                "default": "en",
                "description": "Language code (e.g., en, de, es, fr, it)"
            },
            "model_type": {
                "type": "string",
                "enum": ["english", "multilingual"],
                "default": "english",
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
        "required": ["text"],
        "additionalProperties": False,
    }
)
@queue_task_wrapper(bypass_queue=False)
def generate_speech(job_id, data):
    """
    Generate speech from text using Chatterbox TTS
    ---
    tags:
      - Chatterbox TTS
    summary: Text-to-Speech Generation
    description: |
      Convert text to natural-sounding speech using Chatterbox TTS model.

      **Features:**
      - Supports 23 languages (with multilingual model)
      - Adjustable emotion intensity
      - High-quality 24kHz audio output
      - GPU-accelerated processing
      - Asynchronous processing with webhooks

      **Model Types:**
      - `english`: English-only, faster processing
      - `multilingual`: 23 languages support

      **Languages Supported (multilingual model):**
      en, de, es, fr, it, pt, pl, tr, ru, nl, cs, ar, zh, ja, ko, hu, hi, and more
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              minLength: 1
              maxLength: 5000
              example: "Hello! Welcome to our AI-powered text-to-speech service."
              description: Text to convert to speech (1-5000 characters)
            language:
              type: string
              default: "en"
              example: "en"
              description: Language code (e.g., en, de, es, fr, it, pt, ja, zh, ko)
            model_type:
              type: string
              enum: [english, multilingual]
              default: "english"
              example: "english"
              description: Model type (english for English only, multilingual for 23 languages)
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
              example: "tts-request-123"
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
              example: "tts-request-123"
            job_id:
              type: string
              example: "550e8400-e29b-41d4-a716-446655440000"
            response:
              type: string
              format: uri
              example: "https://storage.example.com/generated-speech.wav"
              description: URL of the generated audio file
            message:
              type: string
              example: "success"
            run_time:
              type: number
              example: 1.234
            queue_time:
              type: number
              example: 0
            total_time:
              type: number
              example: 1.234
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
              example: "tts-request-123"
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
              example: "Invalid request: 'text' is a required property"
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
              example: "Failed to load Chatterbox model: CUDA out of memory"
    security:
      - ApiKeyAuth: []
    """
    text = data["text"]
    language = data.get("language", "en")
    model_type = data.get("model_type", "english")
    emotion_intensity = data.get("emotion_intensity", 1.0)

    logger.info(
        f"Job {job_id}: Received text-to-speech request for text: {text[:50]}... (language: {language})"
    )

    try:
        output_file = process_text_to_speech(
            text=text,
            job_id=job_id,
            language=language,
            emotion_intensity=emotion_intensity,
            model_type=model_type
        )
        logger.info(f"Job {job_id}: Text-to-speech generation completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(
            f"Job {job_id}: Generated audio uploaded to cloud storage: {cloud_url}"
        )

        return cloud_url, "/v1/chatterbox/text-to-speech", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during text-to-speech generation - {str(e)}")
        return str(e), "/v1/chatterbox/text-to-speech", 500
