class AssetManager:
    """
    Manages lists of assets (baskets) for trading.
    """
    
    BTC = ['BTC/USDT']
    ETH = ['ETH/USDT']
    
    TOP_3 = [
        'BTC/USDT', 
        'ETH/USDT', 
        'SOL/USDT'
    ]
    
    TOP_10 = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
        'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'TRX/USDT', 'LINK/USDT'
    ]
    
    # High volatility / Meme coins
    MEME_BASKET = [
        'DOGE/USDT', 'SHIB/USDT', 'PEPE/USDT', 
        'WIF/USDT', 'BONK/USDT', 'FLOKI/USDT'
    ]

    DEFI_BLUECHIPS = [
        'UNI/USDT', 'AAVE/USDT', 'MKR/USDT', 
        'LDO/USDT', 'CRV/USDT'
    ]

    @staticmethod
    def get_basket(name: str) -> list[str]:
        """
        Returns the list of symbols for a given basket name.
        """
        if not name:
            return []
            
        # Try to get attribute directly
        basket = getattr(AssetManager, name.upper(), None)
        
        if basket is None:
            # Fallback: maybe it's a comma-separated string provided by generic config
            if ',' in name:
                return [s.strip() for s in name.split(',')]
            # Fallback: maybe it's a single symbol
            return [name]
            
        return basket
