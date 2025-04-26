from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("google_asset_query_converter")
except PackageNotFoundError:
    pass
