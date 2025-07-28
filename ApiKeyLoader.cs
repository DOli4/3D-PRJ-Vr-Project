using Microsoft.Extensions.Configuration;
using System.IO;

public static class ApiKeyLoader
{
    public static string Load()
    {
        var config = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
            .Build();

        return config["OpenAI:ApiKey"];
    }
}