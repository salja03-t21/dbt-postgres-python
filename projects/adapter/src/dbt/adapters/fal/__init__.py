from dbt.adapters.base import AdapterPlugin
from src.dbt.adapters.fal.connections import FalEncCredentials
from src.dbt.include import fal

# Avoid loading the plugin code for any import
def __getattr__(name):
    if name == "FalEncAdapter":
        from src.dbt.adapters.fal.impl import FalEncAdapter

        return FalEncAdapter
    if name == "Plugin":
        from src.dbt.adapters.fal.impl import FalEncAdapter

        return AdapterPlugin(
            adapter=FalEncAdapter,
            credentials=FalEncCredentials,
            include_path=fal.PACKAGE_PATH
        )

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
