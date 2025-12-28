#!/bin/bash
# 🔒 Fix commit with API keys

set -e

echo "🔒 Fixing commit with API keys..."
echo ""

# Check if we are on the correct branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📌 Current branch: $CURRENT_BRANCH"
echo ""

# Check if commit 61dacb5 exists
if ! git cat-file -e 61dacb5 2>/dev/null; then
    echo "❌ Commit 61dacb5 does not exist"
    exit 1
fi

# Check if commit 61dacb5 is in history
if ! git log --oneline | grep -q "61dacb5"; then
    echo "⚠️  Commit 61dacb5 is not in current history"
    echo "Use: git rebase -i 61dacb5^"
    exit 1
fi

# Check if this is the last commit with env.example
LAST_ENV_COMMIT=$(git log --oneline --all -- env.example | head -1 | cut -d' ' -f1)
echo "📝 Last commit with env.example: $LAST_ENV_COMMIT"

# If 61dacb5 is the last commit, we can use --amend
if [ "$LAST_ENV_COMMIT" = "61dacb5" ] && [ "$(git rev-parse HEAD)" = "61dacb5" ]; then
    echo "✅ This is the last commit - using --amend"
    git add env.example
    git commit --amend --no-edit
    echo "✅ Commit fixed!"
    exit 0
fi

# If not, we need to use rebase
echo "⚠️  Commit is not last - using interactive rebase"
echo ""
echo "Will execute: git rebase -i 61dacb5^"
echo "In editor change 'pick' to 'edit' for commit 61dacb5"
echo ""

read -p "Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled. Execute manually:"
    echo "  git rebase -i 61dacb5^"
    echo "  # Change 'pick' to 'edit' for 61dacb5"
    echo "  git add env.example"
    echo "  git commit --amend --no-edit"
    echo "  git rebase --continue"
    exit 0
fi

# Automatic rebase
echo "🔄 Starting rebase..."
git rebase -i 61dacb5^ <<EOF
edit 61dacb5 config: add OpenRouter API key configuration
pick $(git log --oneline | head -1 | cut -d' ' -f1)
EOF

# Fix commit
git add env.example
git commit --amend --no-edit

# Continue rebase
git rebase --continue

echo "✅ Commit fixed via rebase!"
