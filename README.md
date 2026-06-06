# 🤖 Dashboard Panel - Bot Automation Monitor

Platform manajemen dan monitoring terpadu untuk bot automation dengan Flask backend dan React frontend.

## ✨ Fitur Utama

- **Real-time Monitoring**: Pantau worker status, queue, dan batch progress secara live
- **Worker Management**: Kontrol 50+ Chrome profiles dengan multiprocessing
- **Analytics Dashboard**: Tracking success rate, performance metrics, dan historical data
- **Log Streaming**: View logs real-time dengan filtering dan search
- **Control Panel**: Start/stop automation, manual triggers, emergency kill
- **File Monitor**: Watch email.txt, link.txt, mapping_profil.txt, monitor.json
- **Screenshot Viewer**: Preview hasil automation
- **Multi-user Auth**: Role-based access (Admin/Operator/Viewer)
- **WebSocket Support**: Push notifications dan live updates
- **System Health**: Memory usage, CPU, process count tracking

## 📋 Requirements

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (optional)
- Redis (optional, untuk caching)

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend: `http://localhost:5000`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend: `http://localhost:5173`

## 🐳 Docker Deployment

```bash
cd docker
docker-compose up -d
```

## 🔑 Default Credentials

- **Username**: admin
- **Password**: admin123
- **AUTH_KEY**: GHOST_SECRET_2026

## 📊 Monitoring Files

- `bot_log.txt` - Task logs
- `email.txt` - Email queue
- `link.txt` - Link queue
- `mapping_profil.txt` - Profile mapping
- `monitor.json` - Live worker status
- `history_sukses.txt` - Completed emails

## 🔗 API Endpoints

```
GET    /api/v1/status              - System status
GET    /api/v1/workers             - Worker list
GET    /api/v1/logs                - Bot logs
GET    /api/v1/analytics           - Charts & analytics
GET    /api/v1/monitor             - monitor.json data
POST   /api/v1/commands/start-login
POST   /api/v1/commands/start-loop
POST   /api/v1/commands/stop
POST   /api/v1/commands/clean
GET    /api/v1/screenshot          - Screenshots
WS     /ws/live                    - WebSocket for real-time updates
```

## 📁 Project Structure

```
dashboard-panel/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── routes/
│   ├── services/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
└── docs/
```

## 👨‍💻 Development

```bash
# Terminal 1: Backend
cd backend && python app.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

## 📝 License

MIT License

## 🆘 Troubleshooting

**Port 5000 already in use:**
```bash
lsof -ti:5000 | xargs kill -9
```

**WebSocket connection failed:**
- Pastikan backend berjalan
- Check CORS settings di backend/config.py

**Monitor.json not updating:**
- Pastikan loop.py sedang berjalan
- Check permissions di working directory
