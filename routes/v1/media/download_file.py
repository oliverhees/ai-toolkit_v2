from flask import Blueprint, send_file
from services.authentication import authenticate
import os
from config import LOCAL_STORAGE_PATH
import logging

v1_media_download_file_bp = Blueprint('v1_media_download_file', __name__)
logger = logging.getLogger(__name__)

@v1_media_download_file_bp.route('/v1/media/download/<filename>', methods=['GET'])
@authenticate
def download_file(filename):
    """
    Download a file from local storage
    ---
    Allows downloading generated files (audio, video, etc.) from the server
    """
    try:
        # Sanitize filename to prevent directory traversal
        filename = os.path.basename(filename)
        file_path = os.path.join(LOCAL_STORAGE_PATH, filename)

        if not os.path.exists(file_path):
            return {"error": "File not found"}, 404

        # Determine MIME type based on extension
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain'
        }

        ext = os.path.splitext(filename)[1].lower()
        mimetype = mime_types.get(ext, 'application/octet-stream')

        logger.info(f"Serving file: {filename} ({mimetype})")

        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        return {"error": str(e)}, 500
