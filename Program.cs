using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        string apiKey = ApiKeyLoader.Load();

        var chatService = new ChatService(apiKey);
        var transcriptionService = new TranscriptionService(apiKey);
        var ttsService = new TTSService();
        var recorder = new AudioRecorder();

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

        // Start with the first question
        string currentQuestion = questions[0];

        for (int i = 0; i < questions.Length; i++)
            {
                // ✅ Ask the current question (original first, then reflavored ones)
                await ttsService.SpeakAsync(currentQuestion);
            
                // Record + transcribe user answer
                recorder.Record("input.wav");
                string userAnswer = await transcriptionService.TranscribeAsync("input.wav");
            
                // Save user audio + text
                string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                string folder = Path.Combine("Transcripts");
                Directory.CreateDirectory(folder);
            
                File.Copy("input.wav", Path.Combine(folder, $"user_{timestamp}.wav"), true);
                await File.WriteAllTextAsync(Path.Combine(folder, $"user_{timestamp}.txt"), userAnswer);
            
                // ✅ Prepare next question (reflavored) – only if there is another question
                if (i + 1 < questions.Length)
                {
                    currentQuestion = await chatService.GetReflavoredQuestionAsync(userAnswer, questions[i + 1]);
                }
            }

        await ttsService.SpeakAsync("Thank you for your time. We'll get back to you soon.");
    }
}