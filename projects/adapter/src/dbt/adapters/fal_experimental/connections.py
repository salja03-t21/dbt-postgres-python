"""
This module defines connection-related classes and enums for the FAL adapter,
including credentials and connection management for teleportation and execution
of Python code in different environments.
"""

from dataclasses import dataclass
from typing import Optional
import os

from dbt.adapters.base import Credentials
from dbt.dataclass_schema import StrEnum, ExtensibleDbtClassMixin

from dbt.fal.adapters.python import PythonConnectionManager


DEFAULT_HOSTS = {
    "cloud": "api.alpha.fal.ai",
    "cloud-eu": "api.eu.fal.ai",
}


class TeleportTypeEnum(StrEnum):
    """
    Enum representing the types of teleportation supported by the FAL adapter.
    """
    LOCAL = "local"
    REMOTE_S3 = "s3"


@dataclass
class TeleportCredentials(ExtensibleDbtClassMixin):
    type: TeleportTypeEnum

    # local
    local_path: Optional[str] = os.getcwd()

    # s3
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_access_key_id: Optional[str] = None
    s3_access_key: Optional[str] = None


class FalConnectionManager(PythonConnectionManager):
    """
    Manages connections for the FAL adapter, extending the PythonConnectionManager
    to handle teleportation and execution of Python code.
    """
    TYPE = "fal_experimental"

    @classmethod
    def open(cls, connection):
        raise NotImplementedError

    def execute(self, compiled_code: str):
        raise NotImplementedError

    def cancel(self, connection):
        raise NotImplementedError


@dataclass
class FalCredentials(Credentials):
    default_environment: str = "local"
    teleport: Optional[TeleportCredentials] = None
    host: str = ""
    key_secret: str = ""
    key_id: str = ""

    # NOTE: So we are allowed to not set them in profiles.yml
    # they are ignored for now
    database: str = ""
    schema: str = ""

    def __post_init__(self):
        if self.host in list(DEFAULT_HOSTS.keys()):
            self.host = DEFAULT_HOSTS[self.host]

    @property
    def type(self):
        return "fal_experimental"

    def _connection_keys(self):
        return ()
