import os
import time
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Define the directory to store emergency videos.
EMERGENCY_DIR = "emergency_videos"
if not os.path.exists(EMERGENCY_DIR):
    os.makedirs(EMERGENCY_DIR)

# Mount the emergency_videos directory as static files.
# This allows the video file to be served at a known URL.
app.mount("/static/emergency-videos", StaticFiles(directory=EMERGENCY_DIR), name="emergency_videos")

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Accepts an uploaded mp4 video file, saves it with the current time in milliseconds as its name,
    and returns the generated file name.
    """
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Uploaded file must be an mp4 video")

    current_millis = str(int(time.time() * 1000))
    file_name = f"{current_millis}.mp4"
    file_path = os.path.join(EMERGENCY_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file_name}

@app.get("/emergency-videos/{video_id}", response_class=HTMLResponse)
async def get_video(video_id: str):
    """
    Retrieves the mp4 video file based on the provided video identifier (milliseconds) 
    and renders it within a webpage using an HTML video player.
    """
    # Ensure the file name has the proper .mp4 extension.
    file_name = f"{video_id}.mp4" if not video_id.endswith(".mp4") else video_id
    file_path = os.path.join(EMERGENCY_DIR, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")

    # Construct an HTML page embedding the video using the static file URL.
    html_content = f"""
    <html>
        <video width="640" height="480" controls>
          <source src="/static/emergency-videos/{file_name}" type="video/mp4">
          Your browser does not support the video tag.
        </video>
    </html>
    """
    return HTMLResponse(content=html_content)
