# ChatGPT Interview Bot with Voice (C# + OpenAI + Google TTS)

This project is a **voice-based coding interview assistant** built in **C# (.NET 8)**.  
It uses:

**OpenAI GPT-4** – For dynamic rephrasing of questions  
**OpenAI Whisper** – For speech-to-text transcription  
**Google TTS (Text-to-Speech)** – For realistic AI voices  
**NAudio** – For recording and playing audio  

---

## Requirements

- [.NET 8 SDK](https://dotnet.microsoft.com/en-us/download)  
- A Google Cloud Project with **Text-to-Speech API enabled**  
- An OpenAI API Key

---

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/chatgpt-interview-bot.git
cd chatgpt-interview-bot
```

Install required packages:

```bash
dotnet add package OpenAI
dotnet add package Google.Cloud.TextToSpeech.V1
dotnet add package NAudio
dotnet add package Microsoft.Extensions.Configuration
dotnet add package Microsoft.Extensions.Configuration.Json
```

Create `appsettings.json` in the project root:

```json
{
  "OpenAI": {
    "ApiKey": "YOUR_OPENAI_API_KEY"
  }
}
```

Set your **Google API Key JSON**:

```powershell
setx GOOGLE_APPLICATION_CREDENTIALS "D:\Keys\google-tts.json"
```

Restart your terminal after setting this.

---

## Running the App

```bash
dotnet restore
dotnet build
dotnet run
```

Or use **auto-reload mode**:

```bash
dotnet watch run
```

---

## Features

**Voice-based Q&A interview flow**  
**Transcribes answers with Whisper (STT)**  
**Saves audio + text transcripts in `/Transcripts`**  
**GPT rephrases each question based on user input**  

---

## File Structure

```
ChatGPTInterviewBot/
│── Program.cs
│── Services/
│   ├── ChatService.cs
│   ├── TranscriptionService.cs
│   ├── TTSService.cs
│   ├── AudioRecorder.cs
│── ApiKeyLoader.cs
│── appsettings.json
│── Transcripts/   # Saved audio + transcriptions (ignored by Git)
```

---

## Example Flow

```
GPT: Hello, welcome to your coding internship interview. Let's begin.
GPT: Tell me about yourself.
[You answer... program records + transcribes]
GPT: Great! Based on that, can you explain why this internship excites you?
```

---

## Ignore Transcripts in Git

Add this to `.gitignore`:

```
# Ignore saved audio/transcripts
Transcripts/
```

---

## License
MIT License
