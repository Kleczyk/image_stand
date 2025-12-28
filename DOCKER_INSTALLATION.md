# 🐳 Instalacja Docker i Docker Compose

## Instalacja Docker (Ubuntu/Debian)

### Krok 1: Update systemu

```bash
sudo apt update
sudo apt upgrade -y
```

### Krok 2: Instalacja zależności

```bash
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

### Krok 3: Dodanie oficjalnego keya GPG Dockera

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

### Krok 4: Dodanie repozytorium Dockera

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Krok 5: Instalacja Dockera

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Krok 6: Weryfikacja instalacji

```bash
# Check wersję Dockera
docker --version

# Check wersję Docker Compose
docker compose version

# Test starting
sudo docker run hello-world
```

## Dodanie użytkownika do grupy docker

### Krok 1: Ucreating grupy docker (if does not exist)

```bash
sudo groupadd docker
```

### Krok 2: Dodanie użytkownika do grupy docker

```bash
# Replace $USER swoją nazwą użytkownika lub użyj:
sudo usermod -aG docker $USER

# Lub for konkretnego użytkownika:
sudo usermod -aG docker twoja_nazwa_uzytkownika
```

### Krok 3: Weryfikacja członkostwa w grupie

```bash
# Check czy użytkownik jest w grupie docker
groups

# Powinno pokazać "docker" w liście grup
```

### Krok 4: Aktywacja zmian

**IMPORTANT**: Po dodaniu użytkownika do grupy, you must:

1. **Wylogować się i zalogować ponownie**, LUB
2. **Użyć `newgrp docker`** w bieżącej sesji:

```bash
newgrp docker
```

### Krok 5: Test bez sudo

```bash
# Teraz powinno działać bez sudo:
docker run hello-world

# If nadal requires sudo, check:
docker ps
```

## Troubleshooting problems

### Problem: "permission denied" przy użyciu dockera bez sudo

1. **Check czy użytkownik jest w grupie docker:**
   ```bash
   groups | grep docker
   ```

2. **If nie widzisz "docker", add ponownie:**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Check uprawnienia do socka Dockera:**
   ```bash
   ls -la /var/run/docker.sock
   # Powinno pokazać: srw-rw---- 1 root docker
   ```

4. **If uprawnienia są nieprawidłowe:**
   ```bash
   sudo chown root:docker /var/run/docker.sock
   sudo chmod 666 /var/run/docker.sock
   ```

### Problem: Docker nie startuje

```bash
# Check status serviceu
sudo systemctl status docker

# Start service
sudo systemctl start docker

# Włącz autostart
sudo systemctl enable docker
```

### Problem: Docker Compose nie działa

```bash
# Check czy plugin jest zainstalowany
docker compose version

# If nie działa, zainstaluj osobno:
sudo apt install docker-compose-plugin
```

## Instalacja Docker Compose (standalone - opcjonalnie)

If wolisz używać `docker-compose` (z myślnikiem) instead of `docker compose`:

```bash
# Pull najnowszą wersję
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/laTest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Nadaj uprawnienia wykonywania
sudo chmod +x /usr/local/bin/docker-compose

# Check instalację
docker-compose --version
```

## Szybka weryfikacja

Po instalacji start:

```bash
# 1. Check wersje
docker --version
docker compose version

# 2. Test bez sudo
docker run hello-world

# 3. Check czy you can startić containers
docker ps

# 4. Test Docker Compose
docker compose version
```

## Automatyczne uruchamianie Dockera przy starcie

```bash
# Włącz autostart (powinno być już włączone)
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

## Odinstalowanie Dockera (if potrzebne)

```bash
# Stop Docker
sudo systemctl stop docker

# Odinstaluj pakiety
sudo apt purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Remove obrazy, containers, wolumeny i sieci
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
```

## Alternatywna instalacja (skrypt automatyczny)

Docker uaccessnia oficjalny skrypt instalacyjny:

```bash
# Pull i start skrypt
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add użytkownika do grupy
sudo usermod -aG docker $USER
newgrp docker
```

**Uwaga**: Używaj oficjalnego skryptu tylko if ufasz źródłu.

## Sprawdzenie konfiguracji

Po instalacji check:

```bash
# 1. Wersja Dockera
docker --version

# 2. Wersja Docker Compose
docker compose version

# 3. Użytkownik w grupie docker
groups

# 4. Test starting kontenera
docker run hello-world

# 5. Status serviceu
sudo systemctl status docker
```

## Następne kroki

Po zainstalowaniu Dockera:

1. **Configure projekt Image Stand:**
   ```bash
   cd /home/dk/repos/image_stand
   cp env.example .env
   nano .env  # Add API keys
   ```

2. **Start application:**
   ```bash
   docker compose up --build -d
   ```

3. **Check status:**
   ```bash
   docker compose ps
   ```

See [INSTALLATION.md](INSTALLATION.md) for dalszych instructions.


