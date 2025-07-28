using Microsoft.Extensions.Configuration;
using System.IO;

public static class ApiKeyLoader
{
    // Loads the OpenAI API key from the appsettings.json configuration file
    public static string Load()
    {
        // Build the configuration object and set the base path to the current directory
        var config = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory()) // Use the current project directory
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true) // Load appsettings.json
            .Build();

        // Retrieve and return the API key from the configuration
        return config["OpenAI:ApiKey"];
    }
}