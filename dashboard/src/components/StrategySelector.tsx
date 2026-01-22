import React from 'react';
import { Cpu } from 'lucide-react';
import styles from './StrategySelector.module.css';

interface Strategy {
    id: string;
    name: string;
    params: any;
}

interface StrategySelectorProps {
    strategies: Strategy[];
    selected: string;
    onSelect: (id: string) => void;
}

const StrategySelector: React.FC<StrategySelectorProps> = ({ strategies, selected, onSelect }) => {
    return (
        <div className={styles.container}>
            <h3 className={styles.header}>
                <Cpu size={16} /> Strategy Engine
            </h3>
            <div className={styles.list}>
                {strategies.map((strat) => (
                    <button
                        key={strat.id}
                        onClick={() => onSelect(strat.id)}
                        className={`${styles.card} ${selected === strat.id ? styles.active : ''}`}
                    >
                        <div className={styles.cardHeader}>
                            <span className={styles.stratName}>{strat.name}</span>
                            {selected === strat.id && <span className={styles.badge}>Active</span>}
                        </div>
                        <div className={styles.params}>
                            {Object.entries(strat.params).map(([key, val]) => (
                                <span key={key}>{key}: {String(val)}</span>
                            ))}
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default StrategySelector;
