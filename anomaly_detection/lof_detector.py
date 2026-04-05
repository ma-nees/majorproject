"""
Local Outlier Factor based anomaly detection
Detects transactions that are different from nearby data points
"""

import numpy as np
from sklearn.neighbors import LocalOutlierFactor


class LOFDetector:

    def __init__(self, neighbors=20):

        self.model = LocalOutlierFactor(
            n_neighbors=neighbors,
            contamination=0.02,
            novelty=True
        )

    def train(self, data):
        """
        Train LOF model
        """

        self.model.fit(data)

    def predict(self, transaction_features):
        """
        Predict anomaly
        """

        prediction = self.model.predict([transaction_features])[0]

        if prediction == -1:
            return "ANOMALY"

        return "NORMAL"

    def anomaly_score(self, transaction_features):
        """
        Return anomaly score
        """

        score = self.model.decision_function([transaction_features])[0]

        return float(score)


# Example usage
if __name__ == "__main__":

    X = np.array([
        [50],
        [60],
        [55],
        [52],
        [58],
        [70000]  # suspicious
    ])

    detector = LOFDetector()

    detector.train(X)

    result = detector.predict([70000])

    print("LOF Prediction:", result)