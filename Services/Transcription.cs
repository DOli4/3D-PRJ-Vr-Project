using OpenAI.Audio;
using System.Threading.Tasks;

public class TranscriptionService
{
    private readonly AudioClient _audioClient;

    public TranscriptionService(string apiKey)
    {
        _audioClient = new AudioClient(model: "whisper-1", apiKey);
    }

    public async Task<string> TranscribeAsync(string filePath)
    {
        var options = new AudioTranscriptionOptions
        {
            ResponseFormat = AudioTranscriptionFormat.Verbose
        };

        var result = await _audioClient.TranscribeAudioAsync(filePath, options);

        // ✅ FIX: Access result.Value.Text
        return result.Value.Text;
    }
}