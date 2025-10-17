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
from services.v1.video.add_audio import process_add_audio
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_video_add_audio_bp = Blueprint('v1_video_add_audio', __name__)
logger = logging.getLogger(__name__)

@v1_video_add_audio_bp.route('/v1/video/add_audio', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "audio_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url", "audio_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def add_audio_to_video(job_id, data):
    """
    Add or replace audio track in a video file.

    Args:
        job_id (str): Unique job identifier
        data (dict): Request JSON payload

    Returns:
        Tuple[dict, str, int]: (response_data, endpoint_path, status_code)
    """
    video_url = data['video_url']
    audio_url = data['audio_url']
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received add-audio request for video: {video_url}, audio: {audio_url}")

    try:
        output_file = process_add_audio(video_url, audio_url, job_id)
        logger.info(f"Job {job_id}: Audio addition process completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(f"Job {job_id}: Video with audio uploaded to cloud storage: {cloud_url}")

        return cloud_url, "/v1/video/add_audio", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during audio addition process - {str(e)}")
        return str(e), "/v1/video/add_audio", 500
