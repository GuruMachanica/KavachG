import cv2
import numpy as np
import os

def create_test_video():
    # Create directory if it doesn't exist
    os.makedirs('sample_videos', exist_ok=True)
    
    # Video settings
    output_path = 'sample_videos/test_pattern.mp4'
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Creating test video at {output_path}...")
    
    try:
        # Generate frames
        for i in range(fps * duration):
            # Create a frame with moving rectangles
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add moving red rectangle (simulating fire)
            x = int(width/2 + np.sin(i/20.0) * 100)
            y = int(height/2 + np.cos(i/15.0) * 50)
            cv2.rectangle(frame, (x-30, y-30), (x+30, y+30), (0, 0, 255), -1)
            
            # Add some text
            cv2.putText(frame, 'Test Pattern', (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
            
        out.release()
        print("Test video created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating video: {str(e)}")
        return False
    finally:
        try:
            out.release()
        except:
            pass

if __name__ == "__main__":
    create_test_video() 