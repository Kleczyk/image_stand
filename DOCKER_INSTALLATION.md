# 🐳 Instalacja Docker i Docker Compose

## Instalacja Docker (Ubuntu/Debian)

### Krok 1: Aktualizacja systemu

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

### Krok 3: Dodanie oficjalnego klucza GPG Dockera

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
# Sprawdź wersję Dockera
docker --version

# Sprawdź wersję Docker Compose
docker compose version

# Test uruchomienia
sudo docker run hello-world
```

## Dodanie użytkownika do grupy docker

### Krok 1: Utworzenie grupy docker (jeśli nie istnieje)

```bash
sudo groupadd docker
```

### Krok 2: Dodanie użytkownika do grupy docker

```bash
# Zastąp $USER swoją nazwą użytkownika lub użyj:
sudo usermod -aG docker $USER

# Lub dla konkretnego użytkownika:
sudo usermod -aG docker twoja_nazwa_uzytkownika
```

### Krok 3: Weryfikacja członkostwa w grupie

```bash
# Sprawdź czy użytkownik jest w grupie docker
groups

# Powinno pokazać "docker" w liście grup
```

### Krok 4: Aktywacja zmian

**WAŻNE**: Po dodaniu użytkownika do grupy, musisz:

1. **Wylogować się i zalogować ponownie**, LUB
2. **Użyć `newgrp docker`** w bieżącej sesji:

```bash
newgrp docker
```

### Krok 5: Test bez sudo

```bash
# Teraz powinno działać bez sudo:
docker run hello-world

# Jeśli nadal wymaga sudo, sprawdź:
docker ps
```

## Rozwiązywanie problemów

### Problem: "permission denied" przy użyciu dockera bez sudo

1. **Sprawdź czy użytkownik jest w grupie docker:**
   ```bash
   groups | grep docker
   ```

2. **Jeśli nie widzisz "docker", dodaj ponownie:**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Sprawdź uprawnienia do socka Dockera:**
   ```bash
   ls -la /var/run/docker.sock
   # Powinno pokazać: srw-rw---- 1 root docker
   ```

4. **Jeśli uprawnienia są nieprawidłowe:**
   ```bash
   sudo chown root:docker /var/run/docker.sock
   sudo chmod 666 /var/run/docker.sock
   ```

### Problem: Docker nie startuje

```bash
# Sprawdź status serwisu
sudo systemctl status docker

# Uruchom serwis
sudo systemctl start docker

# Włącz autostart
sudo systemctl enable docker
```

### Problem: Docker Compose nie działa

```bash
# Sprawdź czy plugin jest zainstalowany
docker compose version

# Jeśli nie działa, zainstaluj osobno:
sudo apt install docker-compose-plugin
```

## Instalacja Docker Compose (standalone - opcjonalnie)

Jeśli wolisz używać `docker-compose` (z myślnikiem) zamiast `docker compose`:

```bash
# Pobierz najnowszą wersję
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Nadaj uprawnienia wykonywania
sudo chmod +x /usr/local/bin/docker-compose

# Sprawdź instalację
docker-compose --version
```

## Szybka weryfikacja

Po instalacji uruchom:

```bash
# 1. Sprawdź wersje
docker --version
docker compose version

# 2. Test bez sudo
docker run hello-world

# 3. Sprawdź czy możesz uruchomić kontenery
docker ps

# 4. Test Docker Compose
docker compose version
```

## Automatyczne uruchamianie Dockera przy starcie

```bash
# Włącz autostart (powinno być już włączone)
sudo systemctl enable docker

# Sprawdź status
sudo systemctl status docker
```

## Odinstalowanie Dockera (jeśli potrzebne)

```bash
# Zatrzymaj Docker
sudo systemctl stop docker

# Odinstaluj pakiety
sudo apt purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Usuń obrazy, kontenery, wolumeny i sieci
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
```

## Alternatywna instalacja (skrypt automatyczny)

Docker udostępnia oficjalny skrypt instalacyjny:

```bash
# Pobierz i uruchom skrypt
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dodaj użytkownika do grupy
sudo usermod -aG docker $USER
newgrp docker
```

**Uwaga**: Używaj oficjalnego skryptu tylko jeśli ufasz źródłu.

## Sprawdzenie konfiguracji

Po instalacji sprawdź:

```bash
# 1. Wersja Dockera
docker --version

# 2. Wersja Docker Compose
docker compose version

# 3. Użytkownik w grupie docker
groups

# 4. Test uruchomienia kontenera
docker run hello-world

# 5. Status serwisu
sudo systemctl status docker
```

## Następne kroki

Po zainstalowaniu Dockera:

1. **Skonfiguruj projekt Image Stand:**
   ```bash
   cd /home/dk/repos/image_stand
   cp env.example .env
   nano .env  # Dodaj klucze API
   ```

2. **Uruchom aplikację:**
   ```bash
   docker compose up --build -d
   ```

3. **Sprawdź status:**
   ```bash
   docker compose ps
   ```

Zobacz [INSTALLATION.md](INSTALLATION.md) dla dalszych instrukcji.


