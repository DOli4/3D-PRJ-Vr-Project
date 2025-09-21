using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System;
using TMPro;
using System.Text;

[System.Serializable]
public class AnalysisData
{
    public float posture_percent;
    public float eye_contact_percent;
    public float gestures_percent;
    public string emotion;
    public float emotion_confidence;
    public float overall_score;
    public string status;
}

[System.Serializable]
public class FrameData
{
    public string image_data;
    public long timestamp;
}

[System.Serializable]
public class UserResponse
{
    public string user_id;
    public string name;
    public string email;
}

public class RealtimeAnalyzer : MonoBehaviour
{
    [Header("UI Elements")]
    public TextMeshProUGUI postureText;
    public TextMeshProUGUI eyeContactText;
    public TextMeshProUGUI gesturesText;
    public TextMeshProUGUI emotionText;
    public TextMeshProUGUI overallScoreText;
    
    [Header("Settings")]
    public string apiUrl = "http://127.0.0.1:8000/analyze-frame";
    public float updateInterval = 1f;
    public int cameraIndex = 0;
    
    private bool isAnalyzing = false;
    private Coroutine analysisCoroutine;
    private WebCamTexture webCamTexture;
    private Texture2D frameTexture;

    public void StartRealtimeAnalysis()
    {
        if (!isAnalyzing)
        {
            Debug.Log("[DEBUG] Starting realtime analysis and backend session");
            StartCoroutine(StartSessionAndCamera());
        }
    }
    
    private IEnumerator StartCamera()
    {
        WebCamDevice[] devices = WebCamTexture.devices;
        if (devices.Length == 0)
        {
            Debug.LogError("No cameras found");
            yield break;
        }
        
        string deviceName = devices[cameraIndex].name;
        webCamTexture = new WebCamTexture(deviceName, 640, 480, 30);
        webCamTexture.Play();
        
        yield return new WaitForSeconds(1f);
        
        frameTexture = new Texture2D(webCamTexture.width, webCamTexture.height);
        
        Debug.Log($"Camera started: {deviceName}");
        isAnalyzing = true;
        analysisCoroutine = StartCoroutine(AnalysisLoop());
    }

    public void StopRealtimeAnalysis()
    {
        if (isAnalyzing)
        {
            Debug.Log("[DEBUG] Stopping realtime analysis and ending backend session");
            isAnalyzing = false;
            if (analysisCoroutine != null)
            {
                StopCoroutine(analysisCoroutine);
            }
            if (webCamTexture != null)
            {
                webCamTexture.Stop();
                Destroy(webCamTexture);
            }
            
            // End session on backend
            StartCoroutine(EndSessionOnBackend());
        }
    }

    private IEnumerator AnalysisLoop()
    {
        while (isAnalyzing)
        {
            yield return StartCoroutine(CaptureAndAnalyze());
            yield return new WaitForSeconds(updateInterval);
        }
    }

    private IEnumerator CaptureAndAnalyze()
    {
        if (webCamTexture != null && webCamTexture.isPlaying)
        {
            frameTexture.SetPixels(webCamTexture.GetPixels());
            frameTexture.Apply();
            
            byte[] imageBytes = frameTexture.EncodeToJPG(75);
            string base64Image = Convert.ToBase64String(imageBytes);
            
            FrameData frameData = new FrameData
            {
                image_data = base64Image,
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
            };
            
            string jsonData = JsonUtility.ToJson(frameData);
            
            Debug.Log($"Calling API: {apiUrl}");
            using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        AnalysisData data = JsonUtility.FromJson<AnalysisData>(request.downloadHandler.text);
                        UpdateUI(data);
                    }
                    catch (Exception e)
                    {
                        Debug.LogError("JSON parse failed: " + e.Message);
                    }
                }
                else
                {
                    Debug.LogError("API failed: " + request.responseCode);
                }
            }
        }
    }

    private void UpdateUI(AnalysisData data)
    {
        if (postureText) postureText.text = $"Posture: {data.posture_percent:F1}%";
        if (eyeContactText) eyeContactText.text = $"Eye Contact: {data.eye_contact_percent:F1}%";
        if (gesturesText) gesturesText.text = $"Gestures: {data.gestures_percent:F1}%";
        if (emotionText) emotionText.text = $"Emotion: {data.emotion} ({data.emotion_confidence:F2})";
        if (overallScoreText) overallScoreText.text = $"Overall: {data.overall_score:F1}%";
    }

    private IEnumerator StartSessionAndCamera()
    {
        // Start backend session first
        yield return StartCoroutine(StartBackendSession());
        // Then start camera
        yield return StartCoroutine(StartCamera());
    }
    
    private IEnumerator StartBackendSession()
    {
        // Generate unique user ID for each session
        string uniqueId = System.DateTime.Now.Ticks.ToString();
        string userEmail = $"vr_user_{uniqueId}@test.com";
        string userId = $"vr_user_{uniqueId}";
        
        string userUrl = "http://127.0.0.1:8000/users/register";
        string userData = $"{{\"name\":\"VR User {uniqueId}\",\"email\":\"{userEmail}\"}}";
        
        Debug.Log($"[DEBUG] Creating unique user: {userId}");
        using (UnityWebRequest userRequest = UnityWebRequest.Post(userUrl, userData, "application/json"))
        {
            yield return userRequest.SendWebRequest();
            
            if (userRequest.result == UnityWebRequest.Result.Success)
            {
                // Extract user_id from response
                var response = JsonUtility.FromJson<UserResponse>(userRequest.downloadHandler.text);
                userId = response.user_id;
                Debug.Log($"[DEBUG] User created with ID: {userId}");
            }
            else
            {
                Debug.LogError("[ERROR] Failed to create user: " + userRequest.error);
                yield break;
            }
        }
        
        string sessionUrl = "http://127.0.0.1:8000/sessions/start";
        string sessionData = $"{{\"user_id\":\"{userId}\",\"role\":\"software_dev\",\"level\":1}}";
        
        Debug.Log("[DEBUG] Starting new session on backend...");
        using (UnityWebRequest sessionRequest = UnityWebRequest.Post(sessionUrl, sessionData, "application/json"))
        {
            yield return sessionRequest.SendWebRequest();
            
            if (sessionRequest.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("[SUCCESS] New backend session started");
                Debug.Log($"[DEBUG] Response: {sessionRequest.downloadHandler.text}");
            }
            else
            {
                Debug.LogError("[ERROR] Failed to start backend session: " + sessionRequest.error);
            }
        }
    }
    
    private IEnumerator EndSessionOnBackend()
    {
        string url = "http://127.0.0.1:8000/sessions/end";
        Debug.Log("[DEBUG] Ending session on backend: " + url);
        
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm(url, ""))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("[SUCCESS] Backend session ended");
            }
            else
            {
                Debug.LogError("[ERROR] Failed to end backend session: " + request.error);
            }
        }
    }

    void OnDestroy()
    {
        StopRealtimeAnalysis();
    }
}