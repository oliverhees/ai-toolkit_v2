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



from flask import Blueprint
from app_utils import *
import logging
from services.v1.video.loop import process_video_loop
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_video_loop_bp = Blueprint('v1_video_loop', __name__)
logger = logging.getLogger(__name__)

@v1_video_loop_bp.route('/v1/video/loop', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "loop_count": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "description": "Number of times to loop the video (1-100)"
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url", "loop_count"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def loop_video(job_id, data):
    """
    Loop a video file multiple times
    ---
    tags:
      - Video
    summary: Loop Video File
    description: |
      Repeat a video file a specified number of times efficiently.

      **Features:**
      - Download video once, loop 1-100 times
      - No re-encoding (uses FFmpeg concat demuxer)
      - Output format: MP4
      - Supports webhook for async processing
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - video_url
            - loop_count
          properties:
            video_url:
              type: string
              format: uri
              example: "https://example.com/video.mp4"
              description: URL of the video file to loop
            loop_count:
              type: integer
              minimum: 1
              maximum: 100
              example: 3
              description: Number of times to repeat the video (1-100)
            webhook_url:
              type: string
              format: uri
              example: "https://your-app.com/webhook"
              description: Optional webhook URL for async processing
            id:
              type: string
              example: "video-loop-456"
              description: Custom identifier for tracking
    responses:
      200:
        description: Success - Video looped
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            response:
              type: string
              example: "file:///app/storage/output.mp4"
              description: URL of the looped video file
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
    video_url = data['video_url']
    loop_count = data['loop_count']
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received loop-video request for {video_url} with {loop_count} loops")

    try:
        output_file = process_video_loop(video_url, loop_count, job_id)
        logger.info(f"Job {job_id}: Video loop process completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(f"Job {job_id}: Looped video uploaded to cloud storage: {cloud_url}")

        return cloud_url, "/v1/video/loop", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during video loop process - {str(e)}")
        return str(e), "/v1/video/loop", 500
