# YieldSense AI-Based Crop Yield Prediction

A Streamlit-based crop yield prediction system using a pretrained Random Forest model, categorical encoders, and SHAP-based explainability.

## 1. Repository purpose

This repository provides an inference-ready application for crop yield prediction with:

- Geographic context (state + district)
- Crop and season context
- Land area and rainfall inputs
- Explainability using SHAP (local) + feature importance (global)

The app predicts yield in **quintals per hectare (q/ha)**.

## 2. Current implementation scope

What is included:

- Full Streamlit UI and inference logic (`app.py`)
- Trained model artifact and label encoders (`*.pkl`) in local workspace
- Dataset used by app for state-district filtering (`crop_production.csv`)
- SHAP integration test script (`test_shap_integration.py`)

What is not included:

- A model training script/notebook in this repository
- A committed model artifact in Git history (`*.pkl` is ignored by `.gitignore`)

## 3. Verified model/artifact metadata

Extracted from local model artifacts:

- **Model**: `RandomForestRegressor` (`sklearn.ensemble._forest`)
- **n_estimators**: `100`
- **criterion**: `squared_error`
- **max_depth**: `None`
- **random_state**: `42`
- **bootstrap**: `True`
- **Input features**: `7`

### 3.1 Encoder coverage

| Encoder | Classes |
|---|---:|
| State | 33 |
| District | 646 |
| Crop | 124 |
| Season | 6 |

Season values:

- `Autumn`
- `Kharif`
- `Rabi`
- `Summer`
- `Whole Year`
- `Winter`

### 3.2 Artifact sizes (local)

| File | Size |
|---|---:|
| `yieldsense_model.pkl` | 1,647,378,801 bytes |
| `yieldsense_le_state.pkl` | 1,089 bytes |
| `yieldsense_le_district.pkl` | 11,633 bytes |
| `yieldsense_le_crop.pkl` | 2,539 bytes |
| `yieldsense_le_season.pkl` | 598 bytes |

## 4. Data and schema details

### 4.1 `crop_production.csv` (repository dataset)

Current file shape:

- Rows: `246,091`
- Columns: `8`

Columns:

| Column | Type (observed) | Description | Missing |
|---|---|---|---:|
| `State_Name` | string | State/UT name | 0 |
| `District_Name` | string | District name | 0 |
| `Crop_Year` | int | Crop year | 0 |
| `Season` | string | Farming season | 0 |
| `Crop` | string | Crop name | 0 |
| `Area` | float | Cultivated area (hectares) | 0 |
| `Rainfall` | float | Annual rainfall (mm) | 0 |
| `Production` | float | Production quantity | 3,730 |

Additional observed dataset facts:

- `Crop_Year` range: `1997` to `2015`
- Unique states: `33`
- Unique districts: `646`
- Unique crops: `124`
- Unique seasons: `6`

### 4.2 Model input schema (runtime inference)

The app builds exactly this feature vector (in order):

1. `State_Name` (encoded integer)
2. `District_Name` (encoded integer)
3. `Crop_Year` (numeric)
4. `Season` (encoded integer)
5. `Crop` (encoded integer)
6. `Area` (float, hectares)
7. `Rainfall` (float, mm)

Important:

- `Rainfall` is part of the dataset schema in `crop_production.csv` and part of model inputs.
- In the current app flow, rainfall remains editable from UI for scenario testing before prediction.

## 5. Feature engineering and inference pipeline (implemented in `app.py`)

This is the exact runtime pipeline:

1. **Load artifacts**
   - Load model + 4 encoders using `joblib`.
   - Load `crop_production.csv`.
2. **Normalize geographic text**
   - `State_Name` and `District_Name` from CSV are normalized to lowercase and stripped.
3. **State-to-district filtering**
   - Selected state filters district options from CSV.
   - District list is additionally filtered to values that exist in district encoder classes.
4. **User input capture**
   - State, district, crop, season, area, rainfall, crop year.
5. **Input validation**
   - `area > 0`
   - `rainfall > 0`
   - selected values must exist in encoder vocabularies.
6. **Categorical encoding**
   - `state` encoded from lowercase form.
   - `district` encoded from uppercase form.
   - `crop` and `season` encoded from title-case form.
7. **Feature vector assembly**
   - Build one-row DataFrame with the 7 model features in expected order.
8. **Prediction**
   - `model.predict(input_data)[0]` => predicted yield (`q/ha`).
9. **Uncertainty proxy**
   - Per-tree predictions are collected from `model.estimators_`.
   - Standard deviation of tree predictions is shown as model uncertainty.
   - Confidence score displayed as `max(0, 100 - std * 10)`.

## 6. Explainability pipeline (SHAP + model importance)

### 6.1 SHAP local explanation

SHAP (SHapley Additive exPlanations) explains one prediction by distributing the final output into feature-wise contributions.

Think of the prediction as:

```text
final_prediction = base_value + contribution_from_state + contribution_from_district + ... + contribution_from_rainfall
```

Implemented with `shap.TreeExplainer(model)` in this app:

1. Compute `shap_values` for the single inference row.
2. Handle SHAP return shape safely (`list` or `ndarray`).
3. Build contribution table with:
   - Feature
   - Input value
   - Absolute SHAP impact
   - Direction (`increases`/`decreases`)
4. Display base value (`explainer.expected_value`) and cumulative contribution breakdown.

How to interpret each SHAP value:

- **Positive SHAP**: feature pushed predicted yield upward.
- **Negative SHAP**: feature pushed predicted yield downward.
- **Larger absolute SHAP**: stronger influence on this specific prediction.
- **Near zero SHAP**: little local influence for this row.

Why this is powerful:

- It is **local** and context-aware.  
  Example: rainfall can increase prediction for one crop-season-state combination but have weaker or opposite effect for another.
- It provides auditability for each forecast instead of only a single black-box number.
- It allows agronomic discussion around *which factors mattered most* for that exact scenario.

### 6.2 SHAP visual output in app

The app provides four explainability tabs:

1. **Feature Contribution**: ranked SHAP impact table
2. **Prediction Breakdown**: base value vs final prediction + stepwise cumulative effects
3. **Feature Impact**: horizontal bar chart of absolute SHAP values
4. **Global Importance**: model-wide feature importances from `model.feature_importances_`

Important distinction:

- Tabs 1-3 are **local explanation** (for the current user input only).
- Tab 4 is **global model behavior** (average split importance across many trees).

### 6.3 Verified global feature importances

From the trained model artifact:

| Feature | Importance |
|---|---:|
| `Crop` | 0.643836 |
| `Season` | 0.103516 |
| `State_Name` | 0.103257 |
| `Area` | 0.055292 |
| `Rainfall` | 0.044816 |
| `Crop_Year` | 0.025055 |
| `District_Name` | 0.024230 |

## 7. Application workflow diagram

```text
User Inputs
(State, District, Crop, Season, Area, Rainfall, Year)
        |
        v
Input validation + normalization
        |
        v
Label encoding (state/district/crop/season)
        |
        v
Assemble model feature row (7 columns)
        |
        v
RandomForestRegressor prediction (q/ha)
        |
        +--> Uncertainty estimate from per-tree std
        |
        +--> SHAP TreeExplainer local interpretation
```

## 8. File-by-file technical map

| File | Role |
|---|---|
| `app.py` | Streamlit UI, prediction flow, validation, SHAP, charts |
| `crop_production.csv` | Dataset used by app for state-district filtering and metadata context |
| `requirements.txt` | Python dependencies |
| `test_shap_integration.py` | Script to validate SHAP integration end-to-end |
| `check_data.py` | Prints encoder-supported states/district samples |
| `generate_crop_data.py` | Generates state-district CSV based on encoder classes and mapping |
| `shap_test_visualization.png` | SHAP test chart artifact |

## 9. Setup and run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

App URL (default): `http://localhost:8501`

## 10. Utility scripts

Run SHAP integration test:

```powershell
python test_shap_integration.py
```

Inspect encoder coverage:

```powershell
python check_data.py
```

Regenerate state-district mapping CSV:

```powershell
python generate_crop_data.py
```

## 11. Known constraints and implementation notes

1. Model artifacts are large and ignored by Git (`*.pkl` in `.gitignore`), so clone-only environments need local artifact provisioning.
2. The app supports prediction years `1997` to `2030` in UI, while observed CSV years are `1997` to `2015`.
3. Training code is not present; runtime behavior is fully documented here from the deployed artifacts and app logic.
4. `theme_mode` option in sidebar is currently a UI setting placeholder and does not switch a separate CSS theme pipeline in code.

## 12. Reproducible environment

Dependencies (`requirements.txt`):

- `streamlit>=1.28.0`
- `joblib>=1.3.0`
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `scikit-learn>=1.3.0`
- `shap>=0.42.0`
- `matplotlib>=3.7.0`

## 13. A-to-Z column reference

### 13.1 Training-style source columns (`crop_production.csv`)

| Column | Unit | Unique Values | Notes |
|---|---|---:|---|
| `State_Name` | text | 33 | State/UT, normalized to lowercase in app |
| `District_Name` | text | 646 | District, normalized to lowercase in app |
| `Crop_Year` | year | 19 | Observed range 1997-2015 |
| `Season` | text | 6 | `Autumn`, `Kharif`, `Rabi`, `Summer`, `Whole Year`, `Winter` |
| `Crop` | text | 124 | Crop category/value used for encoding |
| `Area` | hectares | 38,442 | Observed min 0.04, max 8,580,100 |
| `Rainfall` | mm | - | Rainfall feature column used in prediction pipeline |
| `Production` | production quantity | 51,627 | 3,730 missing values |

### 13.2 Inference columns (model input row)

| Feature | Type passed to model | Source |
|---|---|---|
| `State_Name` | int (label-encoded) | UI state selection |
| `District_Name` | int (label-encoded) | UI district selection |
| `Crop_Year` | numeric | UI year input |
| `Season` | int (label-encoded) | UI season selection |
| `Crop` | int (label-encoded) | UI crop selection |
| `Area` | float | UI area input |
| `Rainfall` | float | `crop_production.csv` column (editable in UI at inference time) |

## 14. End-to-end execution lifecycle

1. App bootstraps Streamlit page and CSS theme.
2. Model and encoders are loaded once using `@st.cache_resource`.
3. CSV is loaded once using `@st.cache_data`.
4. User selects state; district list is filtered from CSV for that state.
5. User fills crop, season, area, rainfall, and year.
6. App validates values and vocabulary membership.
7. Categorical fields are encoded with persisted label encoders.
8. One-row DataFrame is created with model feature order.
9. Model predicts yield.
10. Tree-level prediction spread is used as an uncertainty proxy.
11. SHAP values are generated and rendered in multiple explanation views.

## 15. Input constraints and defaults (from code)

| Input | Widget | Default | Constraint |
|---|---|---:|---|
| State | `selectbox` | First sorted state | Must exist in state encoder classes |
| District | `selectbox` | First filtered district | Must belong to selected state and district encoder |
| Crop | `selectbox` | First sorted crop | Must exist in crop encoder classes |
| Season | `selectbox` | First sorted season | Must exist in season encoder classes |
| Area | `number_input` | 1.0 | Must be `> 0` |
| Rainfall | `number_input` | 500.0 | Must be `> 0` |
| Crop Year | `number_input` | Current year | Min 1997, max 2030 |

## 16. Encoding and normalization rules

- State from UI: shown as title case, converted to lowercase for matching and encoding.
- District from UI: shown as title case, converted to lowercase for display logic, transformed to uppercase for encoder lookup.
- Crop and Season: shown as title case and encoded in title case.
- CSV values are normalized to lowercase (`state`, `district`) for filtering logic.

These case conversions are required because saved encoder vocabularies use mixed canonical formats.

## 17. Prediction and uncertainty formulas

Prediction:

```text
yield_q_per_ha = model.predict(X)[0]
```

Uncertainty proxy:

```text
tree_preds = [tree.predict(X)[0] for tree in model.estimators_]
uncertainty = std(tree_preds)
confidence_score = max(0, 100 - uncertainty * 10)
```

Interpretation:

- Lower `uncertainty` means tree models agree more.
- Higher `confidence_score` means tighter ensemble agreement.

## 18. SHAP mathematics used in app

For a single prediction:

```text
prediction = base_value + sum(feature_shap_values)
```

Where:

- `base_value` = model expected output from `TreeExplainer`
- each SHAP value = signed contribution of one feature for this prediction
- absolute SHAP values are used for ranking contribution strength

Interpretation rule of thumb:

1. Start at `base_value`.
2. Add all positive SHAP values (features raising yield).
3. Add all negative SHAP values (features lowering yield).
4. Result equals the final predicted yield.

This additive consistency is why SHAP is easy to explain to non-ML stakeholders.

## 19. Explainability outputs in UI

1. **Feature Contribution tab**  
   Ranked table with feature value, absolute SHAP impact, and impact direction (`increases`/`decreases`).

2. **Prediction Breakdown tab**  
   Displays final prediction, SHAP base value, and cumulative feature contributions from baseline to final output.

3. **Feature Impact tab**  
   Horizontal chart of top absolute SHAP effects for the current row (magnitude-first view).

4. **Global Importance tab**  
   `model.feature_importances_` across all training trees (global, not local SHAP).

Common interpretation mistakes to avoid:

- High global importance does **not** always mean high local SHAP for every row.
- SHAP direction is row-specific; the same feature may push up in one case and down in another.
- Absolute SHAP rank shows strength, while signed SHAP shows direction.

## 20. Data quality and distribution notes

- `Production` has missing values (3,730 rows).
- Derived yield (`Production / Area`) has strong skew/outliers:
  - count: 242,361
  - mean: 41.6491
  - median: 1.0
  - p95: 22.4483
  - min: 0.0
  - max: 88,000.0

This indicates a heavy-tailed target distribution and possible outlier-driven behavior.

## 21. Operational considerations

1. Model artifact is large (~1.65 GB); startup and memory usage depend on host capacity.
2. Cloud deployment with strict memory limits may require model compression or external model serving.
3. Encoder files must always match the model version; mismatches can cause invalid class lookups.
4. Because training code is absent in this repo, retraining reproducibility is currently out of scope.

## 22. Troubleshooting (technical)

### 22.1 Artifact errors

- If any `.pkl` file is missing or renamed, app stops with load error.
- Keep model and all 4 encoders in project root beside `app.py`.

### 22.2 Invalid category errors

- Happens when input value is not present in the corresponding encoder classes.
- Ensure dataset/encoder versions are synchronized.

### 22.3 SHAP issues

- SHAP can fail for incompatible package versions or model serialization edge cases.
- Use versions from `requirements.txt` and verify with `test_shap_integration.py`.

### 22.4 Performance bottlenecks

- First run cost: artifact load + SHAP initialization.
- Subsequent runs benefit from Streamlit cache decorators.

## 23. Suggested production hardening (future work)

1. Add explicit model metadata file (version, trained date, feature spec hash).
2. Add schema validator for all inference inputs before prediction.
3. Add drift/outlier monitoring for rainfall, area, and categorical frequencies.
4. Add quantile prediction intervals (instead of std-based proxy only).
5. Add artifact checksum verification on startup.

