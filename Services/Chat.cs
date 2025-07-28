using OpenAI.Chat;
using System.Collections.Generic;
using System.Threading.Tasks;

public class ChatService
{
    // ChatClient is used to communicate with OpenAI's chat completion API
    private readonly ChatClient _chatClient;

    // A list to store messages exchanged during the conversation (not used for reflavoring)
    private readonly List<ChatMessage> _messages;

    // Constructor initializes the ChatClient with the given API key
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

    // Method to get a rephrased version of the next interview question
    public async Task<string> GetReflavoredQuestionAsync(string userAnswer, string originalQuestion)
    {
        // A new set of messages is created each time to avoid adding unnecessary history
        var messages = new List<ChatMessage>
        {
            new SystemChatMessage("You are a helpful assistant that only rephrases interview questions."),
            new UserChatMessage(
                $"The user just answered: \"{userAnswer}\". " +
                $"Please rephrase the following question so it flows naturally from their answer, " +
                $"but keep the meaning and topic the same. " +
                $"Return only the rephrased question, nothing else:\n\"{originalQuestion}\"")
        };

        // Call OpenAI API to get the rephrased question
        var result = await _chatClient.CompleteChatAsync(messages);

        // Extract and return the text of the rephrased question
        return result.Value.Content[0].Text.Trim();
    }
}