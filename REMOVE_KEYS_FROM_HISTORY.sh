#!/bin/bash
# 🔒 Script to remove API keys from git history

set -e

echo "🔒 Removing API keys from git history..."
echo ""
echo "⚠️  WARNING: This will change commit history!"
echo "⚠️  If you have already pushed commits to remote, you will need to use force push"
echo ""
read -p "Are you really sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# Check if git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "📦 Installing git-filter-repo..."
    pip install git-filter-repo || {
        echo "❌ Cannot install git-filter-repo"
        echo "Install manually: pip install git-filter-repo"
        exit 1
    }
fi

# Backup branch
echo "💾 Creating backup branch..."
git branch backup-before-key-removal 2>/dev/null || true

# Remove keys from history
echo "🔍 Searching and removing API keys from history..."

# List of keys to remove (update if you find more)
KEYS_TO_REMOVE=(
    "3bc7f2c018b971f67ebafa46937b34e9"
    "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"
)

# Use git filter-branch to remove keys
for key in "${KEYS_TO_REMOVE[@]}"; do
    echo "Removing key: ${key:0:20}..."
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch env.example .env 2>/dev/null || true" \
        --prune-empty --tag-name-filter cat -- --all
    
    # Replace keys with placeholders in entire history
    git filter-branch --force --tree-filter \
        "if [ -f env.example ]; then
            sed -i 's/$key/your_api_key_here/g' env.example 2>/dev/null || true
            sed -i 's/sk-or-v1-[a-zA-Z0-9]*/your_openrouter_api_key_here/g' env.example 2>/dev/null || true
        fi" \
        --prune-empty --tag-name-filter cat -- --all
done

# Alternatively, use git-filter-repo (more efficient)
echo "🧹 Cleaning history using git-filter-repo..."

# Remove .env files from history (if they were committed)
git filter-repo --path .env --invert-paths --force 2>/dev/null || true

# Replace keys in env.example
git filter-repo --replace-text <(cat <<EOF
3bc7f2c018b971f67ebafa46937b34e9==>your_api_key_here
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==>your_openrouter_api_key_here
EOF
) --force 2>/dev/null || {
    echo "⚠️  git-filter-repo did not work, using git filter-branch..."
    
    # Fallback: use git filter-branch
    git filter-branch --force --tree-filter \
        "if [ -f env.example ]; then
            sed -i 's/3bc7f2c018b971f67ebafa46937b34e9/your_api_key_here/g' env.example
            sed -i 's/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/your_openrouter_api_key_here/g' env.example
        fi" \
        --prune-empty --tag-name-filter cat -- --all
}

# Cleanup
echo "🧹 Cleaning references..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Keys have been removed from history!"
echo ""
echo "📊 Check result:"
echo "   git log --all --oneline"
echo ""
echo "⚠️  If you have already pushed to remote, use:"
echo "   git push --force --all"
echo "   git push --force --tags"
echo ""
echo "💾 Backup branch: backup-before-key-removal"
