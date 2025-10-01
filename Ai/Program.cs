using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    static async Task<int> Main(string[] args)
    {
        try
        {
            await RunAsync();
            Console.WriteLine("Done. Press Enter to exit.");
            Console.ReadLine(); // keeps window open on double-click
            return 0;
        }
        catch (Exception ex)
        {
            var logPath = Path.Combine(AppContext.BaseDirectory, "crash.log");
            File.WriteAllText(logPath, ex.ToString());
            Console.Error.WriteLine($"Fatal error. See crash.log at: {logPath}");
            Console.ReadLine(); // keep window open
            return 1;
        }
    }

    static async Task RunAsync()
    {
        Console.WriteLine("=== Boot ===");
        Console.WriteLine($"BaseDir: {AppContext.BaseDirectory}");
        Console.WriteLine($"Creds exist: {File.Exists(Path.Combine(AppContext.BaseDirectory, "automated-lodge-466210-u4-279b32a10295.json"))}");

        // ----- services -----
        string apiKey = ApiKeyLoader.Load();

        var chatService = new ChatService(apiKey);
        var transcriptionService = new TranscriptionService(apiKey);
        var ttsService = new TTSService();
        var recorder = new AudioRecorder();

        // interview questions
        string[] questions =
        {
            "Tell me about yourself.",
            "Why are you interested in this internship?",
            "What programming languages are you most comfortable with?",
            "Describe a project you're proud of.",
            "How do you approach problem solving in code?",
            "Where do you see yourself in 3 years?"
        };

        await ttsService.SpeakAsync("Hello, welcome to your coding internship interview. Let's begin.");

        string currentQuestion = questions[0];

        for (int i = 0; i < questions.Length; i++)
        {
            await ttsService.SpeakAsync(currentQuestion);

            // record + transcribe
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.wav");
            await recorder.RecordUntilEnterAsync(inputPath, minMs: 1500);   // updated call
            string userAnswer = await transcriptionService.TranscribeAsync(inputPath);

            // stable folders next to the exe
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            string folderV = Path.Combine(AppContext.BaseDirectory, "VoiceTranscripts");
            string folderT = Path.Combine(AppContext.BaseDirectory, "TextTranscripts");
            Directory.CreateDirectory(folderV);
            Directory.CreateDirectory(folderT);

            File.Copy(inputPath, Path.Combine(folderV, $"user_{timestamp}.wav"), true);
            await File.WriteAllTextAsync(Path.Combine(folderT, $"user_{timestamp}.txt"), userAnswer);

            if (i + 1 < questions.Length)
            {
                currentQuestion = await chatService.GetReflavoredQuestionAsync(userAnswer, questions[i + 1]);
            }
        }

        await ttsService.SpeakAsync("Thank you for your time. We'll get back to you soon.");
    }
}
