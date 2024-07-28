from scipy import stats
from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer
import numpy as np


# Anomaly
def get_anomalies_zscore(series, thresh=3):
    z_scores = np.abs(stats.zscore(series))
    return series[z_scores > thresh]

def get_anomalies_modified_zscore(series, thresh=1):
    pass

def get_anomalies_dbscan(series, thresh):
    pass

def get_anomalies_isolation_forest(series, thresh):
    pass

def get_anomalies_lof(series, thresh):
    pass

# Normalizing
# normalize(series, Normalizer(norm="l2"))
def normalize_sklearn(series, scaler):
    normalized_data = scaler.fit_transform([[x] for x in series]).flatten()
    return normalized_data

# 