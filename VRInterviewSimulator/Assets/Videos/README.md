# Loading Screen Videos

Place your MP4 loading screen videos in this folder.

## Setup Instructions:

1. Add your MP4 video file to this folder
2. Create a new scene called "LoadingScene"
3. Add a Canvas with:
   - VideoPlayer component (assign your MP4)
   - LoadingScreen script
   - Progress bar (optional)
   - Loading text (optional)
4. Use SceneLoader.LoadSceneWithLoading("YourTargetScene") to trigger loading

## Video Specs:
- Format: MP4
- Resolution: Up to 4K (3840x2160) supported
- Duration: 3-10 seconds (looping)
- Compression: H.264

## 4K Video Optimization:
- Set VideoPlayer Quality to "Fast" in Unity
- Enable "Skip On Drop" for smooth playback
- Consider using Render Texture for better performance
- Test on target VR device for performance