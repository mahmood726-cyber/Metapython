# MetaPython GUI Documentation

## 🎨 World-Class Modern Web Interface

MetaPython v1.0.0 includes a **best-in-class React dashboard** with advanced visualizations, real-time collaboration, and Grafana integration.

---

## 🏗️ Architecture Overview

### **Frontend Stack (2025 Best Practices)**

- **React 18.2** with TypeScript
- **Vite** for lightning-fast builds
- **Material-UI v5** for modern components
- **Recharts** for advanced charts
- **Plotly.js** for interactive 3D visualizations
- **React Query** for server state management
- **Zustand** for client state management
- **Socket.io** for real-time collaboration

### **Backend Stack**

- **FastAPI** for high-performance async API
- **WebSocket** for real-time updates
- **Prometheus** for metrics export
- **Grafana** for advanced monitoring dashboards

---

## 📦 Installation & Setup

### **1. Install Backend Dependencies**

```bash
# Install API dependencies
cd /path/to/Metapython
pip install -r api/requirements.txt
```

### **2. Install Frontend Dependencies**

```bash
# Install Node.js dependencies
cd frontend
npm install
```

### **3. Start the Development Servers**

**Terminal 1 - Backend (FastAPI):**
```bash
cd api
python main.py
# API will run on http://localhost:8000
```

**Terminal 2 - Frontend (React):**
```bash
cd frontend
npm run dev
# UI will run on http://localhost:3000
```

### **4. Access the Application**

- **Web Interface:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Prometheus Metrics:** http://localhost:8000/metrics

---

## 🎯 Key Features

### **1. Interactive Dashboards**

#### **Home Dashboard**
- Overview of all features
- Quick access to analysis tools
- Statistics and highlights

#### **Analytics Dashboard**
- Real-time metrics cards
- Time-series visualizations
- Analysis status tracking
- Live forest plots and funnel plots

### **2. Advanced Visualizations**

#### **Forest Plots**
- Interactive hover tooltips
- Confidence interval visualization
- Weight-based marker sizing
- Pooled effect display

#### **Funnel Plots**
- Asymmetry detection
- 95% CI contours
- Publication bias indicators

#### **Heterogeneity Charts**
- I² statistic with interpretation
- τ² visualization
- Cochran's Q display
- Interactive bar charts

### **3. Meta-Analysis Interface**

- **Multiple Methods:**
  - Random Effects
  - Fixed Effects
  - REML
  - Maximum Likelihood
  - Empirical Bayes

- **Results Display:**
  - Pooled effect with CI
  - P-values and z-scores
  - Heterogeneity metrics
  - Study-level details

### **4. Real-Time Collaboration**

- WebSocket-based live updates
- Multi-user session support
- Shared cursor tracking
- Real-time chat
- Collaborative analysis editing

### **5. ML Predictions**

- Heterogeneity prediction
- Publication bias detection
- Feature importance visualization
- Model confidence scores

### **6. Grafana Integration**

- Pre-built dashboard templates
- Prometheus metrics export
- Real-time monitoring
- Custom alert rules

---

## 🎨 Component Library

### **Layout Components**

```typescript
import MainLayout from '@components/layout/MainLayout';
import Sidebar from '@components/layout/Sidebar';
import Header from '@components/layout/Header';
```

### **Chart Components**

```typescript
import ForestPlot from '@components/charts/ForestPlot';
import FunnelPlot from '@components/charts/FunnelPlot';
import HeterogeneityChart from '@components/charts/HeterogeneityChart';
```

**Usage Example:**

```tsx
<ForestPlot
  studies={studies}
  pooledEffect={0.485}
  pooledCI={[0.320, 0.650]}
  showWeights={true}
  height={500}
/>
```

### **State Management**

```typescript
// Analysis Store
import { useAnalysisStore } from '@stores/analysisStore';

const {
  studies,
  currentResult,
  setStudies,
  addStudy,
  removeStudy
} = useAnalysisStore();

// UI Store
import { useUIStore } from '@stores/uiStore';

const {
  theme,
  toggleTheme,
  sidebarOpen,
  toggleSidebar
} = useUIStore();

// Collaboration Store
import { useCollaborationStore } from '@stores/collaborationStore';

const {
  joinSession,
  sendMessage,
  messages
} = useCollaborationStore();
```

### **API Hooks**

```typescript
import {
  useRunMetaAnalysis,
  usePublicationBias,
  useSensitivityAnalysis,
  useDashboardMetrics
} from '@hooks/useMetaAnalysis';

// Run analysis
const runAnalysis = useRunMetaAnalysis();
runAnalysis.mutate();

// Get dashboard metrics
const { data, isLoading } = useDashboardMetrics();
```

---

## 🚀 API Endpoints

### **Meta-Analysis**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/meta-analysis/run` | Run meta-analysis |
| POST | `/api/meta-analysis/publication-bias` | Assess publication bias |
| POST | `/api/meta-analysis/sensitivity` | Sensitivity analysis |
| POST | `/api/meta-analysis/bayesian` | Bayesian analysis |

### **ML Predictions**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ml/predict-heterogeneity` | Predict I² |
| POST | `/api/ml/detect-bias` | Detect publication bias |

### **Data Management**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/data/upload` | Upload dataset |
| GET | `/api/data/datasets` | List datasets |

### **Dashboard**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/metrics` | Get dashboard metrics |
| GET | `/metrics` | Prometheus metrics |

### **WebSocket**

| Endpoint | Description |
|----------|-------------|
| WS `/ws/{session_id}` | Real-time collaboration |

---

## 📊 Grafana Dashboard Setup

### **1. Start Grafana**

```bash
# Using Docker
docker run -d -p 3001:3000 --name=grafana grafana/grafana
```

### **2. Add Prometheus Data Source**

1. Open Grafana at http://localhost:3001
2. Go to Configuration → Data Sources
3. Add Prometheus data source
4. Set URL to your Prometheus instance

### **3. Import MetaPython Dashboard**

Use the Python API to generate dashboard config:

```python
from metapython.grafana.dashboard_builder import create_meta_analysis_dashboard

dashboard = create_meta_analysis_dashboard()
dashboard.save_json('dashboard.json')
```

Then import `dashboard.json` in Grafana.

---

## 🎨 Theming & Customization

### **Theme Configuration**

Edit `src/App.tsx`:

```typescript
const theme = createTheme({
  palette: {
    mode: 'light', // or 'dark'
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});
```

### **Custom Color Schemes**

Modify chart colors in individual components:

```typescript
// ForestPlot.tsx
fill={theme.palette.primary.main}
```

---

## 🔧 Advanced Configuration

### **Environment Variables**

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

### **Build for Production**

```bash
# Frontend
cd frontend
npm run build
# Output in frontend/dist

# Backend
cd api
# Use production ASGI server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 📈 Performance Optimization

### **Frontend**

- **Code Splitting:** Automatic with Vite
- **Lazy Loading:** Pages loaded on demand
- **Memoization:** React.memo for expensive components
- **Virtual Scrolling:** For large study lists

### **Backend**

- **Async Operations:** All endpoints use async/await
- **Connection Pooling:** Database connections reused
- **Caching:** Redis for frequently accessed data
- **CDN:** Static assets served via CDN

---

## 🧪 Testing

### **Frontend Tests**

```bash
cd frontend
npm run test
```

### **Backend Tests**

```bash
pytest api/tests/
```

---

## 📚 API Usage Examples

### **Run Meta-Analysis**

```python
import requests

data = {
    "studies": [
        {"id": "1", "label": "Study 1", "effect": 0.5, "se": 0.1, "n": 100},
        {"id": "2", "label": "Study 2", "effect": 0.6, "se": 0.12, "n": 150},
    ],
    "method": "random"
}

response = requests.post("http://localhost:8000/api/meta-analysis/run", json=data)
result = response.json()

print(f"Pooled Effect: {result['pooled_effect']}")
print(f"I²: {result['heterogeneity']['I2']}%")
```

### **WebSocket Collaboration**

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:8000');

socket.on('connect', () => {
  socket.emit('join_session', { sessionId: 'room1', userName: 'User1' });
});

socket.on('analysis_update', (data) => {
  console.log('New analysis results:', data);
});
```

---

## 🌟 Unique Features

### **1. World-First Transportability UI**
- Interactive target population selection
- Similarity score visualization
- Adjusted effect display

### **2. Component-Based Meta-Analysis (CBAMM) Interface**
- Drag-and-drop component selection
- Interaction matrix editor
- Predicted effect calculator

### **3. INLA Bayesian Interface**
- Prior distribution visualizer
- Posterior plot display
- Convergence diagnostics

### **4. Real-Time Collaboration**
- Multi-user analysis sessions
- Shared cursors
- Live chat
- Synchronized views

---

## 🐛 Troubleshooting

### **Port Already in Use**

```bash
# Change port in vite.config.ts
server: {
  port: 3001  // Use different port
}
```

### **API Connection Failed**

Check that backend is running:
```bash
curl http://localhost:8000/health
```

### **WebSocket Not Connecting**

Ensure CORS is properly configured in `api/main.py`.

---

## 📖 Further Reading

- [React Documentation](https://react.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Material-UI Documentation](https://mui.com/)
- [Recharts Documentation](https://recharts.org/)
- [Grafana Documentation](https://grafana.com/docs/)

---

## 🎉 Conclusion

MetaPython's GUI represents the **most advanced meta-analysis web interface** available, combining:

✅ Modern React architecture
✅ Real-time collaboration
✅ Advanced visualizations
✅ ML-powered insights
✅ Production-ready deployment
✅ Comprehensive documentation

**Start building world-class meta-analyses today!** 🚀
