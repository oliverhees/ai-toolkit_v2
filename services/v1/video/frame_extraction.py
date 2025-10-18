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


import os
import ffmpeg
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH


def extract_first_frame(video_url, job_id):
    """
    Extract the first frame from a video.

    Args:
        video_url (str): URL of the video
        job_id (str): Unique job identifier

    Returns:
        str: Path to the extracted frame image
    """
    return _extract_frame_at_position(video_url, job_id, "first")


def extract_middle_frame(video_url, job_id):
    """
    Extract the middle frame from a video.

    Args:
        video_url (str): URL of the video
        job_id (str): Unique job identifier

    Returns:
        str: Path to the extracted frame image
    """
    return _extract_frame_at_position(video_url, job_id, "middle")


def extract_last_frame(video_url, job_id):
    """
    Extract the last frame from a video.

    Args:
        video_url (str): URL of the video
        job_id (str): Unique job identifier

    Returns:
        str: Path to the extracted frame image
    """
    return _extract_frame_at_position(video_url, job_id, "last")


def _extract_frame_at_position(video_url, job_id, position):
    """
    Internal function to extract a frame at a specific position.

    Args:
        video_url (str): URL of the video
        job_id (str): Unique job identifier
        position (str): "first", "middle", or "last"

    Returns:
        str: Path to the extracted frame image
    """
    # Download the video
    video_path = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))

    # Set output path
    frame_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_{position}_frame.jpg")

    try:
        # Get video duration using ffprobe
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])

        # Calculate timestamp based on position
        if position == "first":
            timestamp = 0.1  # Slightly after start to ensure valid frame
        elif position == "middle":
            timestamp = duration / 2
        elif position == "last":
            timestamp = max(0, duration - 0.1)  # Slightly before end
        else:
            raise ValueError(f"Invalid position: {position}")

        print(f"Extracting {position} frame at {timestamp}s from video (duration: {duration}s)")

        # Extract frame using ffmpeg
        (
            ffmpeg
            .input(video_path, ss=timestamp)
            .output(frame_path, vframes=1, format='image2', vcodec='mjpeg')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        # Clean up video file
        os.remove(video_path)

        # Verify frame was created
        if not os.path.exists(frame_path):
            raise FileNotFoundError(f"Frame file {frame_path} was not created")

        return frame_path

    except Exception as e:
        print(f"Frame extraction failed: {str(e)}")
        # Clean up on error
        if os.path.exists(video_path):
            os.remove(video_path)
        raise
