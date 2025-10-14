using UnityEngine;
using System.IO;
using System;

public class DataManager : MonoBehaviour
{
    // Unity local storage paths
    public static string LocalDataPath => Application.persistentDataPath;
    public static string SessionsPath => Path.Combine(LocalDataPath, "Sessions");
    public static string RecordingsPath => Path.Combine(LocalDataPath, "Recordings");
    
    // Backend integration path (matches .env UNITY_BASE_DIR)
    public static string BackendPath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData).Replace("Local", "LocalLow"),
        "DefaultCompany", "VRInterview", "Recordings"
    );

    void Awake()
    {
        InitializeDirectories();
        Debug.Log($"Unity Data Path: {LocalDataPath}");
        Debug.Log($"Backend Path: {BackendPath}");
    }

    void InitializeDirectories()
    {
        Directory.CreateDirectory(SessionsPath);
        Directory.CreateDirectory(RecordingsPath);
        Directory.CreateDirectory(BackendPath);
    }

    public static string CreateSessionFolder()
    {
        string sessionId = $"Session_{DateTime.Now:yyyyMMdd_HHmmss}";
        
        // Create in both Unity local and backend paths
        string localPath = Path.Combine(SessionsPath, sessionId);
        string backendPath = Path.Combine(BackendPath, sessionId);
        
        Directory.CreateDirectory(localPath);
        Directory.CreateDirectory(backendPath);
        
        return sessionId;
    }

    public static void SaveAudioFile(string sessionId, byte[] audioData, string filename)
    {
        // Save to both locations for redundancy
        string localFile = Path.Combine(SessionsPath, sessionId, filename);
        string backendFile = Path.Combine(BackendPath, sessionId, filename);
        
        File.WriteAllBytes(localFile, audioData);
        File.WriteAllBytes(backendFile, audioData);
        
        Debug.Log($"Audio saved: {filename}");
    }

    public static void SaveSessionLog(string sessionId, string logData)
    {
        string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        string logEntry = $"[{timestamp}] {logData}\n";
        
        string localLog = Path.Combine(SessionsPath, sessionId, "session.log");
        string backendLog = Path.Combine(BackendPath, sessionId, "session.log");
        
        File.AppendAllText(localLog, logEntry);
        File.AppendAllText(backendLog, logEntry);
    }
}