import whisper
from moviepy import VideoFileClip, TextClip, CompositeVideoClip


video_file = "Video2.mov"
output_file = "test_with_subs.mp4"

print("Loading Whisper model...")
model = whisper.load_model("small")

print("Transcribing video with word-level timestamps...")
result = model.transcribe(video_file, word_timestamps=True)
print("Transcription completed!")


video = VideoFileClip(video_file)

subtitle_clips = []
words_per_clip = 3  
max_gap = 0.5       

for segment in result["segments"]:
    words = segment.get("words", [])
    if not words:
        continue

    i = 0
    while i < len(words):
        # Take next 2–3 words
        phrase_words = words[i:i+words_per_clip]
        phrase_text = " ".join([w["word"] for w in phrase_words])
        phrase_start = phrase_words[0]["start"]
        phrase_end = phrase_words[-1]["end"]

        # If words are too far apart, adjust end time
        if phrase_end - phrase_start > 5:  # optional max phrase duration
            phrase_end = phrase_start + 5

        txt_clip = (TextClip(text=phrase_text, font_size=24,size=video.size, method='caption', color='white')
                    .with_position('center')
                    .with_start(phrase_start)
                    .with_end(phrase_end))
        subtitle_clips.append(txt_clip)

        i += words_per_clip


final = CompositeVideoClip([video, *subtitle_clips])


print("Exporting video with subtitles...")
final.write_videofile(output_file, codec="libx264", audio_codec="aac")

print(f"Video with subtitles saved as {output_file}")
