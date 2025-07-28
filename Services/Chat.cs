using OpenAI.Chat;
using System.Collections.Generic;
using System.Threading.Tasks;

public class ChatService
{
    private readonly ChatClient _chatClient;
    private readonly List<ChatMessage> _messages;

    public ChatService(string apiKey)
    {
        _chatClient = new ChatClient(model: "gpt-4", apiKey);
        _messages = new List<ChatMessage>
        {
            new SystemChatMessage(
                "You are a thoughtful and realistic interviewer conducting a coding internship interview. " +
                "Use the provided questions as guidance, but ask natural follow-ups if the user's answers inspire them. " +
                "Only move on if it makes sense. Speak in a conversational tone.")
        };
    }

    public async Task<string> GetReflavoredQuestionAsync(string userAnswer, string originalQuestion)
{
    // Create a fresh prompt each time (don't use full chat history)
    var messages = new List<ChatMessage>
    {
        new SystemChatMessage("You are a helpful assistant that only rephrases interview questions."),
        new UserChatMessage(
            $"The user just answered: \"{userAnswer}\". " +
            $"Please rephrase the following question so it flows naturally from their answer, " +
            $"but keep the meaning and topic the same. " +
            $"Return only the rephrased question, nothing else:\n\"{originalQuestion}\"")
    };

    var result = await _chatClient.CompleteChatAsync(messages);

    return result.Value.Content[0].Text.Trim();
    }
}