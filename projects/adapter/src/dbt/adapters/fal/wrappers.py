"""
This module provides wrapper classes for the FAL adapter, facilitating integration with database
adapters and dynamic credential management. It includes:

- FalCredentialsWrapper: A wrapper for FAL credentials that allows dynamic type determination based
  on the execution context. It proxies attribute access to the underlying database credentials.
- FalEncAdapterWrapper: A wrapper for the FAL adapter that integrates with the database adapter,
  providing methods to submit Python jobs and execute database materializations.

The module also includes utility functions to determine the execution context from file paths and
check for specific functions in the call stack.
"""

from typing import Any, Optional, Type, Set

from dbt.adapters.factory import get_adapter_by_type
from dbt.adapters.base.meta import available
from dbt.adapters.base.impl import BaseAdapter
from dbt.contracts.connection import Credentials
from dbt.parser.manifest import ManifestLoader
from dbt.clients.jinja import MacroGenerator

from ..fal_experimental.utils import cache_static
from ..fal_experimental.impl import FalAdapterMixin
import os

class FalCredentialsWrapper:
    """
    Wrapper class for FAL credentials, allowing for dynamic type determination based on context.
    """
    _db_creds: Optional[Credentials] = None

    def __init__(self, db_creds: Credentials):
        """
        Initializes the wrapper with the given database credentials.
        """
        self._db_creds = db_creds

    @property
    def type(self):
        """
        Determines the type of the credentials based on the current model's file context.
        """
        # Determine context using the file type approach
        model_file_path = self.get_current_model_file_path()  # Placeholder for actual implementation
        context = get_context_from_file(model_file_path)
        if context == 'sql':
            return self._db_creds.type
        elif context == 'python':
            return 'fal'
        else:
            raise ValueError(f"Unknown file extension in {model_file_path}")

    def __getattr__(self, name: str) -> Any:

        """
        Directly proxy to the DB adapter, just shadowing the type
        """
        return getattr(self._db_creds, name)

    def get_current_model_file_path(self) -> str:

        """
        Retrieves the current model's file path from the dbt context or environment.
        """
        # Implement logic to retrieve the current model's file path
        # This function should access the dbt context or environment to get the current model file path
        # Placeholder: return a static path or integrate with dbt internals
        return "/path/to/current/model/file.sql"  # Example placeholder


class FalEncAdapterWrapper(FalAdapterMixin):
    """
    Wrapper class for the FAL adapter, integrating with the database adapter.
    """
    def __init__(self, db_adapter_type: Type[BaseAdapter], config):
        """
        Initializes the wrapper with the given database adapter type and configuration.
        """
        # Use the db_adapter_type connection manager
        self.ConnectionManager = db_adapter_type.ConnectionManager

        db_adapter = get_adapter_by_type(db_adapter_type.type())
        super().__init__(config, db_adapter)

        self._available_ = self._db_adapter._available_.union(self._available_)
        self._parse_replacements_.update(self._db_adapter._parse_replacements_)

    def submit_python_job(self, *args, **kwargs):
        """
        Submits a Python job using the FAL adapter.
        """
        return super().submit_python_job(*args, **kwargs)

    @available
    def db_materialization(self, context: dict, materialization: str):
        """
        Executes a database materialization using the specified context and materialization name.
        """
        materialization_macro = self.manifest.find_materialization_macro_by_name(
            self.config.project_name, materialization, self._db_adapter.type()
        )

        return MacroGenerator(
            materialization_macro, context, stack=context["context_macro_stack"]
        )()

    @property
    @cache_static
    def manifest(self):
        """
        Loads and returns the full manifest for the current configuration.
        """
        return ManifestLoader.get_full_manifest(self.config)

    def type(self):
        # Determine context using the file type approach
        model_file_path = self.get_current_model_file_path()  # Placeholder for actual implementation
        context = get_context_from_file(model_file_path)
        if context == 'sql':
            return self._db_adapter.type()
        elif context == 'python':
            return 'fal'
        else:
            raise ValueError(f"Unknown file extension in {model_file_path}")

    def get_current_model_file_path(self) -> str:
        # Implement logic to retrieve the current model's file path
        # This function should access the dbt context or environment to get the current model file path
        # Placeholder: return a static path or integrate with dbt internals
        return "/path/to/current/model/file.sql"  # Example placeholder

    def __getattr__(self, name):
        """
        Proxies attribute access to the underlying database adapter or the superclass.
        Directly proxy to the DB adapter, Python adapter in this case does what we explicitly define in this class.
        """
        if hasattr(self._db_adapter, name):
            return getattr(self._db_adapter, name)
        else:
            return getattr(super(), name)


def get_context_from_file(file_path: str) -> str:
    """
    Determine the execution context based on the file extension.
    :param file_path: Path to the model file being executed.
    :return: 'sql' if it's a SQL file, 'python' if it's a Python file, otherwise 'unknown'.
    """
    _, file_extension = os.path.splitext(file_path)
    if file_extension == '.sql':
        return 'sql'
    elif file_extension == '.py':
        return 'python'
    return 'unknown'


def find_funcs_in_stack(funcs: Set[str]) -> bool:
    """
    Checks if any of the specified functions are present in the current call stack.
    """
    import inspect

    frame = inspect.currentframe()
    while frame:
        if frame.f_code.co_name in funcs:
            return True
        frame = frame.f_back

    return False
