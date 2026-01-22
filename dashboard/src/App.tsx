import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Play } from 'lucide-react';
import AssetSelector from './components/AssetSelector';
import StrategySelector from './components/StrategySelector';
import PerformanceChart from './components/PerformanceChart';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [baskets, setBaskets] = useState<string[]>([]);
  const [basketMap, setBasketMap] = useState<Record<string, string[]>>({});

  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [selectedBasket, setSelectedBasket] = useState<string>('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stratRes, assetRes] = await Promise.all([
          axios.get(`${API_URL}/strategies`),
          axios.get(`${API_URL}/assets`)
        ]);
        setStrategies(stratRes.data);
        if (stratRes.data.length > 0) setSelectedStrategy(stratRes.data[0].id);

        const assetData = assetRes.data.baskets;
        setBasketMap(assetData);
        const basketNames = Object.keys(assetData);
        setBaskets(basketNames);
        if (basketNames.length > 0) setSelectedBasket(basketNames[0]);

      } catch (err) {
        console.error("Failed to fetch initial data", err);
      }
    };
    fetchData();
  }, []);

  const runBacktest = async () => {
    if (!selectedStrategy || !selectedBasket) return;

    setLoading(true);
    try {
      const payload = {
        strategy: selectedStrategy,
        basket: basketMap[selectedBasket], // Send list of symbols
        params: {} // Use defaults for now
      };

      const res = await axios.post(`${API_URL}/backtest`, payload);
      setResults(res.data.results);
    } catch (err) {
      console.error("Backtest failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <Activity size={24} className="text-indigo-500" />
          <h1>Momontum</h1>
        </div>

        <div className="controls">
          <AssetSelector
            baskets={baskets}
            selected={selectedBasket}
            onSelect={setSelectedBasket}
          />

          <div className="divider" />

          <StrategySelector
            strategies={strategies}
            selected={selectedStrategy}
            onSelect={setSelectedStrategy}
          />

          <button
            className="run-btn"
            onClick={runBacktest}
            disabled={loading}
          >
            <Play size={18} fill="currentColor" />
            {loading ? 'Running...' : 'Run Backtest'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <PerformanceChart results={results} />

        {/* Placeholder for future Timeline / Signals table */}
        <div className="grid grid-cols-1 gap-4 mt-4">
          {/* Detailed table could go here */}
        </div>
      </main>
    </div>
  );
}

export default App;
