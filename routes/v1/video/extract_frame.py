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
from services.v1.video.frame_extraction import _extract_frame_at_position
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_video_extract_frame_bp = Blueprint('v1_video_extract_frame', __name__)
logger = logging.getLogger(__name__)


@v1_video_extract_frame_bp.route('/v1/video/extract-frame', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {
            "type": "string",
            "format": "uri",
            "description": "URL of the video file"
        },
        "position": {
            "type": "string",
            "enum": ["first", "middle", "last"],
            "default": "first",
            "description": "Which frame to extract (first, middle, or last)"
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
    "required": ["video_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def extract_frame(job_id, data):
    """
    Extract a specific frame from a video
    ---
    tags:
      - Video
    summary: Extract frame from video
    description: |
      Extract the first, middle, or last frame from a video as an image.

      **Features:**
      - Extract first frame (at 0.1s)
      - Extract middle frame (at 50% of duration)
      - Extract last frame (at duration - 0.1s)
      - Output format: JPEG
      - Automatic video duration detection

      **Use Cases:**
      - Create video thumbnails
      - Extract keyframes for previews
      - Get end-frame for video loops
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - video_url
          properties:
            video_url:
              type: string
              format: uri
              example: "https://example.com/video.mp4"
              description: URL of the video file
            position:
              type: string
              enum: [first, middle, last]
              default: first
              example: "last"
              description: Which frame to extract
            webhook_url:
              type: string
              format: uri
              example: "https://your-app.com/webhook"
              description: Optional webhook URL for async processing
            id:
              type: string
              example: "frame-extract-123"
              description: Custom identifier for tracking
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            response:
              type: string
              format: uri
              example: "https://storage.example.com/last_frame.jpg"
              description: URL of the extracted frame image
      202:
        description: Accepted for async processing
      400:
        description: Bad Request
      401:
        description: Unauthorized
      500:
        description: Internal Server Error
    security:
      - ApiKeyAuth: []
    """
    video_url = data['video_url']
    position = data.get('position', 'first')

    logger.info(f"Job {job_id}: Extracting {position} frame from video: {video_url}")

    try:
        frame_path = _extract_frame_at_position(video_url, job_id, position)
        logger.info(f"Job {job_id}: Frame extracted successfully")

        cloud_url = upload_file(frame_path)
        logger.info(f"Job {job_id}: Frame uploaded to cloud storage: {cloud_url}")

        return cloud_url, "/v1/video/extract-frame", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error extracting frame - {str(e)}")
        return str(e), "/v1/video/extract-frame", 500
