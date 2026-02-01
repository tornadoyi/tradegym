from typing import Optional
import pandas as pd
from tradegym.engine.core import TObject, ConfigDict



__all__ = ["Quote"]



class Quote(TObject):

    model_config = ConfigDict(extra='allow')

    @property
    def datetime(self) -> pd.Timestamp:
        return self._containers["datetime"]
