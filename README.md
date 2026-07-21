# YieldSense AI-Based Crop Yield Prediction with Weather Integration

YieldSense is a Streamlit app that predicts crop yield (**q/ha**) using a trained **RandomForestRegressor**, then explains each prediction with **SHAP**.

This README explains the project in depth: data columns, feature engineering, and complete runtime pipeline.

---

## 1) Project objective

Given location + crop context + farm + weather inputs, the app estimates expected yield and shows why the model predicted that value.

Inputs:

1. State
2. District
3. Crop
4. Season
5. Crop Year
6. Area (hectares)
7. Annual Rainfall (mm)

Outputs:

1. Predicted yield (q/ha)
2. Confidence/uncertainty estimate
3. SHAP-based explanation (local + global views)

---

## 2) Repository structure

| File | Purpose | Runtime critical |
|---|---|---|
| `app.py` | Main Streamlit app: UI, validation, encoding, inference, SHAP | Yes |
| `crop_production.csv` | Source dataset for state-district filtering and reference values | Yes |
| `yieldsense_model.pkl` | Trained `RandomForestRegressor` model artifact | Yes |
| `yieldsense_le_state.pkl` | Label encoder for state | Yes |
| `yieldsense_le_district.pkl` | Label encoder for district | Yes |
| `yieldsense_le_crop.pkl` | Label encoder for crop | Yes |
| `yieldsense_le_season.pkl` | Label encoder for season | Yes |
| `requirements.txt` | Python dependencies | Yes |
| `check_data.py` | Utility to inspect encoder classes | No |
| `generate_crop_data.py` | Utility to generate state-district mapping CSV | No |
| `test_shap_integration.py` | Utility to validate SHAP pipeline end-to-end | No |

---

## 3) Dataset documentation (every column)

Current `crop_production.csv` profile:

- Rows: **246,091**
- Columns: **7**
- Unique states: **33**
- Unique districts: **646**
- Year range: **1997-2015**

### 3.1 Column-level definition

| Column | Type | Meaning | Cardinality / Range | Used in runtime model input |
|---|---|---|---|---|
| `State_Name` | object | State / UT label | 33 unique | Yes (encoded) |
| `District_Name` | object | District label | 646 unique | Yes (encoded) |
| `Crop_Year` | int64 | Year context | 1997-2015 | Yes (numeric) |
| `Season` | object | Growing season | 6 unique | Yes (encoded) |
| `Crop` | object | Crop type | 124 unique | Yes (encoded) |
| `Area` | float64 | Cultivated land (hectares) | 0.04 to 8,580,100.0 | Yes (numeric) |
| `Production` | float64 | Total production in source records | 0 to 1,250,800,000.0 | No |

### 3.2 Nulls

| Column | Missing |
|---|---:|
| `State_Name` | 0 |
| `District_Name` | 0 |
| `Crop_Year` | 0 |
| `Season` | 0 |
| `Crop` | 0 |
| `Area` | 0 |
| `Production` | 3,730 |

### 3.3 Season values

- Autumn
- Kharif
- Rabi
- Summer
- Whole Year
- Winter

---

## 4) Actual model feature schema

From the loaded artifact, model expects exactly **7 features**, in this order:

1. `State_Name`
2. `District_Name`
3. `Crop_Year`
4. `Season`
5. `Crop`
6. `Area`
7. `Rainfall`

Important distinction:

- `Rainfall` is user-entered at prediction time.
- `Production` is in CSV but not used in runtime feature vector.

---

## 5) Feature engineering in this project (inference-time)

This repository includes inference code (`app.py`) and trained artifacts. The full training notebook/script is not included, so the following are the **verified runtime feature engineering steps**:

### 5.1 String normalization and canonical casing

To match saved encoder class formats:

- State: lowercase + strip
- District: lowercase + strip for filtering, uppercase for encoding
- Crop: lowercase + strip in UI, `title()` for encoding
- Season: lowercase + strip in UI, `title()` for encoding

### 5.2 State-district compatibility engineering

District options are dynamically constrained by selected state:

1. Filter CSV by `State_Name`
2. Get unique districts in that state
3. Keep only districts present in district encoder classes

This prevents invalid state/district combinations at inference time.

### 5.3 Categorical encoding

Four label encoders transform categories to integer IDs:

- `le_state` -> `State_Name`
- `le_district` -> `District_Name`
- `le_crop` -> `Crop`
- `le_season` -> `Season`

### 5.4 Numeric feature handling

Numeric runtime features are:

- `Crop_Year`
- `Area`
- `Rainfall`

Validation before prediction:

1. `Area > 0`
2. `Rainfall > 0`

### 5.5 Fixed feature order engineering

Single-row input DataFrame is built with strict order:

```python
['State_Name', 'District_Name', 'Crop_Year', 'Season', 'Crop', 'Area', 'Rainfall']
```

Keeping this order is critical for correct model behavior.

---

## 6) End-to-end runtime pipeline (step-by-step)

### Step A: startup

1. Streamlit page config and UI theme are initialized.
2. Model + encoders load via `@st.cache_resource`.
3. CSV loads via `@st.cache_data`.
4. If required files are missing, app stops.

### Step B: input capture

User selects state, district, crop, season and enters area, rainfall, year.

### Step C: validation

App validates:

1. positive numeric constraints
2. category support in encoder classes
3. district availability for chosen state

### Step D: transformation and feature assembly

1. Categorical values are encoded.
2. One-row feature DataFrame is constructed in model-required order.

### Step E: model inference

Prediction call:

```python
prediction = model.predict(input_data)[0]
```

Returned value is displayed as q/ha.

### Step F: confidence / uncertainty estimation

The app computes tree-level spread:

1. Predict with every tree in `model.estimators_`
2. Standard deviation of these values = uncertainty proxy
3. Confidence heuristic:

```python
confidence_score = max(0, 100 - (std_dev * 10))
```

### Step G: explainability pipeline

1. Build `shap.TreeExplainer(model)` (cached)
2. Compute SHAP values for current row
3. Normalize shape differences (list/array handling)
4. Display 4 sections:
   - Feature Contribution (local SHAP table)
   - Prediction Breakdown (base value + cumulative contributions)
   - Feature Impact (local SHAP bar chart)
   - Global Importance (`model.feature_importances_`)

---

## 7) SHAP outputs and interpretation

### Local explanation (prediction-specific)

Answers: **Why this exact prediction?**

- Per-feature signed SHAP effects
- Absolute impact ranking
- Base value to final value path

### Global explanation (model-level)

Answers: **Which features matter most overall in the trained model?**

- Uses `feature_importances_` from RandomForest
- Not tied to a single row

---

## 8) Model and encoder artifact facts (loaded runtime values)

- Model type: `RandomForestRegressor`
- Number of trees: `100` in the originally trained model
- Input feature count: `7`
- Training set size: `246,091` records (2.4L+)
- Evaluation metric: `R² = 0.94` (held-out test split, measured on the full 100-tree model)
- Encoder class counts:
  - States: `33`
  - Districts: `646`
  - Crops: `124`
  - Seasons: `6`

### Two model files, chosen automatically

`app.py` looks for `yieldsense_model_full.pkl` first (the full 100-tree model) and only falls back to `yieldsense_model.pkl` if that file isn't present:

- **Local development**: keep `yieldsense_model_full.pkl` on disk (gitignored, ~1.65 GB) for full-fidelity predictions. This is what you get by default after cloning and generating/copying in the full model.
- **Hosted deployment** (e.g. Streamlit Community Cloud): only `yieldsense_model.pkl` is committed to this repo — a 20-tree subset of the exact same fitted trees (no retraining), pruned so the artifact fits within GitHub's 100MB direct-push limit and the free tier's ~1GB RAM ceiling (the full model alone uses ~1.7GB in memory once loaded). Across a 50-row sample, predictions from the pruned model differ from the full model by ~7% on average.

Feature importances (aligned to model feature order):

| Feature | Importance |
|---|---:|
| State_Name | 0.1033 |
| District_Name | 0.0242 |
| Crop_Year | 0.0251 |
| Season | 0.1035 |
| Crop | 0.6438 |
| Area | 0.0553 |
| Rainfall | 0.0448 |

In this artifact, `Crop` is the strongest global driver.

---

## 9) Training pipeline scope note

This repository contains:

- Inference pipeline (`app.py`)
- Model and encoder artifacts (`*.pkl`)

It does **not** contain the original full training script (data cleaning, target definition, split strategy, hyperparameter search, etc.), so those training-phase steps cannot be documented from code here with full certainty.

What can be confirmed from artifacts:

1. Model is a Random Forest regressor.
2. Runtime feature schema has 7 features listed above.
3. Encoded categorical domains are fixed by saved encoders.
4. Output is interpreted in app as yield (`q/ha`).

---

## 10) Constraints and caveats

1. **Encoder dependency**: unseen category labels are unsupported unless encoders are retrained.
2. **Year extrapolation**: UI allows year up to 2030 while source CSV ends at 2015; future-year predictions are extrapolative.
3. **Rainfall source**: rainfall is manual input in current app code (no live weather API fetch in `app.py`, despite the "weather-aware" UI copy).
4. **Pruned deployed model**: the repo-tracked `yieldsense_model.pkl` is a 20-tree subset of the original 100-tree model (see section 8); predictions differ from the full model by ~7% on average. The full model is used automatically instead whenever `yieldsense_model_full.pkl` is present locally.
5. **Production column mismatch**: raw CSV includes `Production`, but the runtime model expects `Rainfall` instead.
6. **UI "model performance" card**: the sidebar shows the R² score and training set size from offline evaluation; these are fixed values baked into the UI, not recomputed live at runtime.

---

## 11) Run locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Default URL: `http://localhost:8501`

---

## 12) Utility scripts

### `check_data.py`

Prints available state and district classes from encoders.

```powershell
python check_data.py
```

### `generate_crop_data.py`

Builds a state-district mapping CSV from a mapping dictionary and encoder class checks.

```powershell
python generate_crop_data.py
```

### `test_shap_integration.py`

Runs a complete SHAP sanity test and saves `shap_test_visualization.png`.

```powershell
python test_shap_integration.py
```

---

## 13) Dependencies

From `requirements.txt`:

- streamlit>=1.28.0
- joblib>=1.3.0
- pandas>=2.0.0
- numpy>=1.24.0
- scikit-learn>=1.3.0
- shap>=0.42.0
- matplotlib>=3.7.0

