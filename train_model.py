import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import joblib

# Load data
df = pd.read_csv('data/amzn_5min.csv', parse_dates=['timestamp'], index_col='timestamp')

# Feature engineering
df['return'] = df['close'].pct_change().shift(-1)
df['target'] = (df['return'] > 0).astype(int)
df['sma_10'] = df['close'].rolling(window=10).mean()
df['sma_30'] = df['close'].rolling(window=30).mean()
df['volatility'] = df['close'].rolling(window=10).std()
df['rsi'] = df['close'].rolling(window=14).apply(lambda x: 100 - (100 / (1 + (x.diff().clip(lower=0).sum() / x.diff().clip(upper=0).abs().sum()))))
df['macd'] = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()

df.dropna(inplace=True)

features = ['open', 'high', 'low', 'close', 'volume', 'sma_10', 'sma_30', 'volatility', 'rsi', 'macd']
X = df[features]
y = df['target']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

# Grid search
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5],
    'learning_rate': [0.05, 0.1],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
grid = GridSearchCV(model, param_grid, cv=3, verbose=1)
grid.fit(X_train, y_train)

# Save model
joblib.dump(grid.best_estimator_, 'model/xgb_amzn_model.pkl')

# Evaluate
preds = grid.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))
