from flask import Flask, request, send_file
import whisper
from flask_cors import CORS
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os
import tempfile

app = Flask(__name__)
CORS(app)
# Load Whisper model once at startup
print("Loading Whisper model...")
model = whisper.load_model("small")
print("Model loaded!")

@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        print("no file")
        return "No file uploaded", 400

    uploaded_file = request.files["file"]
    input_file = f"temp_input_{uploaded_file.filename}"
    uploaded_file.save(input_file)

    # Prepare output temporary file
    output_file = f"temp_output_{uploaded_file.filename}"

    try:
        # 1️⃣ Transcribe video with word-level timestamps
        print("Transcribing video with word-level timestamps...")
        result = model.transcribe(input_file, word_timestamps=True)
        print("Transcription completed!")

        # 2️⃣ Load video
        video = VideoFileClip(input_file)

        # 3️⃣ Create subtitles
        subtitle_clips = []
        words_per_clip = 3
        max_gap = 0.5

        for segment in result["segments"]:
            words = segment.get("words", [])
            if not words:
                continue

            i = 0
            while i < len(words):
                phrase_words = words[i:i+words_per_clip]
                phrase_text = " ".join([w["word"] for w in phrase_words])
                phrase_start = phrase_words[0]["start"]
                phrase_end = phrase_words[-1]["end"]

                # Optional: limit max phrase duration
                if phrase_end - phrase_start > 5:
                    phrase_end = phrase_start + 5

                txt_clip = (
                    TextClip(
                        text=phrase_text,
                        font_size=24,
                        size=video.size,
                        method="caption",
                        color="white",
                    )
                    .with_position("center")
                    .with_start(phrase_start)
                    .with_end(phrase_end)
                )
                subtitle_clips.append(txt_clip)
                i += words_per_clip

        # 4️⃣ Combine video and subtitles
        final = CompositeVideoClip([video, *subtitle_clips])

        # 5️⃣ Export video
        print("Exporting video with subtitles...")
        final.write_videofile(output_file, codec="libx264", audio_codec="aac")

        # 6️⃣ Send video back as download
        return send_file(
            output_file, as_attachment=True, download_name="video_with_subs.mp4"
        )

    finally:
        # Cleanup temporary files
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)


if __name__ == "__main__":
    app.run(debug=True)
