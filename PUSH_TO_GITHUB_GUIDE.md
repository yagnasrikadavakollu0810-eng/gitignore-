# 🚀 Push to GitHub - Quick Guide

Your workflow files are ready to push to GitHub!

## Option 1: Use the Helper Script (EASIEST)

### Step 1: Get Your Repository URL
1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Click the green **Code** button
3. Select **HTTPS** (or SSH if you prefer)
4. Copy the URL (looks like: `https://github.com/YOUR_USERNAME/YOUR_REPO.git`)

### Step 2: Run the Push Script

Open PowerShell and run:

```powershell
cd "c:\Users\K Yagnasri"

# Run the helper script with your repository URL
.\push-to-github.ps1 -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
```

The script will:
- ✓ Check for Git installation
- ✓ Initialize repository (if needed)
- ✓ Add all workflow files
- ✓ Commit with meaningful message
- ✓ Push to GitHub

---

## Option 2: Manual Git Commands

If you prefer manual steps:

```powershell
cd "c:\Users\K Yagnasri"

# Initialize repository
git init

# Add remote (replace with your actual URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Configure git user
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Create commit
git commit -m "Add PDF-to-Embeddings workflow pipeline"

# Push to GitHub
git push -u origin main
```

---

## Option 3: If You Already Have a Repository Cloned

If your repository is already cloned somewhere else:

```powershell
# Navigate to your cloned repository
cd "Your-Repo-Directory"

# Copy the workflow files
Copy-Item "c:\Users\K Yagnasri\*.py" .
Copy-Item "c:\Users\K Yagnasri\*.md" .
Copy-Item "c:\Users\K Yagnasri\requirements.txt" .

# Add and push
git add .
git commit -m "Add PDF-to-Embeddings workflow pipeline"
git push
```

---

## 📋 Files to be Pushed

These files will be uploaded:
- ✅ `COMPLETE_WORKFLOW_STEPS.py` - Full pipeline code
- ✅ `VISUAL_WORKFLOW_GUIDE.md` - Visual guide
- ✅ `STEP_BY_STEP_SNIPPETS.py` - Code examples
- ✅ `INDEX.md` - Navigation guide
- ✅ `requirements.txt` - Dependencies
- ✅ `scripts/` - Your script directory
- ✅ `.gitignore` - (automatically created)

---

## 🔑 GitHub Authentication

### For HTTPS:
- Use your GitHub username
- **Password**: Use a **Personal Access Token** (not your password!)
  - Create token: https://github.com/settings/tokens
  - Scopes needed: `repo` (full control of private repositories)

### For SSH:
- Add SSH key to GitHub: https://github.com/settings/keys
- Use SSH URL: `git@github.com:YOUR_USERNAME/YOUR_REPO.git`

---

## ✅ Troubleshooting

### "Git is not installed"
Install from: https://git-scm.com/download/win

### "Authentication failed"
1. For HTTPS: Use Personal Access Token (create at https://github.com/settings/tokens)
2. For SSH: Add SSH keys (https://github.com/settings/keys)

### "Fatal: this operation must be run in a work tree"
Make sure you're in the correct directory: `c:\Users\K Yagnasri`

### "Remote already exists"
Run: `git remote set-url origin YOUR_NEW_URL`

---

## 📝 Next Steps After Push

1. ✓ Files uploaded to GitHub
2. Open your repository on GitHub to verify
3. Share the repository with others
4. Start using the workflow!

---

**Ready to push?**

Provide your GitHub repository URL and I'll help you execute the push!

Example:
```
https://github.com/kyagnasri/pdf-embeddings.git
```
