import random
import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import static_ffmpeg

# def split_into_frames(input_path, output_folder):
#     os.makedirs(output_folder, exist_ok=True)
#     os.system(f"static_ffmpeg -i {input_path} {output_folder}/frame_%04d.png")
#     result_label.config(text=f"Done! Video frames saved in {output_folder}/")
def split_into_frames(input_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    duration = get_video_duration(input_path)  # Get video duration
    frame_number = 0

    while frame_number < 100:  # Change the number of frames as needed
        random_scale = random.uniform(0.5, 2.0)  # Random scale factor
        random_frame_time = random.uniform(0, duration)
        frame_file = f"{output_folder}/frame_{frame_number:04d}.png"

        # Generate a frame at a random time with the random scale
        os.system(f"static_ffmpeg -i {input_path} -ss {random_frame_time} -vf scale=iw*{random_scale}:ih*{random_scale} -vframes 1 {frame_file}")
        frame_number += 1

    result_label.config(text=f"Done! Video frames with random sizes saved in {output_folder}/")

def get_video_duration(video_path):
    try:
        ffprobe_output = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path])
        duration = float(ffprobe_output)
    except subprocess.CalledProcessError:
        duration = 0.0  # Handle the case when FFprobe fails
    return duration
def choose_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.webm")])
    if file_path:
        output_folder = "koolframes"
        result_label.config(text=f"Splitting video into frames. Please wait...")
        split_into_frames(file_path, output_folder)
        frames_to_webm(output_folder,"koolvideo")
def frames_to_webm(input_folder, output_path):
    os.makedirs(output_path, exist_ok=True)
    os.system(f"static_ffmpeg -framerate 30 -i {input_folder}/frame_%04d.png -c:v libvpx -preset veryfast -b:v 1M -y {output_path}.webm")
    result_label.config(text=f"Done! Frames converted back to {output_path}")

# Create a simple GUI window
root = tk.Tk()
root.title("What the heii")

# Add a button to choose a file
choose_button = tk.Button(root, text="Choose Video File", command=choose_file)
choose_button.pack(pady=20)

# Label to display the result
result_label = tk.Label(root, text="", font=("Helvetica", 12))
result_label.pack()

root.mainloop()