'use client';

import { useState } from 'react';
import MetricsDisplay from '@/components/MetricsDisplay';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Metrics {
  total_elements: number;
  total_sections: number;
  total_parts: number;
  total_subparts: number;
  element_distribution: Record<string, number>;
  section_count_by_part: Record<string, number>;
  text_length_stats: {
    mean: number;
    min: number;
    max: number;
    total_chars: number;
  };
}

export default function Home() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<Metrics>(`${API_BASE_URL}/api/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMetrics(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze file. Please try again.');
      console.error('Error uploading file:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSampleData = async () => {
    setLoading(true);
    setError(null);
    setFileName('Sample Data');

    try {
      const response = await axios.get<Metrics>(`${API_BASE_URL}/api/sample-metrics`);
      setMetrics(response.data);
    } catch (err: any) {
      setError('Failed to load sample data. Please ensure the backend is running.');
      console.error('Error loading sample data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <div className="header">
        <h1>ECFR Metrics Dashboard</h1>
        <p>Analyze and Visualize Electronic Code of Federal Regulations XML Data</p>
      </div>

      <div className="container">
        <div className="upload-section">
          <h2>Upload ECFR XML File</h2>
          <div className="file-input-wrapper">
            <input
              type="file"
              accept=".xml"
              onChange={handleFileUpload}
              className="file-input"
              disabled={loading}
            />
            <button
              onClick={loadSampleData}
              className="button button-secondary"
              disabled={loading}
            >
              Load Sample Data
            </button>
          </div>
          {fileName && (
            <div className="info" style={{ marginTop: '15px' }}>
              Analyzing: {fileName}
            </div>
          )}
        </div>

        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <p>Processing XML file...</p>
          </div>
        )}

        {metrics && !loading && <MetricsDisplay metrics={metrics} />}

        {!metrics && !loading && !error && (
          <div className="info">
            <p>
              <strong>Getting Started:</strong> Upload an ECFR XML file to analyze its structure and metrics,
              or click "Load Sample Data" to see a demonstration with sample data.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
