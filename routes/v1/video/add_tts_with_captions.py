# Copyright (c) 2025 NetzPrinz aka Oliver Hees
# Based on no-code-architects-toolkit by Stephen G. Pope
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


from flask import Blueprint
from app_utils import *
import logging
from services.v1.video.add_tts_with_captions import process_add_tts_with_captions
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_video_add_tts_with_captions_bp = Blueprint('v1_video_add_tts_with_captions', __name__)
logger = logging.getLogger(__name__)


@v1_video_add_tts_with_captions_bp.route('/v1/video/add-tts-with-captions', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {
            "type": "string",
            "format": "uri",
            "description": "URL of the video file (without audio)"
        },
        "text": {
            "type": "string",
            "minLength": 1,
            "maxLength": 5000,
            "description": "Text to convert to speech and use for captions"
        },
        "language": {
            "type": "string",
            "default": "de",
            "description": "Language code (e.g., de, en, fr, es)"
        },
        "emotion_intensity": {
            "type": "number",
            "minimum": 0.25,
            "maximum": 2.0,
            "default": 0.5,
            "description": "TTS emotion level (0.5=neutral, higher=more dramatic)"
        },
        "model_type": {
            "type": "string",
            "enum": ["english", "multilingual"],
            "default": "multilingual",
            "description": "TTS model type"
        },
        "caption_settings": {
            "type": "object",
            "description": "Caption styling options (defaults to TikTok-style karaoke)",
            "properties": {
                "style": {
                    "type": "string",
                    "enum": ["classic", "karaoke", "highlight", "underline", "word_by_word"],
                    "default": "karaoke"
                },
                "position": {
                    "type": "string",
                    "enum": [
                        "bottom_left", "bottom_center", "bottom_right",
                        "middle_left", "middle_center", "middle_right",
                        "top_left", "top_center", "top_right"
                    ],
                    "default": "bottom_center"
                },
                "alignment": {"type": "string", "enum": ["left", "center", "right"]},
                "line_color": {"type": "string"},
                "word_color": {"type": "string"},
                "outline_color": {"type": "string"},
                "font_family": {"type": "string"},
                "font_size": {"type": "integer"},
                "bold": {"type": "boolean"},
                "italic": {"type": "boolean"},
                "outline_width": {"type": "integer"},
                "shadow_offset": {"type": "integer"},
                "all_caps": {"type": "boolean"},
                "max_words_per_line": {"type": "integer"}
            }
        },
        "replace": {
            "type": "array",
            "description": "Text replacements for captions",
            "items": {
                "type": "object",
                "properties": {
                    "find": {"type": "string"},
                    "replace": {"type": "string"}
                },
                "required": ["find", "replace"]
            }
        },
        "exclude_time_ranges": {
            "type": "array",
            "description": "Time ranges to skip captioning",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "string"},
                    "end": {"type": "string"}
                },
                "required": ["start", "end"]
            }
        },
        "webhook_url": {
            "type": "string",
            "format": "uri",
            "description": "Optional webhook URL for async processing"
        },
        "id": {
            "type": "string",
            "description": "Custom identifier for tracking"
        }
    },
    "required": ["video_url", "text"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def add_tts_with_captions(job_id, data):
    """
    Add TTS audio and karaoke captions to video in one step
    ---
    tags:
      - Video
    summary: Add TTS audio + captions to video
    description: |
      Complete workflow: Generate TTS audio from text, add to video, and add synchronized karaoke captions.

      **Perfect for:**
      - TikTok-style videos with text-to-speech
      - Educational videos with synchronized captions
      - Automated video narration with subtitles

      **Process:**
      1. Generate TTS audio from your text (23 languages)
      2. Add TTS audio to your silent video
      3. Auto-generate karaoke captions synchronized with TTS
      4. Return final video with audio + captions

      **Default Style:** TikTok-style karaoke (white text, yellow highlight)
    """
    video_url = data['video_url']
    text = data['text']
    language = data.get('language', 'de')
    emotion_intensity = data.get('emotion_intensity', 0.5)
    model_type = data.get('model_type', 'multilingual')
    caption_settings = data.get('caption_settings')
    replace = data.get('replace', [])
    exclude_time_ranges = data.get('exclude_time_ranges', [])

    logger.info(f"Job {job_id}: TTS + Captions workflow started")
    logger.info(f"Video: {video_url}, Text: {text[:50]}..., Language: {language}")

    try:
        output_path = process_add_tts_with_captions(
            video_url=video_url,
            text=text,
            job_id=job_id,
            language=language,
            emotion_intensity=emotion_intensity,
            model_type=model_type,
            caption_settings=caption_settings,
            replace=replace,
            exclude_time_ranges=exclude_time_ranges
        )

        logger.info(f"Job {job_id}: TTS + Captions completed successfully: {output_path}")

        # Upload to cloud storage
        cloud_url = upload_file(output_path)
        logger.info(f"Job {job_id}: Final video uploaded: {cloud_url}")

        return cloud_url, "/v1/video/add-tts-with-captions", 200

    except Exception as e:
        logger.error(f"Job {job_id}: TTS + Captions workflow failed - {str(e)}")
        return str(e), "/v1/video/add-tts-with-captions", 500
