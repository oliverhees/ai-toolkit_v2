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
import torch
import torchaudio
from config import LOCAL_STORAGE_PATH
from services.file_management import download_file

# Cache for loaded models to avoid reloading
_model_cache = {}


def get_chatterbox_model(model_type="english", device=None):
    """
    Load and cache Chatterbox TTS model.

    Args:
        model_type: "english" or "multilingual" (ignored - same model for all)
        device: Device to load model on ("cuda" or "cpu")

    Returns:
        Loaded Chatterbox model instance
    """
    global _model_cache

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # Use same model for all languages
    cache_key = f"chatterbox_{device}"

    if cache_key not in _model_cache:
        try:
            from chatterbox.tts import ChatterboxTTS
            _model_cache[cache_key] = ChatterboxTTS.from_pretrained(device=device)
            print(f"Chatterbox TTS model loaded on {device}")
        except Exception as e:
            raise Exception(f"Failed to load Chatterbox model: {str(e)}")

    return _model_cache[cache_key]


def process_text_to_speech(text, job_id, language="en", emotion_intensity=1.0, model_type="english"):
    """
    Convert text to speech using Chatterbox TTS.

    Args:
        text: Text to convert to speech
        job_id: Unique job identifier
        language: Language code (e.g., "en", "de", "es")
        emotion_intensity: Emotion exaggeration level (0.0 to 2.0)
        model_type: "english" or "multilingual"

    Returns:
        Path to generated audio file
    """
    output_filename = f"{job_id}_tts.wav"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    try:
        # Load model
        model = get_chatterbox_model(model_type=model_type)

        # Generate speech
        print(f"Generating speech for text: {text[:50]}... (language: {language}, model: {model_type})")

        # Generate audio waveform
        # Only multilingual model supports language parameter
        if model_type == "multilingual":
            wav = model.generate(text, language=language)
        else:
            # English model doesn't accept language parameter
            wav = model.generate(text)

        # Save audio file
        if isinstance(wav, torch.Tensor):
            # If wav is a tensor, save using torchaudio
            torchaudio.save(output_path, wav.unsqueeze(0) if wav.dim() == 1 else wav, 24000)
        else:
            # If wav is numpy array or other format
            import numpy as np
            if isinstance(wav, np.ndarray):
                wav_tensor = torch.from_numpy(wav)
                torchaudio.save(output_path, wav_tensor.unsqueeze(0) if wav_tensor.dim() == 1 else wav_tensor, 24000)

        print(f"Text-to-speech generation successful: {output_path}")

        # Verify output file exists
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after generation.")

        return output_path

    except Exception as e:
        print(f"Text-to-speech generation failed: {str(e)}")
        raise


def process_voice_cloning(text, voice_audio_url, job_id, language="en", emotion_intensity=1.0, model_type="multilingual"):
    """
    Clone a voice and generate speech using Chatterbox TTS.

    Args:
        text: Text to convert to speech
        voice_audio_url: URL of reference voice audio
        job_id: Unique job identifier
        language: Language code
        emotion_intensity: Emotion exaggeration level
        model_type: Model type to use

    Returns:
        Path to generated audio file with cloned voice
    """
    output_filename = f"{job_id}_voice_clone.wav"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)
    reference_audio_path = None

    try:
        # Download reference voice audio
        print(f"Downloading reference voice audio from: {voice_audio_url}")
        reference_audio_path = download_file(
            voice_audio_url,
            os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_reference")
        )

        # Load model
        model = get_chatterbox_model(model_type=model_type)

        # Load reference audio
        reference_wav, sample_rate = torchaudio.load(reference_audio_path)

        # Resample if necessary (Chatterbox expects 24kHz)
        if sample_rate != 24000:
            resampler = torchaudio.transforms.Resample(sample_rate, 24000)
            reference_wav = resampler(reference_wav)

        print(f"Generating speech with voice cloning for text: {text[:50]}...")

        # Generate speech with voice cloning
        wav = model.generate(
            text,
            reference_audio=reference_wav,
            language=language if model_type == "multilingual" else None
        )

        # Save audio file
        if isinstance(wav, torch.Tensor):
            torchaudio.save(output_path, wav.unsqueeze(0) if wav.dim() == 1 else wav, 24000)
        else:
            import numpy as np
            if isinstance(wav, np.ndarray):
                wav_tensor = torch.from_numpy(wav)
                torchaudio.save(output_path, wav_tensor.unsqueeze(0) if wav_tensor.dim() == 1 else wav_tensor, 24000)

        print(f"Voice cloning successful: {output_path}")

        # Clean up reference audio
        if reference_audio_path and os.path.exists(reference_audio_path):
            os.remove(reference_audio_path)

        # Verify output file exists
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after generation.")

        return output_path

    except Exception as e:
        # Clean up reference audio in case of error
        if reference_audio_path and os.path.exists(reference_audio_path):
            os.remove(reference_audio_path)

        print(f"Voice cloning failed: {str(e)}")
        raise
