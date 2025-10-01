using System;
using System.IO;
using System.Threading.Tasks;
using Google.Cloud.TextToSpeech.V1;
using Google.Apis.Auth.OAuth2;
using NAudio.Wave;

public class TTSService
{
    private readonly TextToSpeechClient _client;

    public TTSService()
    {
        Console.WriteLine("TTS: using explicit creds via builder (no env var)");

        var credPath = Path.Combine(AppContext.BaseDirectory, "automated-lodge-466210-u4-279b32a10295.json");
        if (!File.Exists(credPath))
            throw new FileNotFoundException($"Google TTS credentials file not found: {credPath}");

        var cred = GoogleCredential.FromFile(credPath);

        _client = new TextToSpeechClientBuilder
        {
            Credential = cred
        }.Build();
    }

    public async Task SpeakAsync(string text)
    {
        Console.WriteLine(" GPT: " + text);

        var input = new SynthesisInput { Text = text };
        var voice = new VoiceSelectionParams { LanguageCode = "en-US", SsmlGender = SsmlVoiceGender.Neutral };
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
