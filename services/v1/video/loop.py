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

def process_video_loop(video_url, loop_count, job_id, webhook_url=None):
    """Loop a video file a specified number of times."""
    output_filename = f"{job_id}.mp4"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    try:
        # Download the video file once
        input_filename = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))

        # Generate a concat list file with the same file repeated loop_count times
        concat_file_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_loop_list.txt")
        with open(concat_file_path, 'w') as concat_file:
            for _ in range(loop_count):
                # Write absolute path to the concat list, repeated loop_count times
                concat_file.write(f"file '{os.path.abspath(input_filename)}'\n")

        # Use the concat demuxer to loop the video file without re-encoding
        (
            ffmpeg.input(concat_file_path, format='concat', safe=0).
                output(output_path, c='copy').
                run(overwrite_output=True)
        )

        # Clean up input file and concat list
        os.remove(input_filename)
        os.remove(concat_file_path)

        print(f"Video loop successful: {output_path}")

        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after looping.")

        return output_path
    except Exception as e:
        print(f"Video loop failed: {str(e)}")
        raise
