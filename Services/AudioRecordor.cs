using System;
using NAudio.Wave;

public class AudioRecorder
{
    // Method to record audio from the default microphone and save it to a WAV file
    public void Record(string outputFile)
    {
        // Configure audio input with a sample rate of 16 kHz and mono channel
        using var waveIn = new WaveInEvent
        {
            WaveFormat = new WaveFormat(16000, 1)
        };

        // Create a writer to save the recorded audio to the specified file
        using var writer = new WaveFileWriter(outputFile, waveIn.WaveFormat);

        // Event handler that writes incoming audio data to the file
        waveIn.DataAvailable += (s, a) =>
        {
            writer.Write(a.Buffer, 0, a.BytesRecorded);
        };

        // Start recording
        waveIn.StartRecording();
        Console.WriteLine("Recording... Press Enter to stop.");

        // Wait for the user to press Enter to stop the recording
        Console.ReadLine();
        waveIn.StopRecording();
    }
}