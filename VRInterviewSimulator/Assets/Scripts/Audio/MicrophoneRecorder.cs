using UnityEngine;
using System.IO;
using System;

public class MicrophoneRecorder : MonoBehaviour
{
    public int sampleRate = 44100;
    public float silenceThreshold = 0.01f;
    public float maxSilenceDuration = 5f;

    private AudioClip audioClip;
    private string microphoneDevice;
    private bool isRecording = false;
    private string sessionId;
    private string sessionPath;
    private int responseCount = 0;
    private float silenceTimer = 0f;
    private int positionLastFrame = 0;


    // Start is called before the first frame update
    void Start()
    {
        InitializeSession();
    }

    private void InitializeSession()
    {
        sessionId = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        sessionPath = Path.Combine(Application.persistentDataPath, "Recordings", "Session_" + sessionId);

        if (!Directory.Exists(sessionPath))
        {
            Directory.CreateDirectory(sessionPath);
            Debug.Log("Created session folder: " + sessionPath);
        }
    }

    public void StartRecording()
    {
        if (Microphone.devices.Length == 0)
        {
            Debug.LogWarning("No microphone detected.");
            return;
        }

        microphoneDevice = Microphone.devices[0];
        audioClip = Microphone.Start(microphoneDevice, true, 300, sampleRate);
        isRecording = true;
        silenceTimer = 0f;
        positionLastFrame = 0;
        responseCount++;

        Debug.Log("Recording started: response_" + responseCount + ".wav");

    }

    // Update is called once per frame
    void Update()
    {
        if (isRecording)
        {
            int currentPosition = Microphone.GetPosition(microphoneDevice);
            int samplesRecorded = currentPosition - positionLastFrame;

            if (samplesRecorded > 0)
            {
                float[] samples = new float[samplesRecorded];
                audioClip.GetData(samples, positionLastFrame);

                float maxVolume = 0f;
                foreach (var sample in samples)
                {
                    float abs = Mathf.Abs(sample);
                    if (abs > maxVolume) maxVolume = abs;
                }

                if (maxVolume < silenceThreshold)
                {
                    silenceTimer += Time.deltaTime;
                    if (silenceTimer >= maxSilenceDuration)
                    {
                        StopRecording();
                    }
                }
                else
                {
                    silenceTimer = 0f;
                }

                positionLastFrame = currentPosition;

            }
        }
    }

    public void StopRecording()
    {

        if (!isRecording) return;

        int position = Microphone.GetPosition(microphoneDevice);
        Microphone.End(microphoneDevice);
        isRecording = false;

        Debug.Log("Recording stopped at position: " + position);

        float[] samples = new float[position * audioClip.channels];
        audioClip.GetData(samples, 0);

        AudioClip trimmedClip = AudioClip.Create("TrimmedClip", position, audioClip.channels, sampleRate, false);
        trimmedClip.SetData(samples, 0);

        string filename = $"response_{responseCount}.wav";
        string filepath = Path.Combine(sessionPath, filename);
        SavWav.Save(filepath, trimmedClip);

        Debug.Log("WAV File Saved: " + filepath);

    }
}
