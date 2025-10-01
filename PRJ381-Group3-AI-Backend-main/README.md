# PRJ381-Group3-AI-Backend

A **FastAPI** service that powers the AI-enhanced job-interview simulator.

---

## 🚀 Prerequisites

| Tool | Windows | macOS / Linux |
|------|---------|---------------|
| **Python 3.9 +** | Install from [python.org](https://www.python.org/downloads/) or the Microsoft Store | Use the official installer or your package manager (`brew`, `apt`, etc.) |
| **Git** | [git-scm.com](https://git-scm.com/download/win) | Pre-installed on most systems or available via package manager |

---

## ⚙️ Setup (one-time per machine)

> **Tip:** Replace `python` with `py` on Windows if that’s your default launcher.

1. **Clone the repo**

```bash
git clone https://github.com/<your-org>/PRJ381-Group3-AI-Backend.git
cd PRJ381-Group3-AI-Backend
```

2. **Create & activate a virtual environment**

   | Shell          | Command                                                  |
   | -------------- | -------------------------------------------------------- |
   | **PowerShell** | `python -m venv .venv`<br>`.\.venv\Scripts\Activate.ps1` |
   | **cmd.exe**    | `python -m venv .venv`<br>`.\.venv\Scripts\activate.bat` |
   | **Bash / zsh** | `python -m venv .venv`<br>`source .venv/bin/activate`    |

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Download the required NLTK data**

```bash
python nltk_install.py
```

> Runs once per fresh environment.
> Places the *punkt* tokenizer and POS-tagger inside `.venv/nltk_data/`.

---

## ▶️ Run the development server

```bash
uvicorn app:app --reload
```

Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** in your browser to explore the interactive API documentation.

---

## 🛠️ Handy commands

```bash
# stop the virtual environment
deactivate         # Bash/zsh / PowerShell
```
