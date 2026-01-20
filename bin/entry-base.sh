#!/bin/bash
# Common entry point logic shared by all agent containers

# Configure SSH for GitHub
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/known_hosts
chmod 600 ~/.ssh/known_hosts

cat > ~/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
EOF
chmod 600 ~/.ssh/config

# Create a container-specific gitconfig that disables GPG signing
# Host config is mounted at ~/.gitconfig.host, copy and modify it
cp ~/.gitconfig.host ~/.gitconfig

# Remove GPG-related settings that reference host binaries not available in container
sed -i '/^\[gpg\]/,/^$/d' ~/.gitconfig
sed -i '/signingkey/d' ~/.gitconfig
sed -i 's/gpgsign = true/gpgsign = false/g' ~/.gitconfig

# Configure git to use GITHUB_TOKEN for HTTPS authentication (optional fallback)
if [ -n "${GITHUB_TOKEN}" ]; then
  # Store GitHub credentials for HTTPS
  mkdir -p ~/.config/git
  echo "[credential]" > ~/.config/git/config
  echo "    helper = store" >> ~/.config/git/config
  echo "https://oauth2:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
  chmod 600 ~/.git-credentials
fi

# Build obsidian-mcp if available
if [ -d "/obsidian-mcp" ]; then
  cd /obsidian-mcp
  npm install --silent
  npm run build --silent
  npm link --silent
  cd /cubicle
fi
