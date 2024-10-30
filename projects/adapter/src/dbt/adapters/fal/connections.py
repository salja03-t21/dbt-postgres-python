from dataclasses import dataclass
from src.dbt.adapters.fal_experimental.connections import FalCredentials


@dataclass
class FalEncCredentials(FalCredentials):
    """
    Extended credentials class for FAL, including a database profile.
    """
    db_profile: str = ""

    def _connection_keys(self):
        """
        Returns the connection keys for the credentials.
        """
        return () + super()._connection_keys()

    @property
    def type(self):
        """
        Returns the type of the connection, which is 'fal'.
        """
        return "fal"

    @property
    def unique_field(self):
        """
        Returns the unique field for the credentials, which is the database profile.
        """
        return self.db_profile
