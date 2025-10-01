using System;
using System.IO;
using Microsoft.Extensions.Configuration;

public static class ApiKeyLoader
{
    public static string Load()
    {
        // 1) Prefer the EXE folder (works when launched from Unity)
        var baseDir = AppContext.BaseDirectory;

        var builder = new ConfigurationBuilder()
            .SetBasePath(baseDir)
            .AddJsonFile("appsettings.json", optional: true, reloadOnChange: false);

        // 2) Fallback: also try current working directory (useful when running from VS/CLI)
        var cwd = Directory.GetCurrentDirectory();
        if (!string.Equals(cwd, baseDir, StringComparison.OrdinalIgnoreCase))
        {
            var alt = Path.Combine(cwd, "appsettings.json");
            if (File.Exists(alt))
                builder.AddJsonFile(alt, optional: true, reloadOnChange: false);
        }

        var config = builder.Build();

        // Try config first, then environment variable
        var key = config["OpenAI:ApiKey"] ?? Environment.GetEnvironmentVariable("OPENAI_API_KEY");

        if (string.IsNullOrWhiteSpace(key))
            throw new InvalidOperationException(
                $"OpenAI API key not found. Put it in appsettings.json next to the EXE or set OPENAI_API_KEY.");

        return key.Trim();
    }
}

