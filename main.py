from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_video_info(url):
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = []

    for fmt in info.get("formats", []):
        height = fmt.get("height")
        filesize = fmt.get("filesize") or fmt.get("filesize_approx")

        if height:
            formats.append({
                "format_id": fmt.get("format_id"),
                "height": height,
                "ext": fmt.get("ext"),
                "filesize": filesize
            })

    return {
        "title": info.get("title", "Unknown"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "uploader": info.get("uploader"),
        "formats": formats
    }


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "Video Downloader API"
    })


@app.route("/api/info", methods=["POST"])
def info():

    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "URL is required"
        }), 400

    try:

        result = get_video_info(url)

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route("/api/download", methods=["POST"])
def download():

    data = request.get_json(silent=True) or {}

    url = data.get("url", "").strip()
    quality = data.get("quality", "best")

    if not url:
        return jsonify({
            "success": False,
            "error": "URL is required"
        }), 400

    file_id = str(uuid.uuid4())

    output_template = os.path.join(
        DOWNLOAD_DIR,
        file_id + ".%(ext)s"
    )

    if quality == "audio":

        ydl_format = "bestaudio/best"

        options = {
            "format": ydl_format,
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

    elif quality == "1080p":

        ydl_format = (
            "bestvideo[height<=1080]+bestaudio/"
            "best[height<=1080]"
        )

        options = {
            "format": ydl_format,
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

    elif quality == "720p":

        ydl_format = (
            "bestvideo[height<=720]+bestaudio/"
            "best[height<=720]"
        )

        options = {
            "format": ydl_format,
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

    elif quality == "480p":

        ydl_format = (
            "bestvideo[height<=480]+bestaudio/"
            "best[height<=480]"
        )

        options = {
            "format": ydl_format,
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

    elif quality == "360p":

        ydl_format = (
            "bestvideo[height<=360]+bestaudio/"
            "best[height<=360]"
        )

        options = {
            "format": ydl_format,
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

    else:

        options = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

    try:

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        downloaded_file = None

        for filename in os.listdir(DOWNLOAD_DIR):

            if filename.startswith(file_id + "."):
                downloaded_file = os.path.join(
                    DOWNLOAD_DIR,
                    filename
                )
                break

        if not downloaded_file:
            return jsonify({
                "success": False,
                "error": "Downloaded file was not found."
            }), 500

        return send_file(
            downloaded_file,
            as_attachment=True,
            download_name=(
                info.get("title", "video")
                + "."
                + downloaded_file.split(".")[-1]
            )
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
