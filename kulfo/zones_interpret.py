from pathlib import Path

import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from rasterio.transform import rowcol
from rasterio.warp import transform_bounds
from pyproj import Transformer


DATA_FILE = (
    Path(__file__).parent
    / "data"
    / "Kulfo_GW_Anomaly_UNet_30m_PROTOTYPE.tif"
)


def classify_zone(value):

    if np.isnan(value):
        return (
            "NoData",
            "No groundwater prediction is available at this location."
        )

    if value < -2:
        return (
            "Very High Depletion",
            "Very high groundwater depletion compared with the reference condition"
        )

    elif value < -1:
        return (
            "High Depletion",
            "High groundwater depletion compared with the reference condition"
        )

    elif value <= 1:
        return (
            "Moderate / Near Reference",
            "Groundwater condition is close to the reference condition"
        )

    elif value <= 2:
        return (
            "High Recharge",
            "High groundwater storage compared with the reference condition"
        )

    else:
        return (
            "Very High Recharge",
            "Very high groundwater storage compared with the reference condition"
        )


def zones_interpret_map():

    # ========================================
    # READ RASTER
    # ========================================

    with rasterio.open(DATA_FILE) as src:

        data = src.read(1).astype(float)

        if src.nodata is not None:
            data[data == src.nodata] = np.nan

        transform = src.transform
        raster_crs = src.crs

        height = src.height
        width = src.width

        bounds = transform_bounds(
            raster_crs,
            "EPSG:4326",
            *src.bounds
        )

    # ========================================
    # COORDINATE TRANSFORMER
    # ========================================

    transformer = Transformer.from_crs(
        "EPSG:4326",
        raster_crs,
        always_xy=True
    )

    # ========================================
    # CREATE FIVE ZONES
    # ========================================

    zones = np.full(data.shape, np.nan)

    zones[data < -2] = 1

    zones[
        (data >= -2) &
        (data < -1)
    ] = 2

    zones[
        (data >= -1) &
        (data <= 1)
    ] = 3

    zones[
        (data > 1) &
        (data <= 2)
    ] = 4

    zones[data > 2] = 5

    # ========================================
    # MAP
    # ========================================

    cmap = ListedColormap(
        [
            "darkred",
            "red",
            "lightgray",
            "lightgreen",
            "darkgreen",
        ]
    )

    fig, ax = plt.subplots(figsize=(12, 10))

    ax.imshow(
        zones,
        cmap=cmap,
        vmin=1,
        vmax=5,
        extent=[
            bounds[0],
            bounds[2],
            bounds[1],
            bounds[3],
        ],
        interpolation="none",
        origin="upper",
    )

    ax.set_title(
        "Kulfo Groundwater Storage Zones\n"
        "30 m Spatial Resolution"
    )

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # ========================================
    # LEGEND
    # ========================================

    from matplotlib.patches import Patch

    legend_elements = [
        Patch(
            facecolor="darkred",
            label="Very High Depletion (< -2)"
        ),
        Patch(
            facecolor="red",
            label="High Depletion (-2 to -1)"
        ),
        Patch(
            facecolor="lightgray",
            label="Moderate / Near Reference (-1 to +1)"
        ),
        Patch(
            facecolor="lightgreen",
            label="High Recharge (+1 to +2)"
        ),
        Patch(
            facecolor="darkgreen",
            label="Very High Recharge (> +2)"
        ),
    ]

    ax.legend(
        handles=legend_elements,
        loc="upper right"
    )

    # ========================================
    # CLICK FUNCTION
    # ========================================

    def onclick(event):

        if event.inaxes != ax:
            return

        if event.xdata is None or event.ydata is None:
            return

        # ------------------------------------
        # Clicked geographic coordinates
        # ------------------------------------

        longitude = float(event.xdata)
        latitude = float(event.ydata)

        # ------------------------------------
        # Convert WGS84 → raster CRS
        # ------------------------------------

        x, y = transformer.transform(
            longitude,
            latitude
        )

        # ------------------------------------
        # Convert raster coordinates → pixel
        # ------------------------------------

        row, col = rowcol(
            transform,
            x,
            y
        )

        row = int(row)
        col = int(col)

        # ------------------------------------
        # Print diagnostic information
        # ------------------------------------

        print("\nGROUNDWATER PIXEL INTERPRETATION")
        print("--------------------------------")
        print(f"Latitude: {latitude:.6f}")
        print(f"Longitude: {longitude:.6f}")
        print(f"Raster X: {x:.3f}")
        print(f"Raster Y: {y:.3f}")
        print(f"Pixel row: {row}")
        print(f"Pixel col: {col}")

        # ------------------------------------
        # Check pixel position
        # ------------------------------------

        if not (
            0 <= row < height and
            0 <= col < width
        ):

            print("Status: Outside raster extent")
            return

        # ------------------------------------
        # Read anomaly
        # ------------------------------------

        value = data[row, col]

        # ------------------------------------
        # Handle NaN / NoData
        # ------------------------------------

        if np.isnan(value):

            print("Groundwater anomaly: NoData")
            print("Zone: NoData")
            print(
                "Interpretation: No groundwater prediction "
                "is available at this location."
            )
            print(
                "Reference condition: "
                "April 2023 (wet season)"
            )

            return

        # ------------------------------------
        # Interpret valid pixel
        # ------------------------------------

        zone, interpretation = classify_zone(value)

        print(f"Groundwater anomaly: {value:.4f}")
        print(f"Zone: {zone}")
        print(f"Interpretation: {interpretation}")
        print(
            "Reference condition: "
            "April 2023 (wet season)"
        )

    # ========================================
    # CONNECT CLICK EVENT
    # ========================================

    fig.canvas.mpl_connect(
        "button_press_event",
        onclick
    )

    plt.tight_layout()
    plt.show()


# ============================================
# PUBLIC FUNCTION
# ============================================

spatial_gw_zones_interpret = zones_interpret_map