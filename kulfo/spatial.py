"""Spatial groundwater functions."""

from pathlib import Path

import rasterio
from rasterio.warp import transform

DATA_FILE = (
    Path(__file__).parent
    / "data"
    / "Kulfo_GW_Anomaly_UNet_30m_PROTOTYPE.tif"
)


def spatial_gw_value(latitude, longitude):
    """Return the predicted spatial groundwater anomaly at a location."""

    with rasterio.open(DATA_FILE) as src:
        # Convert raster bounds to latitude/longitude
        xs = [src.bounds.left, src.bounds.right]
        ys = [src.bounds.bottom, src.bounds.top]

        lons, lats = transform(
            src.crs,
            "EPSG:4326",
            xs,
            ys
        )

        min_lon = min(lons)
        max_lon = max(lons)
        min_lat = min(lats)
        max_lat = max(lats)

        # Check whether location is inside prediction area
        if not (
            min_lat <= latitude <= max_lat
            and min_lon <= longitude <= max_lon
        ):
            raise ValueError(
                "Location is outside the Kulfo prediction area.\n"
                f"Valid latitude: {min_lat:.5f} to {max_lat:.5f}° N\n"
                f"Valid longitude: {min_lon:.5f} to {max_lon:.5f}° E"
            )

        # Convert input coordinates to raster CRS
        x, y = transform(
            "EPSG:4326",
            src.crs,
            [longitude],
            [latitude]
        )

        row, col = src.index(x[0], y[0])

        result = src.read(1)[row, col]

        if src.nodata is not None and result == src.nodata:
            return None

        return float(result)


def spatial_gw_interpret(latitude, longitude):
    """Interpret the spatial groundwater condition at a location."""

    value = spatial_gw_value(latitude, longitude)

    if value is None:
        return "No groundwater prediction available at this location."

    if value > 0:
        return (
            "Groundwater condition: Higher predicted groundwater storage\n"
            "Reference condition: Defined model reference"
        )

    if value < 0:
        return (
            "Groundwater condition: Lower predicted groundwater storage\n"
            "Reference condition: Defined model reference"
        )

    return (
        "Groundwater condition: Close to the reference condition\n"
        "Reference condition: Defined model reference"
    )