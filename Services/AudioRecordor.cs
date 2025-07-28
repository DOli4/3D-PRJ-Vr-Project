using System;
using NAudio.Wave;

public class AudioRecorder
{
    public void Record(string outputFile)
    {
        using var waveIn = new WaveInEvent
        {
            WaveFormat = new WaveFormat(16000, 1)
        };

        using var writer = new WaveFileWriter(outputFile, waveIn.WaveFormat);

        waveIn.DataAvailable += (s, a) =>
        {
            writer.Write(a.Buffer, 0, a.BytesRecorded);
        };

        waveIn.StartRecording();
        Console.WriteLine("Recording... Press Enter to stop.");
        Console.ReadLine();
        waveIn.StopRecording();
    }
}
