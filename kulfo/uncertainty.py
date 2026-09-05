from pathlib import Path

import numpy as np
import pandas as pd


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).parent

VALIDATION_FILE = (
    BASE_DIR
    / "figures"
    / "spatial_validation"
    / "borehole_spatial_validation.csv"
)

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
# UNCERTAINTY ASSESSMENT
# ==================================================

def uncertainty_assessment():
    """
    Calculate empirical uncertainty of the U-Net
    groundwater anomaly predictions using the
    borehole validation residuals.

    No maps or plots are produced.
    """

    print("\n==============================================")
    print("KULFO U-NET UNCERTAINTY ASSESSMENT")
    print("==============================================\n")

    print("Validation data:")
    print(VALIDATION_FILE)


    # --------------------------------------------------
    # 1. Load validation results
    # --------------------------------------------------

    print("\nLoading validation data...")

    if not VALIDATION_FILE.exists():

        raise FileNotFoundError(
            f"Validation file not found:\n"
            f"{VALIDATION_FILE}\n\n"
            "Run spatial_validation() first."
        )

    boreholes = pd.read_csv(
        VALIDATION_FILE
    )


    # --------------------------------------------------
    # 2. Check required columns
    # --------------------------------------------------

    required_columns = [
        "GW_Anomaly",
        "UNet_Anomaly",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in boreholes.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


    # --------------------------------------------------
    # 3. Keep valid comparisons
    # --------------------------------------------------

    valid = boreholes[
        boreholes["GW_Anomaly"].notna()
        &
        boreholes["UNet_Anomaly"].notna()
    ].copy()


    print(
        f"Valid borehole comparisons: {len(valid)}"
    )


    if len(valid) < 2:

        raise ValueError(
            "At least two valid borehole comparisons "
            "are required for uncertainty assessment."
        )


    # --------------------------------------------------
    # 4. Calculate residuals
    # --------------------------------------------------

    # Residual = observed - predicted

    valid["Residual"] = (
        valid["GW_Anomaly"]
        -
        valid["UNet_Anomaly"]
    )

    valid["Absolute_Error"] = (
        valid["Residual"].abs()
    )


    # --------------------------------------------------
    # 5. Calculate uncertainty statistics
    # --------------------------------------------------

    residual_mean = (
        valid["Residual"].mean()
    )

    residual_std = (
        valid["Residual"].std(
            ddof=1
        )
    )

    n = len(valid)


    # --------------------------------------------------
    # 6. Empirical 95% prediction-error interval
    # --------------------------------------------------

    # Approximate interval for individual
    # prediction errors:
    #
    # mean residual ± 1.96 × residual SD

    uncertainty_lower = (
        residual_mean
        -
        1.96 * residual_std
    )

    uncertainty_upper = (
        residual_mean
        +
        1.96 * residual_std
    )


    # --------------------------------------------------
    # 7. 95th percentile absolute error
    # --------------------------------------------------

    error_95_percentile = np.percentile(
        valid["Absolute_Error"],
        95
    )


    # --------------------------------------------------
    # 8. Standard error of mean residual
    # --------------------------------------------------

    standard_error = (
        residual_std
        /
        np.sqrt(n)
    )


    # --------------------------------------------------
    # 9. 95% confidence interval for mean bias
    # --------------------------------------------------

    bias_ci_lower = (
        residual_mean
        -
        1.96 * standard_error
    )

    bias_ci_upper = (
        residual_mean
        +
        1.96 * standard_error
    )


    # --------------------------------------------------
    # 10. Mean absolute error
    # --------------------------------------------------

    mae = (
        valid["Absolute_Error"].mean()
    )


    # --------------------------------------------------
    # 11. RMSE
    # --------------------------------------------------

    rmse = np.sqrt(
        np.mean(
            valid["Residual"] ** 2
        )
    )


    # --------------------------------------------------
    # 12. Error threshold coverage
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
    # 13. Create uncertainty table
    # --------------------------------------------------

    uncertainty = pd.DataFrame(
        {
            "Metric": [
                "Valid borehole comparisons",
                "Mean residual",
                "Residual standard deviation",
                "MAE",
                "RMSE",
                "Standard error of mean residual",
                "95% uncertainty lower bound",
                "95% uncertainty upper bound",
                "95% absolute error percentile",
                "95% CI lower bound for mean residual",
                "95% CI upper bound for mean residual",
                "Within ±1 anomaly unit (%)",
                "Within ±2 anomaly units (%)",
                "Within ±5 anomaly units (%)",
            ],

            "Value": [
                n,
                residual_mean,
                residual_std,
                mae,
                rmse,
                standard_error,
                uncertainty_lower,
                uncertainty_upper,
                error_95_percentile,
                bias_ci_lower,
                bias_ci_upper,
                within_1,
                within_2,
                within_5,
            ],
        }
    )


    # --------------------------------------------------
    # 14. Print results
    # --------------------------------------------------

    print(
        "\n----------------------------------------------"
    )

    print(
        "UNCERTAINTY ASSESSMENT RESULTS"
    )

    print(
        "----------------------------------------------"
    )

    print(
        uncertainty.to_string(
            index=False
        )
    )


    # --------------------------------------------------
    # 15. Save uncertainty metrics
    # --------------------------------------------------

    output_file = (
        OUTPUT_DIR
        / "uncertainty_metrics.csv"
    )

    uncertainty.to_csv(
        output_file,
        index=False,
    )


    print(
        "\nSaved:",
        output_file
    )


    # --------------------------------------------------
    # 16. Final interpretation
    # --------------------------------------------------

    print(
        "\n=============================================="
    )

    print(
        "UNCERTAINTY ASSESSMENT COMPLETE"
    )

    print(
        "=============================================="
    )

    print(
        f"\n95% uncertainty interval: "
        f"{uncertainty_lower:.3f} "
        f"to "
        f"{uncertainty_upper:.3f} anomaly units"
    )

    print(
        f"95th percentile absolute error: "
        f"{error_95_percentile:.3f} anomaly units"
    )

    print(
        f"Mean residual: "
        f"{residual_mean:.3f}"
    )

    print(
        f"Residual SD: "
        f"{residual_std:.3f}"
    )


    return uncertainty


# ==================================================
# SHORT ALIAS
# ==================================================

uncertainty = uncertainty_assessment