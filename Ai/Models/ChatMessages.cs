public class ChatMessageModel
{
    // The role of the message sender, for example "user" or "assistant"
    public string Role { get; set; }

    // The actual content or text of the message
    public string Content { get; set; }

    // Constructor to initialize a chat message with a role and content
    public ChatMessageModel(string role, string content)
    {
        Role = role;
        Content = content;
    }
}