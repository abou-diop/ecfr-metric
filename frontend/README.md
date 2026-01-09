# ECFR Metrics Frontend

Next.js frontend dashboard for visualizing Electronic Code of Federal Regulations (ECFR) metrics.

## Features

- Upload and analyze ECFR XML files
- Interactive visualizations using Recharts
- Real-time metric computation
- Sample data for demonstration

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file (optional):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Building for Production

```bash
npm run build
npm start
```

## Components

- `app/page.tsx` - Main dashboard page
- `components/MetricsDisplay.tsx` - Metrics visualization component

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default.
