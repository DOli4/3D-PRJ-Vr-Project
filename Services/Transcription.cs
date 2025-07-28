using OpenAI.Audio;
using System.Threading.Tasks;

public class TranscriptionService
{
    // Client for interacting with OpenAI's audio transcription API
    private readonly AudioClient _audioClient;

    // Constructor initializes the AudioClient with the provided API key
    public TranscriptionService(string apiKey)
    {
        _audioClient = new AudioClient(model: "whisper-1", apiKey);
    }

    // Asynchronous method to transcribe an audio file into text
    public async Task<string> TranscribeAsync(string filePath)
    {
        // Configure transcription options such as response format
        var options = new AudioTranscriptionOptions
        {
            ResponseFormat = AudioTranscriptionFormat.Verbose
        };

        // Send the audio file to OpenAI for transcription
        var result = await _audioClient.TranscribeAudioAsync(filePath, options);

        // Extract and return the transcribed text from the result
        return result.Value.Text;
    }
}