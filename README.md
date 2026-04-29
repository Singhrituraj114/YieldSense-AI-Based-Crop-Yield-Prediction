# YieldSense AI Based Crop Yield Prediction with Weather Integration

YieldSense AI is a Streamlit application that predicts crop yield (quintals/hectare) using a trained **RandomForestRegressor** and explains each prediction with **SHAP**.

It combines geography (state/district), crop context (crop/season/year), farm size (area), and weather signal (rainfall) into one prediction pipeline and presents both local (per-prediction) and global (model-level) feature impact.

## 1. Project introduction

The goal is to support data-driven agricultural decisions by estimating expected yield before harvest.  
The app is designed for interactive use: choose region + crop + season + environmental values, then immediately see:

1. Predicted yield
2. Confidence/uncertainty estimate
3. SHAP-based feature contributions

## 2. Repository structure and role of each file

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app (UI + prediction + SHAP explainability) |
| `crop_production.csv` | Source agricultural records used for state-district filtering and reference data |
| `*.pkl` model artifacts | Required locally for runtime predictions (not tracked in GitHub) |
| `requirements.txt` | Python dependencies |

## 3. Data depth: all columns and how they work

### 3.1 `crop_production.csv` schema

The raw CSV contains **246,091 rows** and these columns:

| Column | Type | Meaning | Used in app |
|---|---|---|---|
| `State_Name` | Categorical (string) | State/UT name | Yes (filter + model input via encoder) |
| `District_Name` | Categorical (string) | District name | Yes (filter + model input via encoder) |
| `Crop_Year` | Numeric (int) | Year of crop record | Yes (model input) |
| `Season` | Categorical (string) | Growing season | Yes (model input via encoder) |
| `Crop` | Categorical (string) | Crop type | Yes (model input via encoder) |
| `Area` | Numeric (float) | Cultivated area in hectares | Yes (model input) |
| `Production` | Numeric (float) | Total production in raw data | Not direct input in UI model prediction |

### 3.2 Cardinality/ranges (from current dataset)

- States: **33**
- Districts: **646**
- Crops: **124**
- Seasons: **6**
- Year range in CSV: **1997 to 2015**
- Area range: **0.04 to 8,580,100.0**
- Production range: **0.0 to 1,250,800,000.0**

### 3.3 Model input columns (final features used for prediction)

The model expects exactly these **7 features** in this order:

1. `State_Name` (encoded)
2. `District_Name` (encoded)
3. `Crop_Year`
4. `Season` (encoded)
5. `Crop` (encoded)
6. `Area`
7. `Rainfall`

> Note: `Rainfall` is user-provided in the app and is part of the trained model feature set.  
> `Production` exists in the source CSV but is not passed as a model input feature in `app.py`.

## 4. End-to-end prediction flow (depth)

### 4.1 Model and encoders loading

`app.py` uses Streamlit caching:

- `@st.cache_resource` for model/encoders and SHAP explainer
- `@st.cache_data` for CSV data

Loaded artifacts:

- `yieldsense_model.pkl`
- 4 label encoders (`state`, `district`, `crop`, `season`)
- These artifacts are kept local and not committed to GitHub.

### 4.2 Geography filtering logic

District options are **state-dependent**:

1. User chooses a state.
2. App filters `crop_production.csv` rows for that state.
3. Extracted districts are cross-checked against encoder classes.
4. Only valid districts are shown in the district dropdown.

This prevents invalid state-district pairs from being sent to the model.

### 4.3 Input normalization + encoding

Before prediction:

- State: lowercased for matching `le_state.classes_`
- District: transformed to uppercase for matching `le_district.classes_`
- Crop/Season: title-cased for matching corresponding encoders
- Area and Rainfall: required to be `> 0`

Then categorical fields are converted to numeric IDs by label encoders.

### 4.4 Prediction execution

The app builds a one-row DataFrame:

```text
['State_Name', 'District_Name', 'Crop_Year', 'Season', 'Crop', 'Area', 'Rainfall']
```

and calls:

```python
prediction = model.predict(input_data)[0]
```

Output unit displayed: **q/ha (quintals per hectare)**.

### 4.5 Confidence / uncertainty shown in UI

For the Random Forest:

1. Prediction from each decision tree is collected.
2. Standard deviation of tree outputs is treated as uncertainty.
3. Confidence score is derived as:

```python
confidence_score = max(0, 100 - (std_dev * 10))
```

This gives a user-friendly confidence percentage plus raw uncertainty value.

## 5. SHAP explainability: full breakdown

YieldSense uses `shap.TreeExplainer(model)` for tree-based explainability.

For a single prediction:

1. Compute SHAP values for each feature.
2. Compare feature contributions against the base value (`expected_value`).
3. Present impact direction and magnitude.

The app exposes SHAP in four tabs:

1. **Feature Contribution**  
   Data table of feature value, absolute SHAP impact, and direction (increase/decrease).

2. **Prediction Breakdown**  
   Shows base value vs final prediction and cumulative contribution steps.

3. **Feature Impact**  
   Horizontal bar chart of absolute SHAP magnitudes for this single prediction.

4. **Global Importance**  
   Uses `model.feature_importances_` to show model-wide importance across training.

### Local vs Global (important difference)

- **SHAP (local):** explains *this specific prediction*.
- **Feature importance (global):** explains what the model generally relies on across many predictions.

## 6. Model details

- Model class: **`RandomForestRegressor`**
- Number of trees: **100**
- Feature count: **7**
- Explainability method: **SHAP TreeExplainer**

## 7. Run locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Default app URL:

```text
http://localhost:8501
```

## 8. Local runtime artifacts required

To run predictions, place these files next to `app.py` on your machine:

1. `yieldsense_model.pkl`
2. `yieldsense_le_state.pkl`
3. `yieldsense_le_district.pkl`
4. `yieldsense_le_crop.pkl`
5. `yieldsense_le_season.pkl`

## 9. Practical notes and constraints

- The model file is large (`~1.65 GB`), so initial load can take time.
- Prediction is scoped to the encoded classes available in shipped encoder files.
- UI year input currently allows **1997–2030**, while source CSV historical years go up to 2015.

## 10. Tech stack

- Python
- Streamlit
- scikit-learn
- SHAP
- pandas / numpy
- matplotlib
