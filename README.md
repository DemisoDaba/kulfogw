````markdown
# Kulfo Spatial Groundwater Analysis Package

An open-source geospatial and AI framework for groundwater analysis in the **Kulfo Watershed, southern Ethiopia**.

## Current Status

The **spatial groundwater analysis component is implemented**.

The current package provides AI-based spatial groundwater anomaly modelling, spatial querying, groundwater zonation, hotspot analysis, borehole-based validation, and uncertainty assessment.

## Spatial Groundwater Analysis

The implemented spatial component includes:

- **U-Net groundwater anomaly modelling**
- **High-resolution groundwater anomaly prediction**
- **Location-specific groundwater anomaly querying**
- **Groundwater anomaly zonation**
- **Groundwater hotspot identification**
- **Borehole-based spatial validation**
- **Prediction uncertainty assessment**

### Spatial Validation

The U-Net groundwater anomaly predictions are evaluated against available borehole observations using:

- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- Bias
- Maximum absolute error
- Residual standard deviation
- Prediction error thresholds

### Uncertainty Assessment

Prediction uncertainty is assessed empirically from the borehole validation residuals using:

- Mean residual
- Residual standard deviation
- MAE
- RMSE
- 95% prediction-error interval
- 95th-percentile absolute error
- Confidence interval for mean residual
- Prediction-error coverage

## Current Spatial Results

The current implementation was evaluated using **25 boreholes**, with **24 valid comparisons** against the U-Net groundwater anomaly raster.

| Metric | Result |
|---|---:|
| Boreholes evaluated | 25 |
| Valid comparisons | 24 |
| MAE | 3.250 |
| RMSE | 4.049 |
| Bias | -0.061 |
| Residual SD | 4.136 |
| Within ±5 anomaly units | 75.0% |
| 95% uncertainty interval | -8.045 to +8.167 |
| 95th percentile absolute error | 7.250 |

## Spatial Workflow

```text
Groundwater & Environmental Data
              |
              v
       U-Net Spatial Model
              |
              v
High-Resolution Groundwater
    Anomaly Prediction
              |
       +------+------+------+
       |      |      |      |
       v      v      v      v
     Query   Zones Hotspots Validation
                              |
                              v
                    Uncertainty Assessment
````

## Package Structure

```text
kulfo/
├── __init__.py
├── spatial.py
├── map.py
├── zones.py
├── zones_interpret.py
├── hotspots.py
├── spatial_validation.py
├── uncertainty.py
└── data/
```

## Validation Outputs

The spatial validation and uncertainty workflows generate:

```text
kulfo/figures/spatial_validation/
├── borehole_spatial_validation.csv
├── spatial_validation_metrics.csv
└── uncertainty_metrics.csv
```

## Main Functions

```python
import kulfo

kulfo.spatial_gw_value
kulfo.spatial_validation
kulfo.uncertainty_assessment
```

## Coming Soon

### Temporal Groundwater Analysis

The **temporal component is coming soon**.

The next stage will extend the current spatial framework toward temporal groundwater monitoring and prediction using time-series data and AI-based temporal modelling.

Planned capabilities include:

* Groundwater time-series analysis
* Location-specific temporal trends
* Groundwater fluctuation prediction
* Temporal depletion and recharge detection
* Integration of spatial and temporal groundwater information

> **Temporal groundwater modelling: Coming Soon**

```
```
Coming Soon
Temporal Groundwater Analysis

The temporal component is coming soon.

The next stage will extend the current spatial framework toward temporal groundwater monitoring and prediction using time-series data and AI-based temporal modelling.

Planned capabilities include:

Groundwater time-series analysis
Location-specific temporal trends
Groundwater fluctuation prediction
Temporal depletion and recharge detection
Integration of spatial and temporal groundwater information
```
Temporal groundwater modelling: Coming Soon
```