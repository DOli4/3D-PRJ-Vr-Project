public class ChatMessageModel
{
    public string Role { get; set; }
    public string Content { get; set; }

    public ChatMessageModel(string role, string content)
    {
        Role = role;
        Content = content;
    }
}
