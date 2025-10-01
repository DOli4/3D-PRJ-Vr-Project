using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using Newtonsoft.Json;

[System.Serializable]
public class FrameAnalysis
{
    public string timestamp;
    public float posture_percent;
    public float eye_contact_percent;
    public float gestures_percent;
    public string emotion;
    public float emotion_confidence;
    public float overall_score;
    public string status;
}

public class RealtimeAnalyzer : MonoBehaviour
{
    [Header("API Configuration")]
    public string apiBaseUrl = "http://127.0.0.1:8000";
    
    [Header("Update Settings")]
    public float updateInterval = 1.0f; // Update every second
    
    [Header("UI Elements")]
    public Text postureText;
    public Text eyeContactText;
    public Text gesturesText;
    public Text emotionText;
    public Text overallScoreText;
    public Slider postureSlider;
    public Slider eyeContactSlider;
    public Slider gesturesSlider;
    public Slider overallScoreSlider;
    
    [Header("Current Analysis")]
    public FrameAnalysis currentAnalysis;
    
    private bool isAnalyzing = false;
    private Coroutine analysisCoroutine;
    
    void Start()
    {
        // Initialize UI
        UpdateUI(new FrameAnalysis());
    }
    
    public void StartRealtimeAnalysis()
    {
        if (isAnalyzing) return;
        
        StartCoroutine(StartCameraCoroutine());
    }
    
    public void StopRealtimeAnalysis()
    {
        if (!isAnalyzing) return;
        
        StartCoroutine(StopCameraCoroutine());
    }
    
    private IEnumerator StartCameraCoroutine()
    {
        Debug.Log("Starting real-time analysis...");
        
        // Start camera
        using (UnityWebRequest request = new UnityWebRequest($"{apiBaseUrl}/frames/start", "POST"))
        {
            request.downloadHandler = new DownloadHandlerBuffer();
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Camera started successfully");
                isAnalyzing = true;
                analysisCoroutine = StartCoroutine(AnalysisLoop());
            }
            else
            {
                Debug.LogError($"Failed to start camera: {request.error}");
            }
        }
    }
    
    private IEnumerator StopCameraCoroutine()
    {
        Debug.Log("Stopping real-time analysis...");
        
        isAnalyzing = false;
        if (analysisCoroutine != null)
        {
            StopCoroutine(analysisCoroutine);
        }
        
        // Stop camera
        using (UnityWebRequest request = new UnityWebRequest($"{apiBaseUrl}/frames/stop", "POST"))
        {
            request.downloadHandler = new DownloadHandlerBuffer();
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Camera stopped successfully");
            }
            else
            {
                Debug.LogError($"Failed to stop camera: {request.error}");
            }
        }
    }
    
    private IEnumerator AnalysisLoop()
    {
        while (isAnalyzing)
        {
            yield return StartCoroutine(GetFrameAnalysis());
            yield return new WaitForSeconds(updateInterval);
        }
    }
    
    private IEnumerator GetFrameAnalysis()
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{apiBaseUrl}/frames"))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    currentAnalysis = JsonConvert.DeserializeObject<FrameAnalysis>(request.downloadHandler.text);
                    UpdateUI(currentAnalysis);
                    
                    // Log for debugging
                    Debug.Log($"Analysis: Posture {currentAnalysis.posture_percent}% | " +
                             $"Eye Contact {currentAnalysis.eye_contact_percent}% | " +
                             $"Gestures {currentAnalysis.gestures_percent}% | " +
                             $"Emotion {currentAnalysis.emotion} | " +
                             $"Overall {currentAnalysis.overall_score}%");
                }
                catch (Exception e)
                {
                    Debug.LogError($"Failed to parse analysis: {e.Message}");
                }
            }
            else
            {
                Debug.LogError($"Frame analysis request failed: {request.error}");
            }
        }
    }
    
    private void UpdateUI(FrameAnalysis analysis)
    {
        // Update text elements
        if (postureText != null)
            postureText.text = $"Posture: {analysis.posture_percent:F1}%";
        
        if (eyeContactText != null)
            eyeContactText.text = $"Eye Contact: {analysis.eye_contact_percent:F1}%";
        
        if (gesturesText != null)
            gesturesText.text = $"Gestures: {analysis.gestures_percent:F1}%";
        
        if (emotionText != null)
            emotionText.text = $"Emotion: {analysis.emotion} ({analysis.emotion_confidence:F2})";
        
        if (overallScoreText != null)
            overallScoreText.text = $"Overall: {analysis.overall_score:F1}% ({GetGrade(analysis.overall_score)})";
        
        // Update sliders
        if (postureSlider != null)
            postureSlider.value = analysis.posture_percent / 100f;
        
        if (eyeContactSlider != null)
            eyeContactSlider.value = analysis.eye_contact_percent / 100f;
        
        if (gesturesSlider != null)
            gesturesSlider.value = analysis.gestures_percent / 100f;
        
        if (overallScoreSlider != null)
            overallScoreSlider.value = analysis.overall_score / 100f;
    }
    
    private string GetGrade(float score)
    {
        if (score >= 90) return "A+";
        if (score >= 85) return "A";
        if (score >= 80) return "A-";
        if (score >= 75) return "B+";
        if (score >= 70) return "B";
        if (score >= 65) return "B-";
        if (score >= 60) return "C+";
        if (score >= 55) return "C";
        if (score >= 50) return "C-";
        return "F";
    }
    
    void OnDestroy()
    {
        if (isAnalyzing)
        {
            StartCoroutine(StopCameraCoroutine());
        }
    }
}