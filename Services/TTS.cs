using System;
using System.IO;
using System.Threading.Tasks;
using Google.Cloud.TextToSpeech.V1;
using NAudio.Wave;

public class TTSService
{
    // Google Text-to-Speech client for generating speech
    private readonly TextToSpeechClient _client;

    public TTSService()
    {
        // Create the Google TTS client instance
        _client = TextToSpeechClient.Create();
    }

    // Asynchronous method to convert text to speech and play it
    public async Task SpeakAsync(string text)
    {
        // Display the text in the console for reference
        Console.WriteLine(" GPT: " + text);

        // Prepare the input text for synthesis
        var input = new SynthesisInput { Text = text };

        // Set voice parameters (language and gender)
        var voice = new VoiceSelectionParams
        {
            LanguageCode = "en-US",
            SsmlGender = SsmlVoiceGender.Neutral
        };

        // Set audio output configuration (MP3 format)
        var config = new AudioConfig { AudioEncoding = AudioEncoding.Mp3 };

        // Send request to Google TTS API to synthesize speech
        var response = await _client.SynthesizeSpeechAsync(input, voice, config);

        // Create a temporary file path for the MP3 output
        string fileName = Path.Combine(Path.GetTempPath(), "tts.mp3");

        // Save the synthesized audio as an MP3 file
        await File.WriteAllBytesAsync(fileName, response.AudioContent.ToByteArray());

        // Load the MP3 file and set up audio playback
        using var mp3 = new Mp3FileReader(fileName);
        using var waveOut = new WaveOutEvent();
        waveOut.Init(mp3);
        waveOut.Play();

        // Wait while the audio is playing
        while (waveOut.PlaybackState == PlaybackState.Playing)
            await Task.Delay(200);
    }
}