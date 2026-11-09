
import streamlit as st
import os
import subprocess
import tempfile
import cv2

st.set_page_config(page_title="MediaForge AI", page_icon="🎬", layout="wide")
st.title("🎬 MediaForge AI - All-in-One AI Media Studio")
st.markdown("**Forge Any Media. In Seconds.** | 12 Features - Basic + Smart AI")

def run_ffmpeg(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def get_video_info(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    size = os.path.getsize(path)/(1024*1024)
    dur = frames/fps if fps else 0
    return f"{w}x{h}, {round(dur,1)}s, {round(size,2)}MB, {round(fps,1)} FPS"

uploaded = st.file_uploader("Upload Video", type=["mp4","mov","mkv","webm","avi"])

if not uploaded:
    st.info("Upload a video to start.")
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
    tmp.write(uploaded.read())
    INPUT = tmp.name

st.video(INPUT)
st.caption(get_video_info(INPUT))

feature = st.selectbox("Choose Feature", [
    "1. Trim Video",
    "2. Convert Format",
    "3. Watermark",
    "4. Speed + Reverse",
    "5. GIF + Thumbnail",
    "6. AI Subtitles (Whisper)",
    "7. Reels Maker 9:16",
    "8. Smart Compression",
    "9. Cinematic Filter",
    "10. Denoise Video + Audio",
    "11. Face Blur",
    "12. Extract Audio + Mute"
])

# 1 TRIM
if "1. Trim" in feature:
    start = st.number_input("Start sec", 0.0, 1000.0, 0.0)
    end = st.number_input("End sec", 1.0, 1000.0, 5.0)
    if st.button("Trim Now"):
        out = "trimmed.mp4"
        cmd = ["ffmpeg","-y","-ss",str(start),"-to",str(end),"-i",INPUT,"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]
        if run_ffmpeg(cmd):
            st.success("Done!")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)

# 2 CONVERT
if "2. Convert" in feature:
    st.info(f"Metadata: {get_video_info(INPUT)}")
    fmt = st.selectbox("Convert To", ["mp4","webm","avi","mov"])
    if st.button("Convert Now"):
        out = f"converted.{fmt}"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,out]):
            st.success("Converted!")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)

# 3 WATERMARK
if "3. Watermark" in feature:
    text = st.text_input("Watermark Text", "MediaForge AI")
    if st.button("Add Watermark"):
        out = "watermarked.mp4"
        vf = f"drawtext=text='{text}':fontcolor=white@0.6:fontsize=30:x=w-tw-10:y=h-th-10"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]):
            st.success("Done!")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)

# 4 SPEED
if "4. Speed" in feature:
    speed = st.slider("Speed", 0.5, 2.0, 1.5)
    if st.button("Change Speed"):
        out = "speed.mp4"
        cmd = ["ffmpeg","-y","-i",INPUT,"-filter_complex",f"[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]
        if run_ffmpeg(cmd):
            st.success("Done!")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)
    if st.button("Reverse Video"):
        out = "reversed.mp4"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-vf","reverse","-af","areverse","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]):
            st.success("Done!")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)

# 5 GIF
if "5. GIF" in feature:
    if st.button("Make GIF"):
        out = "output.gif"
        if run_ffmpeg(["ffmpeg","-y","-ss","0","-t","3","-i",INPUT,"-vf","fps=10,scale=480:-1:flags=lanczos","-loop","0",out]):
            st.success("Done!")
            st.image(out)
            with open(out,"rb") as f: st.download_button("Download GIF", f, file_name=out)
    if st.button("Make Thumbnail"):
        cap = cv2.VideoCapture(INPUT)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 30)
        ret, frame = cap.read()
        cap.release()
        if ret:
            cv2.imwrite("thumb.jpg", frame)
            st.image("thumb.jpg")
            with open("thumb.jpg","rb") as f: st.download_button("Download Thumb", f, file_name="thumb.jpg")

# 6 SUBTITLES
if "6. AI Subtitles" in feature:
    st.warning("Need speech in video. Fan video = empty subtitles.")
    if st.button("Generate Subtitles"):
        with st.spinner("Whisper working..."):
            import whisper
            model = whisper.load_model("tiny")
            result = model.transcribe(INPUT, fp16=False)
            st.write(result["text"])
            with open("subs.srt","w") as f:
                for i, seg in enumerate(result["segments"]):
                    def fmt(t):
                        h=int(t//3600); m=int((t%3600)//60); s=int(t%60); ms=int((t%1)*1000)
                        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
                    f.write(f"{i+1}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n{seg['text'].strip()}\n\n")
            out = "subtitled.mp4"
            if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-vf","subtitles=subs.srt","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]):
                st.success("Done!")
                st.video(out)
                with open(out,"rb") as f: st.download_button("Download Video", f, file_name=out)

# 7 REELS
if "7. Reels" in feature:
    if st.button("Make Reel"):
        out = "reel.mp4"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-vf","crop=ih*9/16:ih,scale=1080:1920","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]):
            st.success("Reel Done 1080x1920")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download Reel", f, file_name=out)

# 8 SMART COMPRESS
if "8. Smart" in feature:
    target = st.slider("Target MB", 1, 50, 10)
    if st.button(f"Compress to {target}MB"):
        cap = cv2.VideoCapture(INPUT)
        fps = cap.get(cv2.CAP_PROP_FPS); frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.release()
        dur = frames/fps if fps else 10
        bitrate = max(200, int((target * 8192 / dur) - 128))
        st.info(f"Bitrate: {bitrate} kbps")
        out = "compressed_smart.mp4"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-b:v",f"{bitrate}k","-b:a","128k","-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",out]):
            st.success(f"Done! Size: {os.path.getsize(out)/(1024*1024):.2f} MB")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)

# 9 FILTER
if "9. Cinematic" in feature:
    if st.button("Apply Cinematic"):
        out = "filtered.mp4"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-vf","eq=brightness=0.05:contrast=1.25:saturation=1.35","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]):
            st.success("Done!")
            st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)

# 10 DENOISE
if "10. Denoise" in feature:
    if st.button("Denoise Video"):
        out = "denoised_video.mp4"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-vf","hqdn3d=1.5:1.5:6:6","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]):
            st.success("Done!"); st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)
    if st.button("Denoise Audio"):
        out = "denoised_audio.mp4"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-af","afftdn","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out]):
            st.success("Done!"); st.video(out)
            with open(out,"rb") as f: st.download_button("Download", f, file_name=out)

# 11 FACE BLUR
if "11. Face Blur" in feature:
    if st.button("Blur Faces"):
        with st.spinner("Detecting faces..."):
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            cap = cv2.VideoCapture(INPUT)
            fps = cap.get(cv2.CAP_PROP_FPS); w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out_writer = cv2.VideoWriter("temp_blur.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            while True:
                ret, frame = cap.read()
                if not ret: break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                for (x,y,fw,fh) in faces:
                    roi = frame[y:y+fh, x:x+fw]
                    frame[y:y+fh, x:x+fw] = cv2.GaussianBlur(roi, (99,99), 30)
                out_writer.write(frame)
            cap.release(); out_writer.release()
            final_out = "face_blurred.mp4"
            run_ffmpeg(["ffmpeg","-y","-i","temp_blur.mp4","-i",INPUT,"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-map","0:v:0","-map","1:a:0","-shortest","-movflags","+faststart",final_out])
            st.success("Done!"); st.video(final_out)
            with open(final_out,"rb") as f: st.download_button("Download", f, file_name=final_out)

# 12 AUDIO
if "12. Extract" in feature:
    if st.button("Extract MP3"):
        out = "audio.mp3"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-vn","-ab","192k",out]):
            st.success("Done!"); st.audio(out)
            with open(out,"rb") as f: st.download_button("Download MP3", f, file_name=out)
    if st.button("Mute Video"):
        out = "muted.mp4"
        if run_ffmpeg(["ffmpeg","-y","-i",INPUT,"-an","-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",out]):
            st.success("Done!"); st.video(out)
            with open(out,"rb") as f: st.download_button("Download Muted", f, file_name=out)

st.caption("MediaForge AI - Built in Colab, Deployed with Streamlit")
