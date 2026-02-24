import cv2
import sys
import numpy as np

def test_video_display(video_path):
    print(f"Testing video display for: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video properties:")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Total frames: {total_frames}")
    
    # Create window with specific properties
    window_name = 'Video Test - Press Q to quit'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    # Try to move window to front-center of screen
    cv2.moveWindow(window_name, 100, 100)
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video")
            break
            
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Frame {frame_count}/{total_frames}")
        
        # Add a bright border to make the window more visible
        frame = cv2.copyMakeBorder(frame, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=(0, 255, 0))
        
        # Add frame counter text
        cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display frame
        cv2.imshow(window_name, frame)
        
        # Wait for key press (30ms)
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            print("User pressed 'q' to quit")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Processed {frame_count} frames")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_video_display.py <video_path>")
        sys.exit(1)
    
    test_video_display(sys.argv[1]) 