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



import os
import ffmpeg
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

def process_add_audio(video_url, audio_url, job_id, webhook_url=None):
    """Add or replace audio track in a video file."""
    output_filename = f"{job_id}.mp4"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    try:
        # Download video and audio files
        video_file = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_video"))
        audio_file = download_file(audio_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_audio"))

        # Use FFmpeg to combine video and audio
        # -c:v copy = copy video stream without re-encoding (fast)
        # -c:a aac = encode audio to AAC (compatible)
        # -map 0:v:0 = take video from first input
        # -map 1:a:0 = take audio from second input
        # -shortest = finish when shortest stream ends
        video_input = ffmpeg.input(video_file)
        audio_input = ffmpeg.input(audio_file)

        (
            ffmpeg
            .output(
                video_input.video,
                audio_input.audio,
                output_path,
                vcodec='copy',  # Copy video stream (no re-encoding)
                acodec='aac',   # Encode audio to AAC
                shortest=None   # Use full video length
            )
            .run(overwrite_output=True)
        )

        # Clean up input files
        os.remove(video_file)
        os.remove(audio_file)

        print(f"Audio addition successful: {output_path}")

        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after adding audio.")

        return output_path
    except Exception as e:
        print(f"Audio addition failed: {str(e)}")
        raise
