using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        // Load the API key from appsettings.json using ApiKeyLoader
        string apiKey = ApiKeyLoader.Load();

        // Initialize services for chat, transcription, TTS, and audio recording
        var chatService = new ChatService(apiKey);
        var transcriptionService = new TranscriptionService(apiKey);
        var ttsService = new TTSService();
        var recorder = new AudioRecorder();

        // List of predefined interview questions
        string[] questions =
        {
            "Tell me about yourself.",
            "Why are you interested in this internship?",
            "What programming languages are you most comfortable with?",
            "Describe a project you're proud of.",
            "How do you approach problem solving in code?",
            "Where do you see yourself in 3 years?"
        };

        // Initial greeting
        await ttsService.SpeakAsync("Hello, welcome to your coding internship interview. Let's begin.");

        // Start with the first question
        string currentQuestion = questions[0];

        for (int i = 0; i < questions.Length; i++)
        {
            // Speak the current question (the first one is original, later ones may be rephrased)
            await ttsService.SpeakAsync(currentQuestion);

            // Record audio input and transcribe it to text
            recorder.Record("input.wav");
            string userAnswer = await transcriptionService.TranscribeAsync("input.wav");

            // Save the user's audio and transcription to the Transcripts folder
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            string folder = Path.Combine("Transcripts");
            Directory.CreateDirectory(folder); // Create the folder if it does not exist

            // Save audio file
            File.Copy("input.wav", Path.Combine(folder, $"user_{timestamp}.wav"), true);

            // Save transcription text file
            await File.WriteAllTextAsync(Path.Combine(folder, $"user_{timestamp}.txt"), userAnswer);

            // Generate a rephrased version of the next question, if there is another one
            if (i + 1 < questions.Length)
            {
                currentQuestion = await chatService.GetReflavoredQuestionAsync(userAnswer, questions[i + 1]);
            }
        }

        // Final closing message
        await ttsService.SpeakAsync("Thank you for your time. We'll get back to you soon.");
    }
}