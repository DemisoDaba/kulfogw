from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from sklearn.metrics import mean_absolute_error, mean_squared_error


BASE_DIR = Path(__file__).parent


# ==================================================
# INPUT FILES
# ==================================================

RASTER_FILE = (
    BASE_DIR
    / "data"
    / "Kulfo_GW_Anomaly_UNet_30m_PROTOTYPE.tif"
)

GROUNDWATER_FILE = (
    BASE_DIR
    / "data"
    / "kulfo_clipped_bh_spring_25.gpkg"
)

GROUNDWATER_LAYER = "kulfo_clipped_bh_spring_25"


# ==================================================
# OUTPUT DIRECTORY
# ==================================================

OUTPUT_DIR = (
    BASE_DIR
    / "figures"
    / "spatial_validation"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# SPATIAL VALIDATION
# ==================================================

def spatial_validation():
    """
    Validate U-Net groundwater anomaly raster
    against observed borehole groundwater anomalies.

    Primary metric:
        MAE

    Supporting metrics:
        RMSE
        Bias
        Maximum absolute error
        Percentage within ±1, ±2 and ±5 anomaly units
    """

    print("\n==============================================")
    print("KULFO U-NET SPATIAL VALIDATION")
    print("==============================================\n")

    print("U-Net raster:")
    print(RASTER_FILE)

    print("\nGroundwater data:")
    print(GROUNDWATER_FILE)


    # --------------------------------------------------
    # 1. Load groundwater data
    # --------------------------------------------------

    print("\nLoading boreholes...")

    groundwater = gpd.read_file(
        GROUNDWATER_FILE,
        layer=GROUNDWATER_LAYER,
    )

    # Keep only records with observed groundwater anomaly
    boreholes = groundwater[
        groundwater["GW_Anomaly"].notna()
    ].copy()

    print(
        f"Validation boreholes: {len(boreholes)}"
    )


    # --------------------------------------------------
    # 2. Open U-Net raster
    # --------------------------------------------------

    with rasterio.open(RASTER_FILE) as src:

        raster_crs = src.crs
        raster_nodata = src.nodata

        print(
            "\nRaster CRS:",
            raster_crs
        )

        print(
            "Raster NoData:",
            raster_nodata
        )

        # Reproject boreholes to raster CRS
        boreholes = boreholes.to_crs(
            raster_crs
        )


        # --------------------------------------------------
        # 3. Extract U-Net predictions
        # --------------------------------------------------

        print(
            "\nExtracting U-Net predictions..."
        )

        predictions = []

        for geom in boreholes.geometry:

            value = list(
                src.sample(
                    [(geom.x, geom.y)]
                )
            )[0][0]

            # Raster NoData
            if (
                raster_nodata is not None
                and value == raster_nodata
            ):
                value = np.nan

            # Common NoData value
            if value == -9999:
                value = np.nan

            predictions.append(
                float(value)
            )


    # Add predictions to borehole table
    boreholes["UNet_Anomaly"] = predictions


    # --------------------------------------------------
    # 4. Validation status
    # --------------------------------------------------

    boreholes["Validation_Status"] = np.where(
        boreholes["UNet_Anomaly"].notna(),
        "Valid",
        "U-Net NoData",
    )


    # Valid comparisons
    valid = boreholes[
        boreholes["GW_Anomaly"].notna()
        &
        boreholes["UNet_Anomaly"].notna()
    ].copy()


    # Invalid comparisons
    invalid = boreholes[
        boreholes["UNet_Anomaly"].isna()
    ].copy()


    print(
        f"\nValid comparisons: {len(valid)}"
    )

    print(
        f"U-Net NoData points: {len(invalid)}"
    )


    # --------------------------------------------------
    # 5. Report excluded boreholes
    # --------------------------------------------------

    if len(invalid) > 0:

        print(
            "\nBoreholes excluded from validation:"
        )

        columns_to_show = [
            column
            for column in [
                "BH_ID",
                "ID",
                "GW_Anomaly",
            ]
            if column in invalid.columns
        ]

        print(
            invalid[
                columns_to_show
            ].to_string(index=False)
        )


    # --------------------------------------------------
    # 6. Check that validation is possible
    # --------------------------------------------------

    if len(valid) == 0:

        raise ValueError(
            "No valid borehole comparisons available. "
            "Check borehole locations, GW_Anomaly values, "
            "and the U-Net raster."
        )


    # --------------------------------------------------
    # 7. Calculate residuals and errors
    # --------------------------------------------------

    # Residual:
    # observed - predicted
    #
    # Positive residual:
    # U-Net underpredicts
    #
    # Negative residual:
    # U-Net overpredicts

    valid["Residual"] = (
        valid["GW_Anomaly"]
        -
        valid["UNet_Anomaly"]
    )


    valid["Absolute_Error"] = (
        valid["Residual"].abs()
    )


    # --------------------------------------------------
    # 8. Calculate validation metrics
    # --------------------------------------------------

    print(
        "\nCalculating validation metrics..."
    )

    y_true = valid[
        "GW_Anomaly"
    ].values

    y_pred = valid[
        "UNet_Anomaly"
    ].values


    # Mean Absolute Error
    mae = mean_absolute_error(
        y_true,
        y_pred,
    )


    # Root Mean Square Error
    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred,
        )
    )


    # Mean Bias Error
    #
    # Positive = overprediction
    # Negative = underprediction
    bias = np.mean(
        y_pred - y_true
    )


    # Maximum absolute error
    max_error = (
        valid["Absolute_Error"].max()
    )


    # Standard deviation of residuals
    residual_std = (
        valid["Residual"].std(
            ddof=1
        )
    )


    # --------------------------------------------------
    # 9. Percentage within error thresholds
    # --------------------------------------------------

    within_1 = (
        valid["Absolute_Error"] <= 1
    ).mean() * 100


    within_2 = (
        valid["Absolute_Error"] <= 2
    ).mean() * 100


    within_5 = (
        valid["Absolute_Error"] <= 5
    ).mean() * 100


    # --------------------------------------------------
    # 10. Create final metrics table
    # --------------------------------------------------

    metrics = pd.DataFrame(
        {
            "Metric": [
                "Number of boreholes",
                "Valid comparisons",
                "U-Net NoData points",
                "MAE",
                "RMSE",
                "Bias",
                "Maximum absolute error",
                "Residual standard deviation",
                "Within ±1 anomaly unit (%)",
                "Within ±2 anomaly units (%)",
                "Within ±5 anomaly units (%)",
            ],

            "Value": [
                len(boreholes),
                len(valid),
                len(invalid),
                mae,
                rmse,
                bias,
                max_error,
                residual_std,
                within_1,
                within_2,
                within_5,
            ],
        }
    )


    # --------------------------------------------------
    # 11. Print results
    # --------------------------------------------------

    print(
        "\n----------------------------------------------"
    )

    print(
        "SPATIAL VALIDATION RESULTS"
    )

    print(
        "----------------------------------------------"
    )

    print(
        metrics.to_string(
            index=False
        )
    )


    # --------------------------------------------------
    # 12. Save complete borehole validation table
    # --------------------------------------------------

    print(
        "\nSaving validation results..."
    )

    validation_file = (
        OUTPUT_DIR
        / "borehole_spatial_validation.csv"
    )


    # Save in geographic coordinates
    boreholes_4326 = boreholes.to_crs(
        "EPSG:4326"
    )


    boreholes_4326.to_csv(
        validation_file,
        index=False,
    )


    print(
        "Saved:",
        validation_file
    )


    # --------------------------------------------------
    # 13. Save validation metrics
    # --------------------------------------------------

    metrics_file = (
        OUTPUT_DIR
        / "spatial_validation_metrics.csv"
    )


    metrics.to_csv(
        metrics_file,
        index=False,
    )


    print(
        "Saved:",
        metrics_file
    )


    # --------------------------------------------------
    # 14. Final summary
    # --------------------------------------------------

    print(
        "\n=============================================="
    )

    print(
        "SPATIAL VALIDATION COMPLETE"
    )

    print(
        "=============================================="
    )

    print(
        f"\nPrimary metric — MAE: {mae:.3f}"
    )

    print(
        f"RMSE: {rmse:.3f}"
    )

    print(
        f"Bias: {bias:.3f}"
    )

    print(
        f"Valid boreholes: {len(valid)} / "
        f"{len(boreholes)}"
    )

    print(
        f"Within ±5 anomaly units: "
        f"{within_5:.1f}%"
    )


    # --------------------------------------------------
    # 15. Return results
    # --------------------------------------------------

    return boreholes, metrics


# ==================================================
# SHORT ALIAS
# ==================================================

validate = spatial_validation