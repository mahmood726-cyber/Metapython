# Frontend Status

## Current Status: No Frontend

MetaPython is currently a **backend Python/R statistical analysis package** focused on:
- Meta-analysis computations
- Statistical modeling
- R package integration (metafor, meta)
- Data processing and visualization

## Why No Frontend?

This package is designed to be:
1. **Used programmatically** - Import and use in Python scripts
2. **CLI-based** - Command-line interface for analysis
3. **Notebook-friendly** - Works in Jupyter notebooks
4. **API-ready** - Can be exposed via FastAPI for web services

## Future Frontend Considerations

If a web UI is needed in the future, consider:

### Option 1: Streamlit Dashboard
```bash
pip install streamlit
streamlit run app.py
```
- Quick to develop
- Python-native
- Good for data science applications

### Option 2: React + FastAPI
```bash
# Backend: FastAPI serves API
# Frontend: React consumes API
npm create vite@latest frontend -- --template react-ts
```
- More scalable
- Better for complex UIs
- Requires separate frontend build

### Option 3: Jupyter Notebook Extension
- Use ipywidgets for interactive controls
- Keep everything in Python
- Good for research workflows

## Current Usage

```python
from metapython import MetaAnalysis

# Use in Python
ma = MetaAnalysis(data)
results = ma.run()
results.plot()
```

For API access:
```python
# main.py
from fastapi import FastAPI
from metapython import MetaAnalysis

app = FastAPI()

@app.post("/analyze")
def analyze(data: dict):
    ma = MetaAnalysis(data)
    return ma.run()
```

## Contributing

If you want to add a frontend:
1. Create `frontend/` directory
2. Add `package.json` with dependencies
3. Update `.github/workflows/frontend-ci.yml`
4. Enable the disabled jobs in the workflow
5. Submit a PR with your frontend implementation
