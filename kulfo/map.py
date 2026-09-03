"""Spatial groundwater map for the Kulfo Watershed."""

from pathlib import Path
import rasterio
import matplotlib.pyplot as plt

DATA_FILE = Path(__file__).parent / "data" / "Kulfo_GW_Anomaly_UNet_30m_PROTOTYPE.tif"

def map():
    """Display the 30 m Kulfo groundwater anomaly map."""
    with rasterio.open(DATA_FILE) as src:
        data = src.read(1)
        bounds = src.bounds
        nodata = src.nodata

    data = data.astype(float)
    if nodata is not None:
        data[data == nodata] = float("nan")

    plt.figure(figsize=(10, 8))
    plt.imshow(data, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top], origin="upper")
    plt.colorbar(label="Groundwater anomaly")
    plt.xlabel("Easting (m)")
    plt.ylabel("Northing (m)")
    plt.title("Kulfo Groundwater Anomaly — 30 m U-Net")
    plt.tight_layout()
    plt.show()
