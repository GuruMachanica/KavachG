import urllib.request
import os

def download_sample_video():
    # Create directory if it doesn't exist
    os.makedirs('sample_videos', exist_ok=True)
    
    # URL of a sample fire video (this is a small fire detection test video)
    video_url = "https://raw.githubusercontent.com/robmarkcole/fire-detection-from-images/master/fire_videos/fire1.mp4"
    output_path = "sample_videos/fire_test.mp4"
    
    print(f"Downloading sample video to {output_path}...")
    try:
        urllib.request.urlretrieve(video_url, output_path)
        print("Download completed successfully!")
        return True
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False

if __name__ == "__main__":
    download_sample_video() 