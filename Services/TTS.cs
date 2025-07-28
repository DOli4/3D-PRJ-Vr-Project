using System;
using System.IO;
using System.Threading.Tasks;
using Google.Cloud.TextToSpeech.V1;
using NAudio.Wave;

public class TTSService
{
    private readonly TextToSpeechClient _client;

    public TTSService()
    {
        _client = TextToSpeechClient.Create();
    }

    public async Task SpeakAsync(string text)
    {
        Console.WriteLine(" GPT: " + text);

        var input = new SynthesisInput { Text = text };
        var voice = new VoiceSelectionParams
        {
            LanguageCode = "en-US",
            SsmlGender = SsmlVoiceGender.Neutral
        };
        var config = new AudioConfig { AudioEncoding = AudioEncoding.Mp3 };

        var response = await _client.SynthesizeSpeechAsync(input, voice, config);

        
        string fileName = Path.Combine(Path.GetTempPath(), "tts.mp3");
        await File.WriteAllBytesAsync(fileName, response.AudioContent.ToByteArray());

        using var mp3 = new Mp3FileReader(fileName);
        using var waveOut = new WaveOutEvent();
        waveOut.Init(mp3);
        waveOut.Play();

        while (waveOut.PlaybackState == PlaybackState.Playing)
            await Task.Delay(200);
    }
}