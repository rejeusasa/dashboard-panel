#!/bin/bash

################################################################################
# 🚀 DASHBOARD-PANEL + CLOUDFLARE TUNNEL INSTALLATION SCRIPT
# 
# Complete setup untuk Bot Panel Dashboard dengan Cloudflare Tunnel integration
# URL: dashboard.jujulefek.qzz.io
# Dengan automatic port configuration
#
# Usage: chmod +x install-dashboard-cloudflare.sh && ./install-dashboard-cloudflare.sh
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
# - Port 7860: Agent Flask Server (dashboard.html diakses dari sini)
# - Port 7861: Dashboard Backend API (REST API endpoints)
# 
# Cloudflare Tunnel akan tunnel kedua port ini ke:
# - dashboard.jujulefek.qzz.io → Port 7860 (Frontend + HTML)
# - api.jujulefek.qzz.io → Port 7861 (API Backend)

DASHBOARD_PORT=7861    # Backend API
AGENT_PORT=7860        # Frontend + HTML Dashboard
TUNNEL_URL="dashboard.jujulefek.qzz.io"

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
# Dashboard Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Port Configuration
# DASHBOARD_PORT (7861) = Backend API Server
# AGENT_PORT (7860) = Frontend + HTML Dashboard
DASHBOARD_API=http://localhost:${DASHBOARD_PORT}/api/dashboard
DASHBOARD_PORT=${DASHBOARD_PORT}
AGENT_PORT=${AGENT_PORT}
DATABASE_PATH=./dashboard_metrics.db
HISTORY_DIR=./history
SCREENSHOT_DIR=./screenshots

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cloudflare Tunnel Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Tunnel URL - akan diakses dari public internet
CLOUDFLARE_TUNNEL_URL=https://${TUNNEL_URL}

# Token dari: cloudflared tunnel login
# Atau credentials file: ~/.cloudflared/cert.pem
CLOUDFLARE_TOKEN=YOUR_TOKEN_HERE

# Service HTTP configuration
# Ini mendefinisikan mana port yang di-tunnel ke URL publik
CLOUDFLARE_SERVICE_PORT=${AGENT_PORT}
CLOUDFLARE_API_PORT=${DASHBOARD_PORT}
EOF
    log_success ".env file created"
    log_warn "⚠ PENTING: Update CLOUDFLARE_TOKEN di .env file"
else
    log_warn ".env file already exists. Skipping..."
fi

# Create detailed cloudflared configuration dengan penjelasan
if [ ! -f "$PROJECT_DIR/cloudflare-tunnel-config.yaml" ]; then
    log_info "Creating Cloudflare Tunnel configuration..."
    cat > "$PROJECT_DIR/cloudflare-tunnel-config.yaml" << 'EOF'
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLOUDFLARE TUNNEL CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Tunnel Name: dashboard-panel
# URL: dashboard.jujulefek.qzz.io
#
# Penjelasan Port Routing:
# ┌─────────────────────────────────────────────────────────────┐
# │ LOCAL SERVER                CLOUDFLARE TUNNEL      PUBLIC   │
# ├─────────────────────────────────────────────────────────────┤
# │ localhost:7860  ──Route 1──→  dashboard.jujulefek.qzz.io    │
# │ localhost:7861  ──Route 2──→  api.jujulefek.qzz.io           │
# └─────────────────────────────────────────────────────────────┘
#
# Port 7860 = Agent Flask (Dashboard HTML & Frontend)
# Port 7861 = Dashboard API (REST API Backend)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tunnel: dashboard-panel
credentials-file: /root/.cloudflared/cert.pem

# Logging
logfile: /var/log/cloudflared/tunnel.log
loglevel: info

ingress:
  # Route 1: Dashboard Frontend (HTML, JavaScript, CSS)
  # Akses melalui: dashboard.jujulefek.qzz.io
  - hostname: dashboard.jujulefek.qzz.io
    service: http://localhost:7860
    originRequest:
      httpHostHeader: dashboard.jujulefek.qzz.io

  # Route 2: Dashboard Backend API
  # Akses melalui: api.jujulefek.qzz.io
  - hostname: api.jujulefek.qzz.io
    service: http://localhost:7861
    originRequest:
      httpHostHeader: api.jujulefek.qzz.io

  # Catch-all untuk undefined routes
  - service: http_status:404
EOF
    log_success "cloudflare-tunnel-config.yaml created"
else
    log_warn "Cloudflare config already exists. Skipping..."
fi

# Create startup script dengan port info
if [ ! -f "$PROJECT_DIR/start-services.sh" ]; then
    log_info "Creating startup script..."
    cat > "$PROJECT_DIR/start-services.sh" << 'EOF'
#!/bin/bash

################################################################################
# START ALL SERVICES
# ┌──────────────────────────────────────────────────────────────┐
# │ Port 7860: Dashboard Frontend (Agent Flask)                 │
# │ Port 7861: Dashboard Backend API                            │
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
echo "║    🚀 DASHBOARD PANEL + CLOUDFLARE TUNNEL STARTUP 🚀       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "[INFO] Project Dir: $PROJECT_DIR"
echo "[INFO] Logs Dir: $LOG_DIR"
echo "[INFO] Tunnel URL: dashboard.jujulefek.qzz.io"
echo ""

# Cleanup old processes
echo "[INFO] Cleaning up old processes..."
pkill -f "python.*dashboard.py" || true
pkill -f "python.*agent.py" || true
pkill -f "cloudflared" || true

sleep 2

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start Dashboard Backend (Port 7861) - API Server
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "[✓] Starting Dashboard Backend API on Port 7861..."
cd "$PROJECT_DIR"
python dashboard.py > "$LOG_DIR/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
echo "    PID: $DASHBOARD_PID"
echo "    API Endpoint: http://localhost:7861/api/dashboard"
echo "    Public: https://api.jujulefek.qzz.io/api/dashboard"

sleep 2

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start Agent (Port 7860) - Frontend Dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "[✓] Starting Agent Frontend on Port 7860..."
python agent.py > "$LOG_DIR/agent.log" 2>&1 &
AGENT_PID=$!
echo "    PID: $AGENT_PID"
echo "    Dashboard: http://localhost:7860/dashboard.html"
echo "    Public: https://dashboard.jujulefek.qzz.io/dashboard.html"

sleep 2

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start Cloudflare Tunnel
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "[✓] Starting Cloudflare Tunnel..."
cloudflared tunnel --config "$PROJECT_DIR/cloudflare-tunnel-config.yaml" run > "$LOG_DIR/cloudflare.log" 2>&1 &
CLOUDFLARE_PID=$!
echo "    PID: $CLOUDFLARE_PID"

# Save PIDs to file
echo "$DASHBOARD_PID" > "$LOG_DIR/dashboard.pid"
echo "$AGENT_PID" > "$LOG_DIR/agent.pid"
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

if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
    echo "[✓] Dashboard Backend API: RUNNING (PID: $DASHBOARD_PID)"
else
    echo "[✗] Dashboard Backend API: FAILED - Check logs/dashboard.log"
    SERVICE_OK=false
fi

if ps -p $AGENT_PID > /dev/null 2>&1; then
    echo "[✓] Agent Frontend: RUNNING (PID: $AGENT_PID)"
else
    echo "[✗] Agent Frontend: FAILED - Check logs/agent.log"
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
    echo "║                  📊 ACCESS YOUR DASHBOARD 📊              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 PUBLIC ACCESS (via Cloudflare Tunnel):"
    echo "   Dashboard: https://dashboard.jujulefek.qzz.io/dashboard.html"
    echo "   API: https://api.jujulefek.qzz.io/api/dashboard"
    echo ""
    echo "💻 LOCAL ACCESS (Direct):"
    echo "   Dashboard: http://localhost:7860/dashboard.html"
    echo "   API: http://localhost:7861/api/dashboard"
    echo ""
    echo "📁 API ENDPOINTS:"
    echo "   • /api/dashboard/realtime"
    echo "   • /api/dashboard/history"
    echo "   • /api/dashboard/worker-stats"
    echo "   • /api/dashboard/analytics"
    echo "   • /api/dashboard/batch-history"
    echo "   • /api/dashboard/email-tracking"
    echo ""
    echo "📋 LOG FILES (Real-time Monitoring):"
    echo "   Dashboard: tail -f $LOG_DIR/dashboard.log"
    echo "   Agent:     tail -f $LOG_DIR/agent.log"
    echo "   Tunnel:    tail -f $LOG_DIR/cloudflare.log"
    echo ""
    echo "🛑 STOP ALL SERVICES:"
    echo "   ./stop-services.sh"
    echo ""
else
    echo "⚠️  SOME SERVICES FAILED TO START"
    echo ""
    echo "📋 CHECK LOGS:"
    echo "   Dashboard: cat $LOG_DIR/dashboard.log"
    echo "   Agent:     cat $LOG_DIR/agent.log"
    echo "   Tunnel:    cat $LOG_DIR/cloudflare.log"
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

echo "🛑 Stopping all Dashboard services..."
echo ""

# Kill by process name
if pkill -f "python.*dashboard.py"; then
    echo "[✓] Dashboard Backend stopped"
else
    echo "[!] Dashboard Backend not running"
fi

if pkill -f "python.*agent.py"; then
    echo "[✓] Agent Frontend stopped"
else
    echo "[!] Agent Frontend not running"
fi

if pkill -f "cloudflared"; then
    echo "[✓] Cloudflare Tunnel stopped"
else
    echo "[!] Cloudflare Tunnel not running"
fi

sleep 2

# Verify
if ! pgrep -f "python.*dashboard.py" > /dev/null && \
   ! pgrep -f "python.*agent.py" > /dev/null && \
   ! pgrep -f "cloudflared" > /dev/null; then
    echo ""
    echo "[✓] All services stopped successfully"
else
    echo ""
    echo "[!] Some processes may still be running"
    echo "    Try: pkill -9 -f 'dashboard\|agent\|cloudflared'"
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
# MONITOR SERVICES STATUS & PORT STATUS
################################################################################

LOG_DIR="./logs"
AGENT_PORT=7860
API_PORT=7861

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🔍 SERVICE MONITORING DASHBOARD 🔍            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check ports
echo "📡 PORT STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if netstat -tlnp 2>/dev/null | grep ":${AGENT_PORT} " > /dev/null; then
    echo "[✓] Port $AGENT_PORT (Agent Frontend): LISTENING"
else
    echo "[✗] Port $AGENT_PORT (Agent Frontend): NOT LISTENING"
fi

if netstat -tlnp 2>/dev/null | grep ":${API_PORT} " > /dev/null; then
    echo "[✓] Port $API_PORT (Dashboard API): LISTENING"
else
    echo "[✗] Port $API_PORT (Dashboard API): NOT LISTENING"
fi

echo ""
echo "📊 RECENT LOG ENTRIES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "[Dashboard Backend] (Port $API_PORT)"
if [ -f "$LOG_DIR/dashboard.log" ]; then
    tail -n 3 "$LOG_DIR/dashboard.log" | sed 's/^/  /'
else
    echo "  (No log file yet)"
fi

echo ""
echo "[Agent Frontend] (Port $AGENT_PORT)"
if [ -f "$LOG_DIR/agent.log" ]; then
    tail -n 3 "$LOG_DIR/agent.log" | sed 's/^/  /'
else
    echo "  (No log file yet)"
fi

echo ""
echo "[Cloudflare Tunnel]"
if [ -f "$LOG_DIR/cloudflare.log" ]; then
    tail -n 3 "$LOG_DIR/cloudflare.log" | sed 's/^/  /'
else
    echo "  (No log file yet)"
fi

echo ""
echo "⚙️  RUNNING PROCESSES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep -E "python.*dashboard|python.*agent|cloudflared" | grep -v grep || echo "  (No processes running)"

echo ""
EOF
    chmod +x "$PROJECT_DIR/monitor-services.sh"
    log_success "Monitoring script created"
else
    log_warn "Monitoring script already exists"
fi

# Create PORT reference document
if [ ! -f "$PROJECT_DIR/PORT-CONFIGURATION.md" ]; then
    log_info "Creating PORT configuration reference..."
    cat > "$PROJECT_DIR/PORT-CONFIGURATION.md" << 'EOF'
# 🔌 PORT CONFIGURATION REFERENCE

## Dashboard Panel Setup dengan Cloudflare Tunnel

### Diagram Routing
```
┌────────────────────────────────────────────────────────────────┐
│                     YOUR INFRASTRUCTURE                         │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Local Server (Linux/Ubuntu)                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  Port 7860: Agent Flask Server (Frontend)               │ │
│  │  ├─ dashboard.html (Web UI)                              │ │
│  │  ├─ Charts.js (Visualization)                            │ │
│  │  └─ Real-time updates (2s interval)                      │ │
│  │                                                           │ │
│  │  Port 7861: Dashboard Backend API (REST API)            │ │
│  │  ├─ /api/dashboard/realtime                              │ │
│  │  ├─ /api/dashboard/history                               │ │
│  │  ├─ /api/dashboard/worker-stats                          │ │
│  │  ├─ /api/dashboard/analytics                             │ │
│  │  └─ /api/dashboard/batch-history                         │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│           ↓ Cloudflare Tunnel (cloudflared)                   │
├────────────────────────────────────────────────────────────────┤
│                   INTERNET / CLOUDFLARE                        │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Public URLs (Accessible dari mana saja)                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  https://dashboard.jujulefek.qzz.io/dashboard.html       │ │
│  │  ↓ (Tunnel ke localhost:7860)                            │ │
│  │  Frontend Dashboard + Agent Server                       │ │
│  │                                                           │ │
│  │  https://api.jujulefek.qzz.io/api/dashboard              │ │
│  │  ↓ (Tunnel ke localhost:7861)                            │ │
│  │  Backend API Server                                      │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

## PORT DETAILS

### Port 7860 - Agent Flask Server (Frontend)
```
URL Lokal:     http://localhost:7860/dashboard.html
URL Publik:    https://dashboard.jujulefek.qzz.io/dashboard.html
Fungsi:        Dashboard Web UI, HTML frontend
Flask:         Berjalan di port ini
Status:        Primary dashboard access point
```

**Apa yang terjadi di Port 7860:**
- Serve HTML file (`dashboard.html`)
- Serve JavaScript files (Charts.js, Axios.js)
- Serve CSS files (styling)
- Handle client-side requests
- Real-time updates setiap 2 detik

### Port 7861 - Dashboard Backend API (API Server)
```
URL Lokal:     http://localhost:7861/api/dashboard
URL Publik:    https://api.jujulefek.qzz.io/api/dashboard
Fungsi:        REST API backend, data processing
Flask:         Berjalan di port ini
Status:        API endpoint for dashboard data
```

**API Endpoints di Port 7861:**
- `GET /api/dashboard/realtime` - Real-time metrics
- `GET /api/dashboard/history` - Event history
- `GET /api/dashboard/worker-stats` - Worker statistics
- `GET /api/dashboard/analytics` - Analytics data
- `GET /api/dashboard/batch-history` - Batch execution history
- `GET /api/dashboard/email-tracking` - Email login tracking
- `POST /api/dashboard/cleanup` - Cleanup old data

## CLOUDFLARE TUNNEL ROUTING

### Ingress Rules (dari `cloudflare-tunnel-config.yaml`)

```yaml
ingress:
  # Rule 1: Frontend Dashboard
  - hostname: dashboard.jujulefek.qzz.io
    service: http://localhost:7860
    
  # Rule 2: Backend API
  - hostname: api.jujulefek.qzz.io
    service: http://localhost:7861
    
  # Catch-all
  - service: http_status:404
```

### Request Flow

**Scenario 1: User membuka dashboard dari internet**
```
1. User membuka: https://dashboard.jujulefek.qzz.io/dashboard.html
2. Cloudflare menerima request ke domain dashboard.jujulefek.qzz.io
3. Tunnel rules match rule 1 → route ke localhost:7860
4. Agent Flask server merespons HTML
5. Browser render dashboard.html
```

**Scenario 2: Dashboard fetch data dari API**
```
1. Frontend JavaScript membuat request ke: /api/dashboard/realtime
2. Browser URL bar menunjuk ke: https://dashboard.jujulefek.qzz.io
3. CORS request ke: https://api.jujulefek.qzz.io/api/dashboard/realtime
4. Cloudflare menerima request ke domain api.jujulefek.qzz.io
5. Tunnel rules match rule 2 → route ke localhost:7861
6. Dashboard Backend API server merespons JSON data
7. Frontend update charts dengan data baru
```

## LAYANAN YANG BERJALAN

### Services Overview

| Service | Port | Protokol | Status | Akses |
|---------|------|----------|--------|-------|
| Agent Frontend | 7860 | HTTP | Berjalan | localhost:7860 |
| Dashboard API | 7861 | HTTP | Berjalan | localhost:7861 |
| Cloudflare Tunnel | - | WSS | Berjalan | N/A (tunnel) |

## ACCESS METHODS

### Akses Lokal (dari server yang sama)
```bash
# Frontend
curl http://localhost:7860/dashboard.html

# API
curl http://localhost:7861/api/dashboard/realtime
```

### Akses Publik (dari internet)
```bash
# Frontend
curl https://dashboard.jujulefek.qzz.io/dashboard.html

# API
curl https://api.jujulefek.qzz.io/api/dashboard/realtime
```

### Via Tunnel Direct (testing)
```bash
# Lihat tunnel status
cloudflared tunnel info dashboard-panel

# List routes
cloudflared tunnel route list dashboard-panel

# DNS management
cloudflared tunnel route dns dashboard-panel dashboard.jujulefek.qzz.io
cloudflared tunnel route dns dashboard-panel api.jujulefek.qzz.io
```

## DEBUGGING

### Check Port Listening Status
```bash
# Lihat semua port yang listening
netstat -tlnp | grep -E "7860|7861"

# Atau gunakan lsof
lsof -i :7860
lsof -i :7861
```

### Test Koneksi
```bash
# Test lokal
curl -v http://localhost:7860/dashboard.html
curl -v http://localhost:7861/api/dashboard/realtime

# Test public (jika tunnel berjalan)
curl -v https://dashboard.jujulefek.qzz.io/dashboard.html
curl -v https://api.jujulefek.qzz.io/api/dashboard/realtime
```

### Check Tunnel Status
```bash
# Lihat tunnel logs
tail -f logs/cloudflare.log

# Check active tunnels
ps aux | grep cloudflared

# Test tunnel connection
curl https://dashboard.jujulefek.qzz.io
```

## FIREWALL RULES

### Jika menggunakan UFW (Ubuntu Firewall)
```bash
# Buka port 7860 untuk lokal akses
sudo ufw allow 7860

# Buka port 7861 untuk lokal akses
sudo ufw allow 7861

# Atau untuk specific IP
sudo ufw allow from 192.168.1.0/24 to any port 7860
sudo ufw allow from 192.168.1.0/24 to any port 7861
```

### Catatan Keamanan
- Port 7860 & 7861 hanya di-listen di `localhost` secara default
- Akses publik hanya via Cloudflare Tunnel (terenkripsi)
- Tunnel menggunakan TLS 1.3
- Tidak ada public exposure tanpa firewall bypass

## CONFIGURATION FILES

### .env
```bash
DASHBOARD_PORT=7861
AGENT_PORT=7860
DASHBOARD_API=http://localhost:7861/api/dashboard
```

### cloudflare-tunnel-config.yaml
```yaml
tunnel: dashboard-panel
ingress:
  - hostname: dashboard.jujulefek.qzz.io
    service: http://localhost:7860
  - hostname: api.jujulefek.qzz.io
    service: http://localhost:7861
  - service: http_status:404
```

## TROUBLESHOOTING

### Port 7860/7861 Already in Use
```bash
# Find process using port
lsof -i :7860
lsof -i :7861

# Kill the process
kill -9 <PID>

# Or use fuser
fuser -k 7860/tcp
fuser -k 7861/tcp
```

### Tunnel Connection Failed
```bash
# Check cloudflared is installed
cloudflared --version

# Check tunnel is configured
cloudflared tunnel list

# Restart tunnel
pkill -f cloudflared
./start-services.sh
```

### Can't Access from Public URL
```bash
# 1. Verify tunnel is running
ps aux | grep cloudflared

# 2. Check tunnel logs
tail -f logs/cloudflare.log

# 3. Verify DNS settings
nslookup dashboard.jujulefek.qzz.io

# 4. Test via curl
curl -v https://dashboard.jujulefek.qzz.io
```

---

**Remember:** 
- Port 7860 = Frontend (dashboard.html)
- Port 7861 = Backend API
- Both tunneled via Cloudflare to public URLs
EOF
    log_success "PORT configuration reference created"
else
    log_warn "PORT configuration reference already exists"
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
required_files=("dashboard.py" "agent.py" "dashboard.html" "dashboard_integration.py")
for file in "${required_files[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        log_success "Found: $file"
    else
        log_warn "Missing: $file (make sure it exists in repo)"
    fi
done

################################################################################
# SECTION 7: SETUP CLOUDFLARE TUNNEL TOKEN
################################################################################
log_info "=== CLOUDFLARE TUNNEL SETUP ==="

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🔐 CLOUDFLARE TUNNEL AUTHENTICATION 🔐           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  PENTING: Setup credentials Cloudflare Tunnel"
echo ""
echo "Langkah-langkah:"
echo "1. Jalankan:"
echo "   cloudflared tunnel login"
echo ""
echo "2. Browser akan membuka halaman Cloudflare"
echo "3. Login dengan akun Cloudflare Anda"
echo "4. Pilih domain: jujulefek.qzz.io"
echo "5. Authorize the tunnel"
echo ""
echo "6. Credentials akan tersimpan di:"
echo "   ~/.cloudflared/cert.pem"
echo ""
echo "7. Verify setup dengan:"
echo "   cloudflared tunnel list"
echo ""
echo "8. Create tunnel jika belum ada:"
echo "   cloudflared tunnel create dashboard-panel"
echo ""
echo "9. Setup DNS routes:"
echo "   cloudflared tunnel route dns dashboard-panel dashboard.jujulefek.qzz.io"
echo "   cloudflared tunnel route dns dashboard-panel api.jujulefek.qzz.io"
echo ""

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
echo "  Tunnel URL:         dashboard.jujulefek.qzz.io"
echo "  Frontend Port:      $AGENT_PORT (Agent Flask)"
echo "  Backend Port:       $DASHBOARD_PORT (Dashboard API)"
echo "  Environment:        .env"
echo "  Tunnel Config:      cloudflare-tunnel-config.yaml"
echo ""
echo "🚀 QUICK START:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Setup Cloudflare Tunnel Authentication:"
echo "    cloudflared tunnel login"
echo ""
echo "2️⃣  Create Tunnel (if not exists):"
echo "    cloudflared tunnel create dashboard-panel"
echo ""
echo "3️⃣  Setup DNS Routes:"
echo "    cloudflared tunnel route dns dashboard-panel dashboard.jujulefek.qzz.io"
echo "    cloudflared tunnel route dns dashboard-panel api.jujulefek.qzz.io"
echo ""
echo "4️⃣  Start All Services:"
echo "    cd $PROJECT_DIR"
echo "    ./start-services.sh"
echo ""
echo "5️⃣  Monitor Services (new terminal):"
echo "    ./monitor-services.sh"
echo "    tail -f logs/dashboard.log"
echo "    tail -f logs/agent.log"
echo "    tail -f logs/cloudflare.log"
echo ""
echo "6️⃣  Access Dashboard:"
echo "    🌐 Public:  https://dashboard.jujulefek.qzz.io/dashboard.html"
echo "    💻 Local:   http://localhost:7860/dashboard.html"
echo ""
echo "7️⃣  Access API:"
echo "    🌐 Public:  https://api.jujulefek.qzz.io/api/dashboard/realtime"
echo "    💻 Local:   http://localhost:7861/api/dashboard/realtime"
echo ""
echo "8️⃣  Stop Services:"
echo "    ./stop-services.sh"
echo ""
echo "📖 PORT REFERENCE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Port 7860 = Frontend Dashboard (Agent Flask)"
echo "  Port 7861 = Backend API (Dashboard Backend)"
echo ""
echo "  Lihat PORT-CONFIGURATION.md untuk detail lengkap"
echo ""
echo "✅ Installation Status:"
echo "   [✓] Python 3 & pip3"
echo "   [✓] Virtual environment"
echo "   [✓] Python dependencies"
echo "   [✓] Cloudflared"
echo "   [✓] Configuration files"
echo "   [✓] Service scripts"
echo "   [✓] PORT configuration reference"
echo ""
log_success "Ready to start services!"
echo ""
