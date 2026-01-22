import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';
import styles from './PerformanceChart.module.css';

interface Result {
    symbol: string;
    "Total PnL": string;
    Trades: number;
    "Avg PnL": string;
}

interface PerformanceChartProps {
    results: Result[];
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ results }) => {
    // Process data for Chart
    const data = results.map(r => ({
        name: r.symbol,
        pnl: parseFloat(r["Total PnL"]),
        trades: r.Trades
    }));

    const totalPnL = data.reduce((sum, item) => sum + item.pnl, 0);

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h3 className={styles.title}>
                    <TrendingUp size={16} /> Performance Metrics
                </h3>
                <div className={styles.metric}>
                    <span className={styles.label}>Total PnL:</span>
                    <span className={`${styles.value} ${totalPnL >= 0 ? styles.positive : styles.negative}`}>
                        ${totalPnL.toFixed(2)}
                    </span>
                </div>
            </div>

            <div className={styles.chartContainer}>
                {results.length === 0 ? (
                    <div className={styles.emptyState}>Run backtest to see results</div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis dataKey="name" stroke="#9ca3af" />
                            <YAxis stroke="#9ca3af" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                                itemStyle={{ color: '#e5e7eb' }}
                            />
                            <Legend />
                            <Bar dataKey="pnl" fill="#4f46e5" name="PnL (USDT)" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
};

export default PerformanceChart;
