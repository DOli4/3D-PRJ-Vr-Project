using UnityEngine;
using UnityEngine.UI;
using TMPro;
using UnityEngine.Networking;
using System.Collections;

public class VRInterviewController : MonoBehaviour
{
    [Header("Analysis Components")]
    public RealtimeAnalyzer analyzer;
    
    [Header("VR UI Canvas")]
    public Canvas vrCanvas;
    public Transform leftHand;
    public Transform rightHand;
    
    [Header("Interview Controls")]
    public Button startButton;
    public Button stopButton;
    public TextMeshProUGUI statusText;
    
    [Header("Score Display")]
    public GameObject scorePanel;
    public TextMeshProUGUI finalScoreText;
    
    private bool interviewActive = false;
    private float sessionStartTime;
    private float totalScore = 0f;
    private int scoreCount = 0;

    void Start()
    {
        SetupVRUI();
        if (startButton) startButton.onClick.AddListener(StartInterview);
        if (stopButton) stopButton.onClick.AddListener(StopInterview);
    }

    void SetupVRUI()
    {
        // Position UI in VR space
        if (vrCanvas)
        {
            vrCanvas.renderMode = RenderMode.WorldSpace;
            vrCanvas.transform.position = Camera.main.transform.position + Camera.main.transform.forward * 2f;
            vrCanvas.transform.LookAt(Camera.main.transform);
            vrCanvas.transform.Rotate(0, 180, 0);
        }
    }

    public void StartInterview()
    {
        if (!interviewActive)
        {
            interviewActive = true;
            sessionStartTime = Time.time;
            totalScore = 0f;
            scoreCount = 0;
            
            // Start session on backend
            StartCoroutine(StartSessionOnBackend());
            
            if (analyzer) analyzer.StartRealtimeAnalysis();
            if (statusText) statusText.text = "Interview Active - Good Luck!";
            if (scorePanel) scorePanel.SetActive(false);
            
            Debug.Log("[DEBUG] VR Interview Started");
        }
    }

    public void StopInterview()
    {
        if (interviewActive)
        {
            interviewActive = false;
            
            if (analyzer) analyzer.StopRealtimeAnalysis();
            if (statusText) statusText.text = "Interview Completed";
            
            // Notify backend that session ended
            StartCoroutine(EndSessionOnBackend());
            
            ShowFinalResults();
            Debug.Log("VR Interview Stopped");
        }
    }

    void ShowFinalResults()
    {
        if (scorePanel) scorePanel.SetActive(true);
        
        float avgScore = scoreCount > 0 ? totalScore / scoreCount : 0f;
        float sessionDuration = Time.time - sessionStartTime;
        
        if (finalScoreText)
        {
            finalScoreText.text = $"Final Score: {avgScore:F1}%\n" +
                                 $"Duration: {sessionDuration:F0}s\n" +
                                 $"Samples: {scoreCount}";
        }
    }

    // Call this from RealtimeAnalyzer to track scores
    public void UpdateSessionScore(float score)
    {
        if (interviewActive)
        {
            totalScore += score;
            scoreCount++;
        }
    }

    void Update()
    {
        // VR hand tracking for UI interaction
        if (interviewActive && leftHand && rightHand)
        {
            // Basic hand gesture detection could go here
            CheckHandGestures();
        }
    }

    void CheckHandGestures()
    {
        // Simple gesture detection for VR
        // This is where you'd add more sophisticated gesture analysis
        Vector3 leftPos = leftHand.position;
        Vector3 rightPos = rightHand.position;
        
        // Example: Detect if hands are in "professional" position
        bool handsInGoodPosition = leftPos.y > Camera.main.transform.position.y - 0.3f &&
                                  rightPos.y > Camera.main.transform.position.y - 0.3f;
        
        // This data could be sent to your backend for additional analysis
    }

    private System.Collections.IEnumerator EndSessionOnBackend()
    {
        string url = "http://127.0.0.1:8000/sessions/end";
        Debug.Log("[DEBUG] Attempting to end session on backend: " + url);
        
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm(url, ""))
        {
            Debug.Log("[DEBUG] Sending POST request to backend...");
            yield return request.SendWebRequest();
            
            Debug.Log("[DEBUG] Request completed. Result: " + request.result);
            Debug.Log("[DEBUG] Response Code: " + request.responseCode);
            Debug.Log("[DEBUG] Response Text: " + request.downloadHandler.text);
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("[SUCCESS] Session ended successfully on backend");
            }
            else
            {
                Debug.LogError("[ERROR] Failed to end session on backend: " + request.error);
                Debug.LogError("[ERROR] Response: " + request.downloadHandler.text);
            }
        }
    }

    private System.Collections.IEnumerator StartSessionOnBackend()
    {
        // First create a user
        string userUrl = "http://127.0.0.1:8000/users/register";
        string userData = "{\"name\":\"VR User\",\"email\":\"vr@test.com\"}";
        
        Debug.Log("[DEBUG] Creating user on backend...");
        using (UnityWebRequest userRequest = UnityWebRequest.Post(userUrl, userData, "application/json"))
        {
            yield return userRequest.SendWebRequest();
            
            if (userRequest.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("[ERROR] Failed to create user: " + userRequest.error);
                yield break;
            }
        }
        
        // Then start session
        string sessionUrl = "http://127.0.0.1:8000/sessions/start";
        string sessionData = "{\"user_id\":\"vr_user\",\"role\":\"software_dev\",\"level\":1}";
        
        Debug.Log("[DEBUG] Starting session on backend...");
        using (UnityWebRequest sessionRequest = UnityWebRequest.Post(sessionUrl, sessionData, "application/json"))
        {
            yield return sessionRequest.SendWebRequest();
            
            if (sessionRequest.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("[SUCCESS] Session started on backend");
                Debug.Log("[DEBUG] Response: " + sessionRequest.downloadHandler.text);
            }
            else
            {
                Debug.LogError("[ERROR] Failed to start session: " + sessionRequest.error);
                Debug.LogError("[ERROR] Response: " + sessionRequest.downloadHandler.text);
            }
        }
    }

    void OnDestroy()
    {
        if (interviewActive)
        {
            StopInterview();
        }
    }
}