# 🚀 AI-Powered Git Commit Generator v2.0

<!-- Updated to v2.0 with improved focused prompting -->
<!-- Now features intelligent, context-aware commit message generation -->
A modular, well-structured Python application that uses Ollama's llama3.2 model to generate conventional git commit messages based on your staged changes.

## 📁 Project Structure

```
commit_ai/
├── __init__.py              # Main package
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
├── README.md               # Documentation
├── core/                   # Core business logic
│   ├── __init__.py
│   ├── git_ops.py          # Git operations
│   ├── llm_client.py       # Ollama/LLM integration
│   └── config.py           # Configuration management
├── ui/                     # User interface
│   ├── __init__.py
│   └── interface.py        # Console UI components
└── utils/                  # Utility functions
    ├── __init__.py
    └── helpers.py          # Helper functions
```

## ✨ Features

- 🔧 **Modular Architecture** - Clean separation of concerns
- 🤖 **AI-Powered** - Uses Ollama llama3.2 for intelligent suggestions
- 📝 **Conventional Commits** - Follows standard format (feat, fix, docs, etc.)
- 🎯 **5 Smart Suggestions** - Multiple options with validation
- ⚙️ **Configurable** - Environment variables for customization
- 🌐 **Portable** - Works in any git repository
- 🔍 **Robust Error Handling** - Graceful failure and helpful messages
- 📊 **Rich UI** - Emojis, progress indicators, and clear formatting

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running
3. **llama3.2 model** downloaded

### Installation

```bash
# 1. Install Ollama (if not already installed)
brew install ollama  # macOS
# or download from https://ollama.ai

# 2. Start Ollama
ollama serve

# 3. Install the model
ollama pull llama3.2:latest

# 4. Clone/download this project
git clone <your-repo>
cd commit_ai

# 5. Install Python dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Navigate to any git repository
cd /path/to/your/project

# Stage some changes
git add .

# Run the commit generator
python /path/to/commit_ai/main.py

# Follow the interactive prompts!
```

## 🔧 Configuration

Configure the application using environment variables:

```bash
# Ollama settings
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2:latest"

# LLM parameters
export LLM_TEMPERATURE="0.7"        # Creativity (0.0-2.0)
export LLM_TOP_P="0.9"             # Response diversity
export MAX_SUGGESTIONS="5"          # Number of suggestions

# Behavior
export SHOW_CONFIDENCE="true"       # Show debug info
export AUTO_CONFIRM="false"         # Skip confirmation prompts
export REQUEST_TIMEOUT="30"         # API timeout in seconds
```

## 📚 Module Documentation

### Core Modules

#### `core/git_ops.py` - Git Operations
```python
from core import GitOperations

git = GitOperations(".")
changes = git.get_staged_changes()  # Get detailed change info
commit_info = git.create_commit("feat: add new feature")
```

#### `core/llm_client.py` - LLM Integration
```python
from core import LLMClient, Config

client = LLMClient(Config())
suggestions = client.generate_commit_suggestions(git_summary)
status = client.test_connection()  # Check availability
```

#### `core/config.py` - Configuration
```python
from core import Config

config = Config()
print(config.llm_model)  # Current model
is_valid, error = config.validate()  # Validate settings
```

### UI Module

#### `ui/interface.py` - User Interface
```python
from ui import UserInterface

ui = UserInterface(config)
ui.show_header()
choice = ui.display_suggestions(suggestions)
ui.show_commit_result(commit_info)
```

### Utils Module

#### `utils/helpers.py` - Utilities
```python
from utils import validate_commit_message, format_commit_message

is_valid, error = validate_commit_message("feat: add login")
formatted = format_commit_message("feat", "auth", "add login")
```

## 🎯 Example Session

```bash
🚀 AI-Powered Git Commit Generator v2.0
==================================================
📍 [1/5] Validating git repository...
✅ Git repository validated
📍 [2/5] Checking AI model availability...
✅ Ollama connected and model ready
📍 [3/5] Analyzing staged changes...

📊 Found staged changes:
------------------------------
📝 src/auth.py (Modified)
➕ tests/test_auth.py (Added)
📝 README.md (Modified)

Total files: 3
------------------------------
📍 [4/5] Generating AI commit suggestions...
🤖 Generating commit message suggestions...
✅ Generated 5 commit suggestions
📍 [5/5] Processing user selection...

============================================================
💡 Generated Commit Message Suggestions:
============================================================
1. feat(auth): add user authentication system
2. feat: implement login functionality with tests
3. test(auth): add comprehensive authentication tests
4. docs: update README with authentication guide
5. feat(auth): implement secure user login flow
0. Cancel (don't commit)
============================================================

Choose a commit message (0-5): 1

📝 Ready to commit with message:
'feat(auth): add user authentication system'

Proceed with commit? (y/N): y
✅ Commit created successfully!
📋 a1b2c3d4 - feat(auth): add user authentication system
```

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to Ollama" | Run `ollama serve` |
| "Model not found" | Run `ollama pull llama3.2:latest` |
| "Not a git repository" | Run from inside a git repository |
| "No staged changes" | Use `git add <files>` to stage changes |
| "Import errors" | Install requirements: `pip install -r requirements.txt` |

## 🛠️ Development

### Adding New Features

1. **New LLM Provider**: Extend `core/llm_client.py`
2. **New UI Components**: Add to `ui/interface.py`
3. **New Git Features**: Extend `core/git_ops.py`
4. **New Utilities**: Add to `utils/helpers.py`

### Testing

```bash
# Test individual components
python -c "from core import GitOperations; print(GitOperations().is_git_repository())"
python -c "from core import LLMClient; print(LLMClient().is_available())"
```

## 📋 Conventional Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes |
| `refactor` | Code refactoring |
| `test` | Test changes |
| `chore` | Maintenance tasks |
| `perf` | Performance improvements |
| `ci` | CI/CD changes |
| `build` | Build system changes |

## 🤝 Contributing

1. Follow the modular structure
2. Add type hints to all functions
3. Include docstrings for public methods
4. Update README for new features
5. Test thoroughly before submitting

---

**Clean, modular, and ready to use! 🚀** 