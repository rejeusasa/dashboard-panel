#!/bin/bash

################################################################################
# 🚀 DASHBOARD-PANEL + CLOUDFLARE TUNNEL INSTALLATION SCRIPT (SIMPLIFIED)
# 
# Complete setup untuk Bot Panel Dashboard dengan Cloudflare Tunnel integration
# URL: https://dashboard.jujulefek.qzz.io
# Single port (7860) untuk Panel + Dashboard
#
# Usage: chmod +x install-dashboard.sh && ./install-dashboard.sh
################################################################################

set -e  # Exit on error

# Color codes untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

################################################################################
# PORT CONFIGURATION
################################################################################
# Penjelasan:
# - Port 7860: Single port untuk Panel + Dashboard (semua dalam 1 Flask app)
#   - dashboard.html (monitoring UI)
#   - agent.py (panel utama)
#   - Semua dalam localhost:7860

DASHBOARD_PORT=7860    # Single port untuk semua

################################################################################
# SECTION 1: SYSTEM REQUIREMENTS CHECK
################################################################################
log_info "=== CHECKING SYSTEM REQUIREMENTS ==="

# Check if running as root for system packages
if [[ $EUID -ne 0 ]]; then
   log_warn "Script tidak dijalankan sebagai root. Beberapa instalasi mungkin membutuhkan sudo."
   USE_SUDO="sudo"
else
   USE_SUDO=""
fi

# Check OS
if ! [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_error "Script ini hanya support Linux. Detected: $OSTYPE"
    exit 1
fi
log_success "OS: Linux"

# Check if Python 3 installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 tidak terinstall. Install dulu:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi
log_success "Python 3 installed: $(python3 --version)"

# Check if pip installed
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 tidak terinstall"
    exit 1
fi
log_success "pip3 installed: $(pip3 --version)"

# Check if git installed
if ! command -v git &> /dev/null; then
    log_warn "git tidak terinstall. Installing..."
    $USE_SUDO apt-get update
    $USE_SUDO apt-get install -y git
fi
log_success "git installed"

################################################################################
# SECTION 2: SETUP PROJECT DIRECTORY
################################################################################
log_info "=== SETTING UP PROJECT DIRECTORY ==="

PROJECT_DIR="${1:-.}"
VENV_DIR="${PROJECT_DIR}/venv"

cd "$PROJECT_DIR"
log_success "Working directory: $(pwd)"

# Create virtual environment if not exists
if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created"
else
    log_success "Virtual environment already exists"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
log_success "Virtual environment activated"

################################################################################
# SECTION 3: INSTALL PYTHON DEPENDENCIES
################################################################################
log_info "=== INSTALLING PYTHON DEPENDENCIES ==="

# Upgrade pip, setuptools, wheel
log_info "Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# List of required Python packages
PYTHON_PACKAGES=(
    "flask>=2.3.0"
    "flask-cors>=4.0.0"
    "psutil>=5.9.0"
    "requests>=2.31.0"
    "urllib3>=2.0.0"
    "selenium>=4.0.0"
    "pyautogui>=0.9.53"
    "mss>=9.0.0"
    "python-dotenv>=1.0.0"
)

log_info "Installing Python packages..."
for package in "${PYTHON_PACKAGES[@]}"; do
    log_info "  → Installing $package"
    pip install "$package"
done
log_success "All Python packages installed"

# Optional: Install gunicorn untuk production deployment
log_info "Installing gunicorn untuk production deployment..."
pip install gunicorn

# Optional: Install Flask-SQLAlchemy
log_info "Installing Flask-SQLAlchemy..."
pip install Flask-SQLAlchemy

################################################################################
# SECTION 4: INSTALL CLOUDFLARE TUNNEL
################################################################################
log_info "=== INSTALLING CLOUDFLARE TUNNEL (CLOUDFLARED) ==="

if command -v cloudflared &> /dev/null; then
    log_success "Cloudflared sudah installed: $(cloudflared --version)"
else
    log_info "Installing Cloudflared..."
    
    # Add Cloudflare GPG key
    log_info "Adding Cloudflare GPG key..."
    $USE_SUDO mkdir -p --mode=0755 /usr/share/keyrings
    curl -fsSL https://pkg.cloudflare.com/cloudflare-public-v2.gpg | $USE_SUDO tee /usr/share/keyrings/cloudflare-public-v2.gpg >/dev/null
    log_success "Cloudflare GPG key added"
    
    # Add Cloudflare repository
    log_info "Adding Cloudflare apt repository..."
    echo 'deb [signed-by=/usr/share/keyrings/cloudflare-public-v2.gpg] https://pkg.cloudflare.com/cloudflared any main' | $USE_SUDO tee /etc/apt/sources.list.d/cloudflared.list >/dev/null
    log_success "Cloudflare repository added"
    
    # Update apt and install cloudflared
    log_info "Running apt-get update and installing cloudflared..."
    $USE_SUDO apt-get update
    $USE_SUDO apt-get install -y cloudflared
    
    log_success "Cloudflared installed: $(cloudflared --version)"
fi

################################################################################
# SECTION 5: CREATE CONFIGURATION FILES
################################################################################
log_info "=== CREATING CONFIGURATION FILES ==="

# Create .env file dengan PORT CONFIGURATION
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_info "Creating .env configuration file..."
    cat > "$PROJECT_DIR/.env" << EOF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dashboard Panel Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Single Port Configuration
# Port 7860: Panel + Dashboard (semua dalam 1 port)
DASHBOARD_PORT=${DASHBOARD_PORT}
DATABASE_PATH=./dashboard_metrics.db
HISTORY_DIR=./history
SCREENSHOT_DIR=./screenshots

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cloudflare Tunnel Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━���━━━━━━━━━━━━━━━━━━━━━━━━

# Tunnel URL - akan diakses dari public internet
CLOUDFLARE_TUNNEL_URL=https://dashboard.jujulefek.qzz.io

# Token dari: cloudflared tunnel login
CLOUDFLARE_TOKEN=YOUR_TOKEN_HERE
EOF
    log_success ".env file created"
else
    log_warn ".env file already exists. Skipping..."
fi

# Create simplified cloudflared configuration (1 tunnel, 1 port)
if [ ! -f "$PROJECT_DIR/cloudflare-tunnel-config.yaml" ]; then
    log_info "Creating Cloudflare Tunnel configuration..."
    cat > "$PROJECT_DIR/cloudflare-tunnel-config.yaml" << 'EOF'
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLOUDFLARE TUNNEL CONFIGURATION (SIMPLIFIED)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Tunnel Name: dashboard-panel
# Domain: dashboard.jujulefek.qzz.io
# Local Port: 7860 (Panel + Dashboard dalam 1 port)
#
# Flow:
# https://dashboard.jujulefek.qzz.io
#        ↓ (Cloudflare Tunnel)
# localhost:7860
#        ↓
# Agent Panel + Dashboard UI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tunnel: dashboard-panel
credentials-file: /root/.cloudflared/cert.pem

# Logging
logfile: /var/log/cloudflared/tunnel.log
loglevel: info

ingress:
  # Single route untuk Panel + Dashboard
  - hostname: dashboard.jujulefek.qzz.io
    service: http://localhost:7860
    originRequest:
      httpHostHeader: dashboard.jujulefek.qzz.io

  # Catch-all untuk undefined routes
  - service: http_status:404
EOF
    log_success "cloudflare-tunnel-config.yaml created"
else
    log_warn "Cloudflare config already exists. Skipping..."
fi

# Create startup script
if [ ! -f "$PROJECT_DIR/start-services.sh" ]; then
    log_info "Creating startup script..."
    cat > "$PROJECT_DIR/start-services.sh" << 'EOF'
#!/bin/bash

################################################################################
# START ALL SERVICES (SIMPLIFIED)
# ┌──────────────────────────────────────────────────────────────┐
# │ Port 7860: Panel + Dashboard (single port)                  │
# │ Cloudflare: Tunnel ke dashboard.jujulefek.qzz.io            │
# └──────────────────────────────────────────────────────────────┘
################################################################################

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

# Source virtual environment
source "$VENV_DIR/bin/activate"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║    🚀 PANEL + DASHBOARD STARTUP (Single Port) 🚀           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "[INFO] Project Dir: $PROJECT_DIR"
echo "[INFO] Logs Dir: $LOG_DIR"
echo "[INFO] Tunnel URL: dashboard.jujulefek.qzz.io"
echo ""

# Cleanup old processes
echo "[INFO] Cleaning up old processes..."
pkill -f "python.*agent.py" || true
pkill -f "python.*dashboard.py" || true
pkill -f "cloudflared" || true

sleep 2

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start Panel + Dashboard (Port 7860) - All in one
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "[✓] Starting Agent Panel + Dashboard on Port 7860..."
cd "$PROJECT_DIR"
python agent.py > "$LOG_DIR/panel.log" 2>&1 &
PANEL_PID=$!
echo "    PID: $PANEL_PID"
echo "    Panel: http://localhost:7860"
echo "    Dashboard: http://localhost:7860/dashboard.html"
echo "    Public: https://dashboard.jujulefek.qzz.io"

sleep 3

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start Cloudflare Tunnel
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "[✓] Starting Cloudflare Tunnel..."
cloudflared tunnel --config "$PROJECT_DIR/cloudflare-tunnel-config.yaml" run > "$LOG_DIR/cloudflare.log" 2>&1 &
CLOUDFLARE_PID=$!
echo "    PID: $CLOUDFLARE_PID"

# Save PIDs to file
echo "$PANEL_PID" > "$LOG_DIR/panel.pid"
echo "$CLOUDFLARE_PID" > "$LOG_DIR/cloudflare.pid"

sleep 3

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Verify Services Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   SERVICE STATUS CHECK                     ║"
echo "╚════════════════════════════════════════════════════════════╝"

SERVICE_OK=true

if ps -p $PANEL_PID > /dev/null 2>&1; then
    echo "[✓] Panel + Dashboard: RUNNING (PID: $PANEL_PID)"
else
    echo "[✗] Panel + Dashboard: FAILED - Check logs/panel.log"
    SERVICE_OK=false
fi

if ps -p $CLOUDFLARE_PID > /dev/null 2>&1; then
    echo "[✓] Cloudflare Tunnel: RUNNING (PID: $CLOUDFLARE_PID)"
else
    echo "[✗] Cloudflare Tunnel: FAILED - Check logs/cloudflare.log"
    SERVICE_OK=false
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Access Information
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if [ "$SERVICE_OK" = true ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║               📊 YOUR SERVICES ARE READY 📊               ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 PUBLIC ACCESS (via Cloudflare Tunnel):"
    echo "   Dashboard: https://dashboard.jujulefek.qzz.io"
    echo "   Dashboard: https://dashboard.jujulefek.qzz.io/dashboard.html"
    echo ""
    echo "💻 LOCAL ACCESS (Direct):"
    echo "   Panel: http://localhost:7860"
    echo "   Dashboard: http://localhost:7860/dashboard.html"
    echo ""
    echo "📋 FEATURES:"
    echo "   ✓ Agent Panel (Full automation control)"
    echo "   ✓ Dashboard UI (Real-time monitoring)"
    echo "   ✓ SQLite Database (Metrics storage)"
    echo "   ✓ Cloudflare Tunnel (Secure remote access)"
    echo ""
    echo "📁 LOG FILES (Real-time Monitoring):"
    echo "   Panel: tail -f $LOG_DIR/panel.log"
    echo "   Tunnel: tail -f $LOG_DIR/cloudflare.log"
    echo ""
    echo "🛑 STOP SERVICES:"
    echo "   ./stop-services.sh"
    echo ""
else
    echo "⚠️  SOME SERVICES FAILED TO START"
    echo ""
    echo "📋 CHECK LOGS:"
    echo "   Panel: cat $LOG_DIR/panel.log"
    echo "   Tunnel: cat $LOG_DIR/cloudflare.log"
    echo ""
fi

echo "╚════════════════════════════════════════════════════════════╝"
echo ""
EOF
    chmod +x "$PROJECT_DIR/start-services.sh"
    log_success "Startup script created"
else
    log_warn "Startup script already exists"
fi

# Create stop script
if [ ! -f "$PROJECT_DIR/stop-services.sh" ]; then
    log_info "Creating stop script..."
    cat > "$PROJECT_DIR/stop-services.sh" << 'EOF'
#!/bin/bash

################################################################################
# STOP ALL SERVICES
################################################################################

echo "🛑 Stopping all services..."
echo ""

if pkill -f "python.*agent.py"; then
    echo "[✓] Panel + Dashboard stopped"
else
    echo "[!] Panel + Dashboard not running"
fi

if pkill -f "cloudflared"; then
    echo "[✓] Cloudflare Tunnel stopped"
else
    echo "[!] Cloudflare Tunnel not running"
fi

sleep 2

if ! pgrep -f "python.*agent.py" > /dev/null && \
   ! pgrep -f "cloudflared" > /dev/null; then
    echo ""
    echo "[✓] All services stopped successfully"
else
    echo ""
    echo "[!] Some processes may still be running"
    echo "    Try: pkill -9 -f 'agent\|cloudflared'"
fi
echo ""
EOF
    chmod +x "$PROJECT_DIR/stop-services.sh"
    log_success "Stop script created"
else
    log_warn "Stop script already exists"
fi

# Create monitoring script
if [ ! -f "$PROJECT_DIR/monitor-services.sh" ]; then
    log_info "Creating monitoring script..."
    cat > "$PROJECT_DIR/monitor-services.sh" << 'EOF'
#!/bin/bash

################################################################################
# MONITOR SERVICES STATUS
################################################################################

LOG_DIR="./logs"
PANEL_PORT=7860

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🔍 SERVICE MONITORING DASHBOARD 🔍            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check ports
echo "📡 PORT STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if netstat -tlnp 2>/dev/null | grep ":${PANEL_PORT} " > /dev/null; then
    echo "[✓] Port $PANEL_PORT (Panel + Dashboard): LISTENING"
else
    echo "[✗] Port $PANEL_PORT (Panel + Dashboard): NOT LISTENING"
fi

echo ""
echo "📊 RECENT LOG ENTRIES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "[Panel + Dashboard] (Port $PANEL_PORT)"
if [ -f "$LOG_DIR/panel.log" ]; then
    tail -n 5 "$LOG_DIR/panel.log" | sed 's/^/  /'
else
    echo "  (No log file yet)"
fi

echo ""
echo "[Cloudflare Tunnel]"
if [ -f "$LOG_DIR/cloudflare.log" ]; then
    tail -n 5 "$LOG_DIR/cloudflare.log" | sed 's/^/  /'
else
    echo "  (No log file yet)"
fi

echo ""
echo "⚙️  RUNNING PROCESSES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep -E "python.*agent|cloudflared" | grep -v grep || echo "  (No processes running)"

echo ""
EOF
    chmod +x "$PROJECT_DIR/monitor-services.sh"
    log_success "Monitoring script created"
else
    log_warn "Monitoring script already exists"
fi

# Create SETUP reference document
if [ ! -f "$PROJECT_DIR/SETUP-GUIDE.md" ]; then
    log_info "Creating SETUP guide..."
    cat > "$PROJECT_DIR/SETUP-GUIDE.md" << 'EOF'
# 🚀 DASHBOARD PANEL + CLOUDFLARE TUNNEL SETUP GUIDE

## Overview

```
┌────────────────────────────────────────────────────────────┐
│ YOUR SERVER (localhost:7860)                               │
│ ├─ Agent Panel (Full automation control)                  │
│ └─ Dashboard UI (Real-time monitoring)                    │
│        ↓ Cloudflare Tunnel (Encrypted)                    │
│ https://dashboard.jujulefek.qzz.io                         │
│ ├─ Access Panel                                            │
│ └─ Monitor Dashboard                                       │
└────────────────────────────────────────────────────────────┘
```

## Single Port Configuration

- **Port 7860** = Agent Panel + Dashboard (semua dalam 1 port)
  - Panel yang sudah ada sebelumnya
  - Dashboard HTML untuk monitoring
  - Keduanya berjalan di Flask app yang sama

## Installation Steps

### 1️⃣ Install Dependencies

```bash
chmod +x install-dashboard.sh
./install-dashboard.sh
```

Script ini akan:
- ✅ Check system requirements
- ✅ Create Python virtual environment
- ✅ Install Python packages
- ✅ Install Cloudflare Tunnel (cloudflared)
- ✅ Create configuration files
- ✅ Create service scripts

### 2️⃣ Setup Cloudflare Tunnel Authentication

```bash
cloudflared tunnel login
```

- Browser akan membuka halaman Cloudflare
- Login dengan akun Cloudflare Anda
- Pilih domain: `jujulefek.qzz.io`
- Authorize the tunnel
- Credentials tersimpan di: `~/.cloudflared/cert.pem`

### 3️⃣ Create & Configure Tunnel

```bash
# Create tunnel
cloudflared tunnel create dashboard-panel

# Setup DNS route (single domain untuk 1 port)
cloudflared tunnel route dns dashboard-panel dashboard.jujulefek.qzz.io

# Verify setup
cloudflared tunnel list
```

### 4️⃣ Start Services

```bash
cd /path/to/dashboard-panel
./start-services.sh
```

Services yang dimulai:
- **Port 7860**: Agent Panel + Dashboard (Flask)
- **Cloudflare Tunnel**: Tunnel ke dashboard.jujulefek.qzz.io

### 5️⃣ Monitor Services

Buka terminal baru:

```bash
./monitor-services.sh
```

Atau lihat logs:

```bash
tail -f logs/panel.log
tail -f logs/cloudflare.log
```

## Access Your Dashboard

### Public Access (via Cloudflare Tunnel)
```
https://dashboard.jujulefek.qzz.io
https://dashboard.jujulefek.qzz.io/dashboard.html
```

### Local Access (Direct)
```
http://localhost:7860
http://localhost:7860/dashboard.html
```

## Service Management

### Start Services
```bash
./start-services.sh
```

### Stop Services
```bash
./stop-services.sh
```

### Monitor Status
```bash
./monitor-services.sh
```

### Check Logs
```bash
tail -f logs/panel.log      # Panel + Dashboard logs
tail -f logs/cloudflare.log # Tunnel logs
```

## Troubleshooting

### Port Already in Use
```bash
lsof -i :7860
kill -9 <PID>
```

### Tunnel Connection Failed
```bash
# Check cloudflared
cloudflared --version

# Check tunnel status
cloudflared tunnel list

# Restart tunnel
pkill -f cloudflared
./start-services.sh
```

### Can't Access from Public URL
```bash
# 1. Check tunnel running
ps aux | grep cloudflared

# 2. Check tunnel logs
tail -f logs/cloudflare.log

# 3. Verify DNS
nslookup dashboard.jujulefek.qzz.io

# 4. Test tunnel
curl -v https://dashboard.jujulefek.qzz.io
```

### No Data in Dashboard
```bash
# 1. Check panel logs
tail logs/panel.log

# 2. Check database
sqlite3 dashboard_metrics.db "SELECT COUNT(*) FROM events"

# 3. Restart panel
./stop-services.sh
./start-services.sh
```

## Configuration Files

### .env
```bash
DASHBOARD_PORT=7860
CLOUDFLARE_TOKEN=YOUR_TOKEN_HERE
```

### cloudflare-tunnel-config.yaml
```yaml
tunnel: dashboard-panel
ingress:
  - hostname: dashboard.jujulefek.qzz.io
    service: http://localhost:7860
  - service: http_status:404
```

## Features

✅ **Agent Panel** - Full automation control panel  
✅ **Dashboard UI** - Real-time monitoring interface  
✅ **SQLite Database** - Metrics & history storage  
✅ **Cloudflare Tunnel** - Secure remote access (TLS 1.3)  
✅ **Single Port** - All services on port 7860  

## Architecture

```
Local Server:
┌──────────────────────┐
│ Agent Panel (7860)   │
├──────────────────────┤
│ • Full Panel UI      │
│ • Admin Controls     │
│ • Config Management  │
└──────────────────────┘
┌──────────────────────┐
│ Dashboard (7860)     │
├──────────────────────┤
│ • Monitoring UI      │
│ • Real-time Charts   │
│ • Analytics          │
│ • History Logs       │
└──────────────────────┘
         ↓ (same port 7860)
    Cloudflare Tunnel
         ↓
Public Internet:
https://dashboard.jujulefek.qzz.io
```

## Data Flow

1. **Panel kirim data** → Agent App (Port 7860)
2. **Data disimpan** → SQLite Database
3. **Dashboard baca data** → dari Database
4. **Dashboard tampilkan** → Real-time Charts & Metrics
5. **User akses** → via Cloudflare Tunnel (dashboard.jujulefek.qzz.io)

## Next Steps

1. ✅ Run `./install-dashboard.sh`
2. ✅ Run `cloudflared tunnel login`
3. ✅ Run `cloudflared tunnel create dashboard-panel`
4. ✅ Run `cloudflared tunnel route dns dashboard-panel dashboard.jujulefek.qzz.io`
5. ✅ Run `./start-services.sh`
6. ✅ Open `https://dashboard.jujulefek.qzz.io`

Happy monitoring! 🎉
EOF
    log_success "SETUP guide created"
else
    log_warn "SETUP guide already exists"
fi

################################################################################
# SECTION 6: VERIFY INSTALLATION
################################################################################
log_info "=== VERIFYING INSTALLATION ==="

log_info "Checking Python packages..."
pip list | grep -E "Flask|flask-cors|selenium|psutil|requests" || log_warn "Some packages might not be listed"

log_info "Checking Cloudflared..."
cloudflared --version

log_info "Checking required files..."
required_files=("agent.py" "dashboard.html" "dashboard_integration.py")
for file in "${required_files[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        log_success "Found: $file"
    else
        log_warn "Missing: $file (make sure it exists in repo)"
    fi
done

################################################################################
# FINAL SUMMARY
################################################################################
log_info "=== INSTALLATION COMPLETE ==="

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🎉 DASHBOARD PANEL INSTALLATION COMPLETE! 🎉            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Project Directory:  $PROJECT_DIR"
echo "🐍 Virtual Environment: $VENV_DIR"
echo ""
echo "⚙️  CONFIGURATION SUMMARY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Tunnel Domain:      dashboard.jujulefek.qzz.io"
echo "  Local Port:         $DASHBOARD_PORT (Panel + Dashboard)"
echo "  Environment:        .env"
echo "  Tunnel Config:      cloudflare-tunnel-config.yaml"
echo ""
echo "🚀 QUICK START:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Setup Cloudflare Tunnel Authentication:"
echo "    cloudflared tunnel login"
echo ""
echo "2️⃣  Create Tunnel:"
echo "    cloudflared tunnel create dashboard-panel"
echo ""
echo "3️⃣  Setup DNS Route:"
echo "    cloudflared tunnel route dns dashboard-panel dashboard.jujulefek.qzz.io"
echo ""
echo "4️⃣  Start All Services:"
echo "    cd $PROJECT_DIR"
echo "    ./start-services.sh"
echo ""
echo "5️⃣  Monitor (new terminal):"
echo "    ./monitor-services.sh"
echo ""
echo "6️⃣  Access:"
echo "    🌐 Public:  https://dashboard.jujulefek.qzz.io"
echo "    💻 Local:   http://localhost:7860"
echo ""
echo "7️⃣  Stop Services:"
echo "    ./stop-services.sh"
echo ""
echo "📖 DOCUMENTATION:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Lihat: SETUP-GUIDE.md untuk detail lengkap"
echo ""
echo "✅ Installation Status:"
echo "   [✓] Python 3 & pip3"
echo "   [✓] Virtual environment"
echo "   [✓] Python dependencies"
echo "   [✓] Cloudflared"
echo "   [✓] Configuration files"
echo "   [✓] Service scripts"
echo ""
log_success "Ready to start services!"
echo ""
