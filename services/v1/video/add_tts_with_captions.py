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
from config import LOCAL_STORAGE_PATH
from services.file_management import download_file
from services.v1.chatterbox.tts import process_text_to_speech
from services.ass_toolkit import generate_ass_captions_v1


def process_add_tts_with_captions(
    video_url,
    text,
    job_id,
    language="de",
    emotion_intensity=0.5,
    model_type="multilingual",
    caption_settings=None,
    replace=None,
    exclude_time_ranges=None
):
    """
    Complete workflow: Generate TTS audio, add to video, and add karaoke captions.

    Args:
        video_url (str): URL of the video file (without audio)
        text (str): Text to convert to speech
        job_id (str): Unique job identifier
        language (str): Language code (e.g., "de", "en", "fr")
        emotion_intensity (float): TTS emotion level (0.25-2.0)
        model_type (str): TTS model type ("english" or "multilingual")
        caption_settings (dict): Caption styling options
        replace (list): Text replacements for captions
        exclude_time_ranges (list): Time ranges to exclude from captioning

    Returns:
        str: Path to final video with TTS audio and captions
    """
    video_path = None
    tts_audio_path = None
    video_with_audio_path = None
    ass_path = None

    try:
        print(f"[1/4] Generating TTS audio for text: {text[:50]}...")

        # Step 1: Generate TTS audio
        tts_audio_path = process_text_to_speech(
            text=text,
            job_id=job_id,
            language=language,
            emotion_intensity=emotion_intensity,
            model_type=model_type
        )
        print(f"TTS audio generated: {tts_audio_path}")

        print(f"[2/4] Downloading video from {video_url}")

        # Step 2: Download video
        video_path = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_video"))
        print(f"Video downloaded: {video_path}")

        print(f"[3/4] Adding TTS audio to video...")

        # Step 3: Add TTS audio to video
        video_with_audio_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_with_audio.mp4")

        video_input = ffmpeg.input(video_path)
        audio_input = ffmpeg.input(tts_audio_path)

        ffmpeg.output(
            video_input.video,
            audio_input.audio,
            video_with_audio_path,
            vcodec='copy',
            acodec='aac',
            shortest=None
        ).run(overwrite_output=True)

        print(f"Video with audio created: {video_with_audio_path}")

        print(f"[4/4] Generating karaoke captions...")

        # Step 4: Generate captions from the TTS audio
        # Use default settings if none provided
        if caption_settings is None:
            caption_settings = {
                "style": "karaoke",
                "position": "bottom_center",
                "alignment": "center",
                "line_color": "#FFFFFF",
                "word_color": "#FFFF00",
                "outline_color": "#000000",
                "font_family": "Arial",
                "font_size": 32,
                "bold": True,
                "outline_width": 3
            }

        # Ensure karaoke style is used (or another supported animated style)
        if "style" not in caption_settings:
            caption_settings["style"] = "karaoke"

        if replace is None:
            replace = []

        if exclude_time_ranges is None:
            exclude_time_ranges = []

        # Generate ASS captions file
        ass_path = generate_ass_captions_v1(
            video_url=video_with_audio_path,  # Use local path, not URL
            captions=None,  # Let it auto-transcribe
            settings=caption_settings,
            replace=replace,
            exclude_time_ranges=exclude_time_ranges,
            job_id=job_id,
            language=language
        )

        if isinstance(ass_path, dict) and 'error' in ass_path:
            raise Exception(f"Caption generation failed: {ass_path['error']}")

        print(f"ASS captions generated: {ass_path}")

        # Step 5: Render video with captions
        output_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_final.mp4")

        ffmpeg.input(video_with_audio_path).output(
            output_path,
            vf=f"subtitles='{ass_path}'",
            acodec='copy'
        ).run(overwrite_output=True)

        print(f"Final video with captions created: {output_path}")

        # Cleanup temporary files
        if tts_audio_path and os.path.exists(tts_audio_path):
            os.remove(tts_audio_path)
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if video_with_audio_path and os.path.exists(video_with_audio_path):
            os.remove(video_with_audio_path)
        if ass_path and os.path.exists(ass_path):
            os.remove(ass_path)

        return output_path

    except Exception as e:
        # Cleanup on error
        for path in [tts_audio_path, video_path, video_with_audio_path, ass_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

        print(f"Error in TTS + Caption workflow: {str(e)}")
        raise
