using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

[System.Serializable]
public class AnalysisReport
{
    public string session_id;
    public string timestamp;
    public FacialAnalysis facial_analysis;
    public BodyLanguageAnalysis body_language;
    public AudioEmotionAnalysis audio_emotion;
    public float overall_score;
    public string[] recommendations;
}

[System.Serializable]
public class FacialAnalysis
{
    public float score;
    public string dominant_emotion;
    public float confidence;
}

[System.Serializable]
public class BodyLanguageAnalysis
{
    public float score;
    public string feedback;
}

[System.Serializable]
public class AudioEmotionAnalysis
{
    public float score;
    public string emotion;
    public float confidence;
}

[System.Serializable]
public class AnalysisRequest
{
    public string session_id;
    public int duration = 60;
}

[System.Serializable]
public class AudioAnalysisRequest
{
    public string session_id;
    public string audio_file_path;
}

public class InterviewAnalyzer : MonoBehaviour
{
    [Header("API Configuration")]
    public string apiBaseUrl = "http://127.0.0.1:8000";
    
    [Header("Analysis Settings")]
    public int analysisDuration = 60;
    public string currentSessionId;
    
    [Header("Events")]
    public UnityEngine.Events.UnityEvent<AnalysisReport> OnAnalysisComplete;
    public UnityEngine.Events.UnityEvent<string> OnAnalysisError;
    
    private bool isAnalyzing = false;
    
    void Start()
    {
        if (string.IsNullOrEmpty(currentSessionId))
        {
            currentSessionId = "unity_session_" + DateTime.Now.Ticks;
        }
    }
    
    public void StartComprehensiveAnalysis()
    {
        if (isAnalyzing)
        {
            Debug.LogWarning("Analysis already in progress");
            return;
        }
        
        StartCoroutine(StartAnalysisCoroutine());
    }
    
    public void AnalyzeAudioFile(string audioFilePath)
    {
        StartCoroutine(AnalyzeAudioCoroutine(audioFilePath));
    }
    
    public void CheckAnalysisStatus()
    {
        StartCoroutine(CheckStatusCoroutine());
    }
    
    private IEnumerator StartAnalysisCoroutine()
    {
        isAnalyzing = true;
        Debug.Log($"Starting comprehensive analysis for session: {currentSessionId}");
        
        var request = new AnalysisRequest
        {
            session_id = currentSessionId,
            duration = analysisDuration
        };
        
        string jsonData = JsonConvert.SerializeObject(request);
        
        using (UnityWebRequest webRequest = new UnityWebRequest($"{apiBaseUrl}/analysis/start", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");
            
            yield return webRequest.SendWebRequest();
            
            isAnalyzing = false;
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonConvert.DeserializeObject<dynamic>(webRequest.downloadHandler.text);
                    var report = JsonConvert.DeserializeObject<AnalysisReport>(response.analysis_report.ToString());
                    
                    Debug.Log($"Analysis complete! Overall score: {report.overall_score}");
                    OnAnalysisComplete?.Invoke(report);
                }
                catch (Exception e)
                {
                    Debug.LogError($"Failed to parse analysis response: {e.Message}");
                    OnAnalysisError?.Invoke($"Parse error: {e.Message}");
                }
            }
            else
            {
                Debug.LogError($"Analysis request failed: {webRequest.error}");
                OnAnalysisError?.Invoke(webRequest.error);
            }
        }
    }
    
    private IEnumerator AnalyzeAudioCoroutine(string audioFilePath)
    {
        Debug.Log($"Analyzing audio file: {audioFilePath}");
        
        var request = new AudioAnalysisRequest
        {
            session_id = currentSessionId,
            audio_file_path = audioFilePath
        };
        
        string jsonData = JsonConvert.SerializeObject(request);
        
        using (UnityWebRequest webRequest = new UnityWebRequest($"{apiBaseUrl}/analysis/audio", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");
            
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonConvert.DeserializeObject<dynamic>(webRequest.downloadHandler.text);
                    Debug.Log($"Audio analysis result: {response.result}");
                }
                catch (Exception e)
                {
                    Debug.LogError($"Failed to parse audio response: {e.Message}");
                    OnAnalysisError?.Invoke($"Audio parse error: {e.Message}");
                }
            }
            else
            {
                Debug.LogError($"Audio analysis failed: {webRequest.error}");
                OnAnalysisError?.Invoke(webRequest.error);
            }
        }
    }
    
    private IEnumerator CheckStatusCoroutine()
    {
        using (UnityWebRequest webRequest = UnityWebRequest.Get($"{apiBaseUrl}/analysis/status/{currentSessionId}"))
        {
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"Analysis status: {webRequest.downloadHandler.text}");
            }
            else
            {
                Debug.LogError($"Status check failed: {webRequest.error}");
            }
        }
    }
    
    public void DisplayResults(AnalysisReport report)
    {
        Debug.Log("=== INTERVIEW ANALYSIS RESULTS ===");
        Debug.Log($"Overall Score: {report.overall_score:F1}%");
        Debug.Log($"Facial Emotion: {report.facial_analysis.dominant_emotion} ({report.facial_analysis.score:F1}%)");
        Debug.Log($"Body Language: {report.body_language.score:F1}% - {report.body_language.feedback}");
        Debug.Log($"Voice Emotion: {report.audio_emotion.emotion} ({report.audio_emotion.score:F1}%)");
        
        Debug.Log("Recommendations:");
        foreach (string recommendation in report.recommendations)
        {
            Debug.Log($"- {recommendation}");
        }
    }
    
    public string GetPerformanceGrade(float score)
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
}