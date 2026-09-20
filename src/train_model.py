import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_squared_error

from xgboost import XGBRegressor

# ==========================
# LOAD DATA
# ==========================
df = pd.read_csv("data/Train.csv")

# ==========================
# CLEAN & FEATURE ENGINEERING
# ==========================
# 1. Clean Fat Content
df['Item_Fat_Content'] = df['Item_Fat_Content'].replace({
    'LF': 'Low Fat',
    'low fat': 'Low Fat',
    'reg': 'Regular'
})

# 2. Impute Zero Visibilities with Item Type mean
mean_visibility = df[df['Item_Visibility'] > 0].groupby('Item_Type')['Item_Visibility'].mean()
df['Item_Visibility'] = df.apply(
    lambda row: mean_visibility[row['Item_Type']] if row['Item_Visibility'] == 0 else row['Item_Visibility'], 
    axis=1
)

# 3. Extract Parent Categories
df['Item_Category'] = df['Item_Identifier'].apply(lambda x: x[:2]).map({
    'FD': 'Food',
    'DR': 'Drinks',
    'NC': 'Non-Consumable'
})

# 4. Calculate operational years (historically standard 2013 base year)
df['Outlet_Age'] = 2013 - df['Outlet_Establishment_Year']

# 5. Categorize MRP into bins
df['MRP_Bin'] = pd.cut(df['Item_MRP'], bins=[0, 70, 140, 210, np.inf], labels=['Low', 'Medium', 'High', 'Very High'])

# log transform target (BOOSTS ACCURACY)
df['Item_Outlet_Sales'] = np.log1p(df['Item_Outlet_Sales'])

cat_features = [
    'Item_Fat_Content',
    'Item_Type',
    'Outlet_Identifier',
    'Outlet_Size',
    'Outlet_Location_Type',
    'Outlet_Type',
    'Item_Category',
    'MRP_Bin'
]

num_features = [
    'Item_Weight',
    'Item_Visibility',
    'Item_MRP',
    'Outlet_Age'
]

X = df[num_features + cat_features]
y = df['Item_Outlet_Sales']

# ==========================
# PREPROCESSOR
# ==========================
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median'))
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, num_features),
        ('cat', categorical_transformer, cat_features)
    ]
)

# ==========================
# MODELS TO COMPARE
# ==========================
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(max_depth=8, random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
    "XGBoost": XGBRegressor(
        n_estimators=500,
        learning_rate=0.03,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
}

# ==========================
# TRAIN TEST SPLIT
# ==========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# ==========================
# EVALUATE ALL MODELS
# ==========================
best_model = None
best_r2 = -float('inf')
best_clf = None

print("=== Model Comparison ===")
for name, model in models.items():
    clf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    # Train
    clf.fit(X_train, y_train)
    
    # Predict
    preds = clf.predict(X_test)
    preds_real = np.expm1(preds)
    y_test_real = np.expm1(y_test)
    
    # Metrics
    r2 = r2_score(y_test_real, preds_real)
    rmse = np.sqrt(mean_squared_error(y_test_real, preds_real))
    
    print(f"{name}: R2 = {r2:.4f} | RMSE = {rmse:.2f}")
    
    if r2 > best_r2:
        best_r2 = r2
        best_clf = clf
        best_model_name = name

print(f"\nBest Model: {best_model_name} with R2 = {best_r2:.4f}")

# ==========================
# SAVE THE BEST MODEL
# ==========================
pickle.dump(best_clf, open("models/sales_model.pkl", "wb"))
print(f"Saved {best_model_name} to models/sales_model.pkl")