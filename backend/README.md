# ECFR Metrics Backend

FastAPI backend for analyzing Electronic Code of Federal Regulations (ECFR) XML data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Health check
- `POST /api/analyze` - Upload and analyze ECFR XML file
- `GET /api/sample-metrics` - Get sample metrics for demonstration

## Testing

Upload the sample XML file:
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_ecfr.xml"
```
