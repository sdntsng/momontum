import logging

from river import compose, linear_model, metrics, optim, preprocessing

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    The Brain of Momontum.
    Uses Online ML to process market data features and predict future price movement.
    """

    def __init__(self):
        # 1. Price Smoother (Kalman Filter would be here, but using simple EMA for now or River's stats)
        # using river.stats.Mean or similar for simple smoothing if needed.

        # 2. Prediction Model: Predict next log-return based on features
        # Pipeline: Scaler -> Linear Regression
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            linear_model.LinearRegression(optimizer=optim.SGD(lr=0.01)),
        )

        self.prev_record = None
        self.prev_features = None
        self.prev_mid_price = None

        # Metrics
        self.mae = metrics.MAE()

    def calculate_features(self, record):
        """Extracts features from the raw record."""
        bid = record["bid"]
        ask = record["ask"]
        bid_vol = record["bidVolume"]
        ask_vol = record["askVolume"]

        mid_price = (bid + ask) / 2
        spread = record["spread"]

        # Feature 1: Order Book Imbalance
        # (BidQty - AskQty) / (BidQty + AskQty)
        # Range: [-1, 1]. Positive means buy pressure?
        volume_total = bid_vol + ask_vol
        imbalance = (bid_vol - ask_vol) / volume_total if volume_total > 0 else 0

        return {
            "spread": spread,
            "imbalance": imbalance,
        }, mid_price

    def process(self, record):
        """
        Main loop step:
        1. Calculate current features (X_t)
        2. Learn using (X_{t-1}, Y_t)  where Y_t is current price change?
        3. Predict Y_{t+1} using X_t
        """
        features, mid_price = self.calculate_features(record)

        prediction = None

        # If we have history, we can learn and predict
        if self.prev_features is not None and self.prev_mid_price is not None:
            # Target: Log Return (multiplier) or simple Difference?
            # Simple Difference for simplicity: price_t - price_{t-1}
            price_change_actual = mid_price - self.prev_mid_price

            # LEARN: Update model with (X_{t-1}, true_Y)
            # We predicted change for this moment using previous features
            self.model.learn_one(self.prev_features, price_change_actual)

            # Monitor performance
            # We would need to store the prediction made at T-1 to update MAE
            # But here we just update model.

            # PREDICT: Predict NEXT price change using CURRENT features
            predicted_change = self.model.predict_one(features)
            predicted_price = mid_price + predicted_change

            prediction = {
                "predicted_price": predicted_price,
                "predicted_change": predicted_change,
                "features": features,
            }

            # logger.info(f"Price: {mid_price:.2f} | Pred: {predicted_price:.2f} | Imbalance: {features['imbalance']:.2f}")

        # Store for next tick
        self.prev_features = features
        self.prev_mid_price = mid_price

        return prediction
