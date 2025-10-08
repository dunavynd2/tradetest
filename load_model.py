import joblib

def load_model():
    return joblib.load('model/xgb_amzn_model.pkl')
