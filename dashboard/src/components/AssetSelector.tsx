import React from 'react';
import { Layers } from 'lucide-react';
import styles from './AssetSelector.module.css';

interface AssetSelectorProps {
    baskets: string[];
    selected: string;
    onSelect: (basket: string) => void;
}

const AssetSelector: React.FC<AssetSelectorProps> = ({ baskets, selected, onSelect }) => {
    return (
        <div className={styles.container}>
            <h3 className={styles.header}>
                <Layers size={16} /> Asset Universe
            </h3>
            <div className={styles.grid}>
                {baskets.map((basket) => (
                    <button
                        key={basket}
                        onClick={() => onSelect(basket)}
                        className={`${styles.button} ${selected === basket ? styles.active : ''}`}
                    >
                        {basket}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default AssetSelector;
