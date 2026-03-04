# Python Version Management

## Required Version

**Python 3.13.5** - This is the EXACT version required for all team members.

## Why Exact Version?

- ✅ Ensures library compatibility across all team members
- ✅ Prevents "works on my machine" issues
- ✅ Consistent behavior in virtual environments
- ✅ No version conflicts with dependencies

## Installation

### Option 1: Using pyenv (Recommended)

**Best for managing multiple Python versions:**

```bash
# Install pyenv
brew install pyenv

# Add to shell config (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.13.5
pyenv install 3.13.5

# Verify
pyenv versions
```

### Option 2: Using Homebrew

```bash
# Install Python 3.13
brew install python@3.13

# Check version (may not be exact 3.13.5)
python3.13 --version
```

### Option 3: Official Installer

Download from: https://www.python.org/downloads/release/python-3135/

## How Setup Works

When you run `make setup`, the script will:

1. ✅ Check if you have Python 3.13.5 installed
2. ✅ If using pyenv and version missing, offer to install it automatically
3. ✅ If not found, provide clear installation instructions
4. ✅ Create virtual environment with exact version
5. ✅ Install all dependencies

## Troubleshooting

### "Python 3.13.5 is required"

You don't have the exact version. Follow installation instructions above.

### "Command not found: pyenv"

Either install pyenv (recommended) or use Homebrew/manual installation.

### "Version mismatch in venv"

Delete and recreate:
```bash
rm -rf venv
make setup
```

## Checking Your Version

```bash
# In venv
source venv/bin/activate
python --version
# Should show: Python 3.13.5
```

## .python-version File

The `.python-version` file in the repo root specifies the required version. Tools like `pyenv` automatically detect and use this version.
