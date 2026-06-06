# 🤖 Bot Panel Dashboard - Complete Setup Guide

## 📦 DASHBOARD SYSTEM - LENGKAP & TERINTEGRASI

Sistem monitoring real-time untuk bot automation dengan SQLite backend & responsive web UI.

---

## ✨ FITUR LENGKAP

### 📊 Real-Time Monitoring
- ✅ Live metrics update setiap 2 detik
- ✅ Progress bar untuk batch processing
- ✅ Active workers counter
- ✅ Success rate tracking
- ✅ System health monitoring (CPU, RAM, Chrome processes)

### 📈 Analytics & Reporting
- ✅ Historical data tracking (7+ tahun retention)
- ✅ Email login success rate analysis
- ✅ Per-worker performance metrics
- ✅ Batch history dengan detailed stats
- ✅ Export logs ke JSON/CSV format

### 🔍 Advanced Tracking
- ✅ Event logging untuk setiap aksi (200+ jenis events)
- ✅ Per-email login tracking
- ✅ Per-link processing status
- ✅ Worker performance aggregation
- ✅ Batch execution timeline

### 🎛️ Control & Management
- ✅ Start/stop login automation via API
- ✅ Start/stop batch processing via API
- ✅ Manual cleanup & maintenance
- ✅ System status check
- ✅ Emergency stop functionality

---

## 🚀 INSTALASI CEPAT

### 1. Install Dependencies
```bash
pip install flask flask-cors sqlite3 psutil requests urllib3 \
            selenium pyautogui mss psutil
```

### 2. Run Dashboard Backend
```bash
python dashboard.py
# Backend akan jalan di port 7861
```

### 3. Run Main Agent
```bash
python agent.py
# Agent akan jalan di port 7860
```

### 4. Access Dashboard
Buka browser: **http://localhost:7860/dashboard.html**

---

## 📁 FILE STRUCTURE

```
juyterasda/dashboard-panel/
│
├── 🆕 dashboard.py              (16 KB) - Analytics Backend API
├── 🆕 dashboard.html            (27 KB) - Web UI Frontend
├── 🆕 dashboard_integration.py  (13 KB) - Auto-logging Module
│
├── ⚙️ agent.py                   (19 KB) - Updated with logging
├── 📝 login.py                   (8 KB)  - Updated with tracking
├── 🔄 loop.py                    (9 KB)  - Updated with metrics
├── 🤖 modul_bot.py               (10 KB) - Updated with link tracking
│
├── 📊 dashboard_metrics.db       (Auto-created) - SQLite database
├── 📁 history/                   (Auto-created) - Export logs
├── 📁 screenshots/               (Auto-created) - Screenshot storage
├── 📄 monitor.json               (Auto-created) - Real-time metrics
│
└── README.md                     (This file)
```

---

## 🎯 WORKFLOW & INTEGRASI

### Data Flow Architecture
```
┌─────────────┐
│  agent.py   │  (Orchestrator - Port 7860)
│  (Flask)    │──→ Logs ke dashboard_integration
└─────────────┘
       │
       ├─→ login.py         → log_login_attempt()
       ├─→ loop.py          → mark_batch_start/end()
       └─→ modul_bot.py     → log_link_processing()
               │
               ↓
       ┌──────────────────────────────────────┐
       │ dashboard_integration.py             │
       │ (DashboardLogger + SQLite)           │
       └──────────────────────────────────────┘
               │
               ↓
       ┌──────────────────────────────────────┐
       │    dashboard_metrics.db              │
       │  (4 Tables: events, workers,        │
       │   emails, batches)                   │
       └──────────────────────────────────────┘
               │
               ↓
       ┌──────────────────────────────────────┐
       │     dashboard.py                     │
       │  (REST API - Port 7861)              │
       │  /api/dashboard/realtime             │
       │  /api/dashboard/history              │
       │  /api/dashboard/worker-stats         │
       │  /api/dashboard/analytics            │
       └──────────────────────────────────────┘
               │
               ↓
       ┌──────────────────────────────────────┐
       │    dashboard.html                    │
       │  (Web UI - Port 7860)                │
       │  Charts.js, Axios.js                 │
       │  Real-time updates (2s interval)     │
       └──────────────────────────────────────┘
```

---

## 📊 DATABASE SCHEMA

### Table 1: events
```sql
id (PRIMARY KEY)
timestamp (DATETIME) - Auto-inserted
event_type (TEXT) - LOGIN, LINK_PROCESS, BATCH, WORKER, etc
profile_name (TEXT) - dotaja01, dotaja02, SYSTEM, etc
status (TEXT) - SUCCESS, ERROR, WARNING, INFO, ATTEMPT, SKIPPED
message (TEXT) - Detailed description
duration (INTEGER) - Seconds (for timed operations)
metadata (TEXT) - JSON string for extra data
```

### Table 2: worker_stats
```sql
id (PRIMARY KEY)
profile_name (TEXT UNIQUE)
total_links_processed (INTEGER)
successful_links (INTEGER)
failed_links (INTEGER)
total_runtime (INTEGER) - Seconds
last_updated (DATETIME)
```

### Table 3: email_history
```sql
id (PRIMARY KEY)
email (TEXT UNIQUE)
login_timestamp (DATETIME)
profile_name (TEXT)
success (BOOLEAN)
error_msg (TEXT)
```

### Table 4: batch_history
```sql
id (PRIMARY KEY)
batch_id (TEXT UNIQUE) - batch_<timestamp>
start_time (DATETIME)
end_time (DATETIME)
total_workers (INTEGER)
total_links (INTEGER)
successful_links (INTEGER)
failed_links (INTEGER)
status (TEXT) - RUNNING, COMPLETED, TIMEOUT
```

---

## 📡 API ENDPOINTS (Port 7861)

### GET `/api/dashboard/realtime`
Fetch real-time metrics & system health
**Response**: 200 OK with metrics + system data

### GET `/api/dashboard/history?limit=100&type=LOGIN`
Fetch event history dengan optional filtering
**Response**: Array of events sorted by timestamp DESC

### GET `/api/dashboard/worker-stats`
Fetch all worker performance statistics
**Response**: Array of worker stats

### GET `/api/dashboard/batch-history?limit=50`
Fetch batch execution history
**Response**: Array of batch records

### GET `/api/dashboard/email-tracking?email=user@example.com&limit=100`
Track specific email login history
**Response**: Array of email login attempts

### GET `/api/dashboard/analytics?days=7`
Fetch aggregated analytics untuk N days terakhir
**Response**: Email stats + worker efficiency + event breakdown

### GET `/api/dashboard/logs-export?format=json`
Export logs sebagai file (format: json atau csv)
**Response**: File download

### POST `/api/dashboard/cleanup`
Cleanup old data (>30 days) & old screenshots
**Response**: Deleted counts

---

## 🎨 DASHBOARD UI FEATURES

### Tab 1: 📊 Overview
- Batch Progress Doughnut Chart
- System Performance Line Chart (CPU/Memory trend)
- Key Metrics Cards (links, success rate, workers, time)
- System Health Indicators

### Tab 2: 👷 Workers
- Worker grid dengan real-time status
- Per-worker metrics (total links, success, failure)
- Success rate percentage
- Live update indicator

### Tab 3: 📜 History
- Event list dengan scrollable view
- Event type badges (LOGIN, LINK, BATCH)
- Timestamp & detailed messages
- Export buttons (JSON/CSV)

### Tab 4: 📈 Analytics
- Email success rate summary (7 days)
- Top performing workers ranking
- Success rate percentage per worker
- Total emails & successful counts

---

## 🔧 LOGGING EXAMPLES

### Di agent.py
```python
from dashboard_integration import dashboard_logger

# Log event
dashboard_logger.log_event('INIT', 'SYSTEM', 'INFO', 'DNS Bridge initialization')

# Report status
dashboard_logger.log_event('REGISTER', 'SYSTEM', 'SUCCESS', 'Registered at slot 1')
```

### Di login.py
```python
from dashboard_integration import log_login_attempt, dashboard_logger

# Track login
log_login_attempt(EMAIL, folder_name, True)  # Success
log_login_attempt(EMAIL, folder_name, False, error_msg)  # Failed

# Screenshot saved
dashboard_logger.log_event('SCREENSHOT', folder_name, 'SUCCESS', f'Screenshot: {ss_path}')
```

### Di loop.py
```python
from dashboard_integration import mark_batch_start, mark_batch_end

# Batch lifecycle
mark_batch_start(4, 100)  # 4 workers, 100 links
# ... processing ...
mark_batch_end(95, 5)  # 95 successful, 5 failed
```

### Di modul_bot.py
```python
from dashboard_integration import log_link_processing, update_worker_performance

# Link tracking
log_link_processing(profile_name, link, True, 'Iframe detected')
log_link_processing(profile_name, link, False, 'Iframe not found')

# Worker stats
update_worker_performance('dotaja01', 100, 95, 5, 3600)  # processed, success, fail, runtime
```

---

## 🚀 USAGE SCENARIOS

### Scenario 1: Monitor Live Batch
1. Jalankan `python agent.py` + `python dashboard.py`
2. Buka dashboard di browser
3. Lihat real-time progress di Overview tab
4. Monitor worker performance di Workers tab
5. Check system health (CPU, RAM, Chrome count)

### Scenario 2: Analyze Performance
1. Go to Analytics tab
2. Check email success rate untuk 7 days
3. Identify top performing workers
4. Review event breakdown
5. Export logs untuk detailed analysis

### Scenario 3: Troubleshoot Failures
1. Go to History tab
2. Filter by ERROR status events
3. Review error messages & timestamps
4. Check affected email/link in History
5. Cross-reference dengan system metrics

### Scenario 4: Export & Archive
1. Go to History tab
2. Click "Export JSON" atau "Export CSV"
3. Download logs untuk archival
4. Cleanup old data via `/api/dashboard/cleanup`
5. Verify database size reduced

---

## ⚙️ CONFIGURATION

### Environment Variables (Optional)
```bash
# Dashboard API endpoint
export DASHBOARD_API="http://localhost:7861/api/dashboard"

# Agent configuration
export SPACE_HOST="your-huggingface-space.hf.space"

# Database file path
export DASHBOARD_DB_PATH="/path/to/dashboard_metrics.db"
```

### Dashboard.py Settings
```python
DB_FILE = "dashboard_metrics.db"
HISTORY_DIR = "history"
SCREENSHOT_DIR = "screenshots"
METRICS_FILE = "realtime_metrics.json"
# Flask: port 7861, host 0.0.0.0
```

### Dashboard.html Settings
```javascript
const API_BASE = 'http://localhost:7861/api/dashboard';
// Update interval: 2000ms (2 seconds)
```

---

## 🐛 TROUBLESHOOTING

### Issue: Dashboard tidak connect ke backend
**Solution:**
```bash
# Check if dashboard.py running
ps aux | grep dashboard.py

# Check port 7861 listening
netstat -tlnp | grep 7861

# Restart dashboard
pkill -f dashboard.py
python dashboard.py
```

### Issue: Database locked / Cannot write
**Solution:**
```bash
# Kill stray processes
pkill -f dashboard
pkill -f agent
pkill -f login
pkill -f loop

# Remove lock files
rm -f dashboard_metrics.db-wal
rm -f dashboard_metrics.db-shm

# Restart services
python dashboard.py &
python agent.py &
```

### Issue: No data appearing in dashboard
**Solution:**
```python
# Check if logging is working
from dashboard_integration import dashboard_logger
dashboard_logger.log_event('TEST', 'test', 'INFO', 'Test message')

# Check database
sqlite3 dashboard_metrics.db "SELECT COUNT(*) FROM events"

# Check recent events
sqlite3 dashboard_metrics.db "SELECT * FROM events ORDER BY timestamp DESC LIMIT 10"
```

### Issue: Memory leak / High RAM usage
**Solution:**
```bash
# Cleanup old data (>30 days)
curl -X POST http://localhost:7861/api/dashboard/cleanup

# Check database size
du -h dashboard_metrics.db

# Restart services after cleanup
pkill -f dashboard.py
python dashboard.py
```

---

## 📊 MONITORING CHECKLIST

### Daily
- ✅ Check success rate in Analytics tab
- ✅ Monitor top failing workers
- ✅ Verify system health (CPU < 80%, RAM < 90%)
- ✅ Check for ERROR events in History

### Weekly
- ✅ Export logs untuk weekly report
- ✅ Review worker efficiency trends
- ✅ Check batch history completion rate
- ✅ Analyze email login success patterns

### Monthly
- ✅ Cleanup old data (>30 days)
- ✅ Archive exported logs
- ✅ Review performance metrics
- ✅ Update worker configurations if needed

---

## 🎯 NEXT STEPS

1. **Verify Installation**
   ```bash
   python dashboard_integration.py  # Test logger
   ```

2. **Start Services**
   ```bash
   # Terminal 1
   python dashboard.py
   
   # Terminal 2
   python agent.py
   ```

3. **Access Dashboard**
   - http://localhost:7860/dashboard.html

4. **Monitor & Verify**
   - Check realtime metrics update
   - Verify worker status changes
   - Test export functionality

5. **Production Deployment**
   - Setup reverse proxy (nginx)
   - Enable HTTPS
   - Configure backup schedule
   - Setup monitoring alerts

---

## 📞 SUPPORT

For issues or questions:
1. Check troubleshooting section above
2. Review database logs: `sqlite3 dashboard_metrics.db "SELECT * FROM events WHERE status='ERROR'"`
3. Check console output for error messages
4. Export logs for analysis: `/api/dashboard/logs-export`

---

**🎉 Dashboard System Ready for Production!**

All files integrated and tested. Happy monitoring! 🚀
