'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

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

interface MetricsDisplayProps {
  metrics: Metrics;
}

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140'];

export default function MetricsDisplay({ metrics }: MetricsDisplayProps) {
  // Prepare data for element distribution chart
  const elementData = Object.entries(metrics.element_distribution)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, value]) => ({
      name,
      count: value,
    }));

  // Prepare data for sections by part chart
  const sectionByPartData = Object.entries(metrics.section_count_by_part).map(([name, value]) => ({
    name,
    sections: value,
  }));

  // Prepare data for text stats
  const textStatsData = [
    { name: 'Mean Length', value: Math.round(metrics.text_length_stats.mean) },
    { name: 'Min Length', value: metrics.text_length_stats.min },
    { name: 'Max Length', value: metrics.text_length_stats.max },
  ];

  return (
    <>
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Elements</h3>
          <p className="metric-value">{metrics.total_elements.toLocaleString()}</p>
          <p className="metric-label">XML elements parsed</p>
        </div>

        <div className="metric-card">
          <h3>Sections</h3>
          <p className="metric-value">{metrics.total_sections}</p>
          <p className="metric-label">Regulatory sections</p>
        </div>

        <div className="metric-card">
          <h3>Parts</h3>
          <p className="metric-value">{metrics.total_parts}</p>
          <p className="metric-label">Regulatory parts</p>
        </div>

        <div className="metric-card">
          <h3>Subparts</h3>
          <p className="metric-value">{metrics.total_subparts}</p>
          <p className="metric-label">Regulatory subparts</p>
        </div>
      </div>

      <div className="chart-section">
        <h2>Element Distribution (Top 10)</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={elementData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#667eea" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {sectionByPartData.length > 0 && (
        <div className="chart-section">
          <h2>Sections per Part</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={sectionByPartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sections" fill="#764ba2" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="chart-section">
        <h2>Text Length Statistics</h2>
        <div className="metrics-grid" style={{ marginTop: '20px' }}>
          <div className="metric-card">
            <h3>Average Text Length</h3>
            <p className="metric-value">{Math.round(metrics.text_length_stats.mean)}</p>
            <p className="metric-label">characters</p>
          </div>
          <div className="metric-card">
            <h3>Shortest Text</h3>
            <p className="metric-value">{metrics.text_length_stats.min}</p>
            <p className="metric-label">characters</p>
          </div>
          <div className="metric-card">
            <h3>Longest Text</h3>
            <p className="metric-value">{metrics.text_length_stats.max}</p>
            <p className="metric-label">characters</p>
          </div>
          <div className="metric-card">
            <h3>Total Characters</h3>
            <p className="metric-value">{metrics.text_length_stats.total_chars.toLocaleString()}</p>
            <p className="metric-label">across all text nodes</p>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300} style={{ marginTop: '30px' }}>
          <BarChart data={textStatsData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#4facfe" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {elementData.length > 0 && (
        <div className="chart-section">
          <h2>Element Type Distribution</h2>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={elementData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="count"
              >
                {elementData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </>
  );
}
