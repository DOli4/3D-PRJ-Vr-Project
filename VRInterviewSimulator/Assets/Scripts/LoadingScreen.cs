using UnityEngine;
using UnityEngine.Video;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Collections;

public class LoadingScreen : MonoBehaviour
{
    [SerializeField] private VideoPlayer videoPlayer;
    [SerializeField] private GameObject loadingUI;
    [SerializeField] private Slider progressBar;
    [SerializeField] private Text loadingText;
    [SerializeField] private float minimumLoadTime = 2f;
    [SerializeField] private string targetSceneName = "EJE-TestingScene";
    
    private string targetScene;
    private float startTime;
    
    void Start()
    {
        Debug.Log("LoadingScreen Start called");
        startTime = Time.time;
        targetScene = PlayerPrefs.GetString("TargetScene", targetSceneName);
        
        if (videoPlayer != null)
        {
            Debug.Log("VideoPlayer found, starting playback");
            
            // Check if video clip is assigned
            if (videoPlayer.clip == null)
            {
                Debug.LogError("VideoPlayer has no video clip assigned!");
                return;
            }
            
            // Setup video player
            videoPlayer.renderMode = VideoRenderMode.CameraFarPlane;
            videoPlayer.skipOnDrop = true;
            videoPlayer.isLooping = true;
            videoPlayer.playOnAwake = false;
            
            // Prepare and play
            videoPlayer.Prepare();
            videoPlayer.Play();
            
            Debug.Log($"Video clip: {videoPlayer.clip.name}, Length: {videoPlayer.clip.length}s");
        }
        else
        {
            Debug.LogError("VideoPlayer is null!");
        }
        
        StartCoroutine(LoadSceneAsync());
    }
    
    private IEnumerator LoadSceneAsync()
    {
        Debug.Log($"Loading scene: {targetScene}");
        AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(targetScene);
        
        if (asyncLoad == null)
        {
            Debug.LogError($"Failed to load scene: {targetScene}");
            yield break;
        }
        
        asyncLoad.allowSceneActivation = false;
        
        while (!asyncLoad.isDone)
        {
            float progress = Mathf.Clamp01(asyncLoad.progress / 0.9f);
            Debug.Log($"Loading progress: {progress * 100:F0}%");
            
            if (progressBar != null)
                progressBar.value = progress;
                
            if (loadingText != null)
                loadingText.text = $"Loading... {(progress * 100):F0}%";
            
            bool minTimeReached = (Time.time - startTime) >= minimumLoadTime;
            
            if (asyncLoad.progress >= 0.9f && minTimeReached)
            {
                Debug.Log("Scene ready, activating...");
                asyncLoad.allowSceneActivation = true;
            }
            
            yield return null;
        }
    }
}