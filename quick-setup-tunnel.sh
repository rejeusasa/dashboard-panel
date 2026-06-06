#!/bin/bash

################################################################################
# 🔧 QUICK SETUP GUIDE FOR CLOUDFLARE TUNNEL (SIMPLIFIED)
# Single tunnel, single domain, single port
# dashboard.jujulefek.qzz.io → localhost:7860
################################################################################

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    🚀 QUICK SETUP: CLOUDFLARE TUNNEL (Single Port Mode) 🚀    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1
echo "📋 STEP 1: Authenticate with Cloudflare"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Run this command and follow browser prompt:"
echo "  $ cloudflared tunnel login"
echo ""
echo "What happens:"
echo "  • Browser akan membuka Cloudflare login page"
echo "  • Login dengan akun Cloudflare kamu"
echo "  • Pilih domain: jujulefek.qzz.io"
echo "  • Authorize the tunnel"
echo "  • Credentials akan tersimpan di ~/.cloudflared/cert.pem"
echo ""
read -p "Press ENTER after completing Cloudflare authentication... "

# Step 2
echo ""
echo "✅ STEP 2: Create Tunnel"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Creating tunnel named 'dashboard-panel'..."
cloudflared tunnel create dashboard-panel 2>/dev/null || {
    echo "⚠️  Tunnel 'dashboard-panel' already exists"
    echo "    Continuing with existing tunnel..."
}

sleep 2

# Step 3
echo ""
echo "✅ STEP 3: Setup DNS Route"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Setting up DNS route for dashboard.jujulefek.qzz.io..."
cloudflared tunnel route dns dashboard-panel dashboard.jujulefek.qzz.io
echo "[✓] DNS route configured"

sleep 2

# Step 4
echo ""
echo "✅ STEP 4: Verify Tunnel Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your tunnels:"
cloudflared tunnel list
echo ""

sleep 2

# Step 5
echo ""
echo "✅ STEP 5: Install Dashboard Panel Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press ENTER to run installation script... "
chmod +x "$PROJECT_DIR/install-dashboard.sh"
"$PROJECT_DIR/install-dashboard.sh"

# Step 6
echo ""
echo "✅ STEP 6: Start All Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Ready to start Panel + Dashboard?"
read -p "Press ENTER to start services... "
cd "$PROJECT_DIR"
./start-services.sh

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 SETUP COMPLETE! 🎉                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Your Dashboard is now accessible at:"
echo "  🌐 https://dashboard.jujulefek.qzz.io"
echo "  🌐 https://dashboard.jujulefek.qzz.io/dashboard.html"
echo ""
echo "Local access:"
echo "  💻 http://localhost:7860"
echo "  💻 http://localhost:7860/dashboard.html"
echo ""
echo "Logs:"
echo "  📋 tail -f logs/panel.log"
echo "  📋 tail -f logs/cloudflare.log"
echo ""
echo "Stop services:"
echo "  🛑 ./stop-services.sh"
echo ""
