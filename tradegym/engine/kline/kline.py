from typing import Optional, Sequence, Union, Dict, Callable
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from tradegym.engine.core import TObject, PrivateAttr, computed_property
from .quote import Quote


__all__ = ["KLine"]



class KLine(TObject):

    _code: str = PrivateAttr()
    _timestep: float = PrivateAttr()
    _cusor: int = PrivateAttr(0)

    _dataframe: pd.DataFrame = PrivateAttr()

    
    @computed_property
    def code(self) -> str:
        return self._code
    
    @computed_property
    def timestep(self) -> float:
        return self._timestep

    @computed_property
    def cursor(self) -> int:
        return self._cusor
    
    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def columns(self) -> Sequence[str]:
        return self._dataframe.columns

    @property
    def quote(self) -> Quote:
        return Quote.from_dict(self._dataframe.iloc[self._cusor].to_dict())
    
    @property
    def terminated(self) -> bool:
        return self._cusor + 1 >= len(self._dataframe)
    
    def __len__(self) -> int:
        return len(self._dataframe)
    
    def __getitem__(self, index: int) -> pd.Series:
        return self._dataframe.iloc[index]
    
    def setup(self, dataframe: pd.DataFrame):
        td = self._dataframe.iloc[1]["datetime"] - self._dataframe.iloc[0]["datetime"]
        assert td.total_seconds() == self._timestep, ValueError(f"timestep mismatch, expect {td.total_seconds()}, got {self._timestep}")
        self._dataframe = self.normalize_dataframe(dataframe)
    
    def locate_cursor(self, datetime: Union[datetime, str, pd.Timestamp]):
        ctime = pd.to_datetime(datetime)
        if ctime == self._dataframe[self._cusor]['datetime']:
            return
        if ctime < self._dataframe[self._cusor]['datetime']:
            raise ValueError(f"Try to locate a previous datetime '{ctime}', current datetime '{self._dataframe[self._cusor]['datetime']}'")
        if ctime - self._dataframe[self._cusor]['datetime'] <= self._timestep:
            return
        if self._cusor + 1 >= len(self._dataframe):
            raise ValueError(f"datetime '{datetime}' is out of range in kline, last datetime '{self._dataframe[self._cusor]['datetime']}'")
        if ctime - self._dataframe[self._cusor+1]['datetime'] <= self._timestep:
            self._cusor += 1
            return
        t = np.asarray(self._dataframe['datetime'])
        idx = np.searchsorted(t, ctime.to_numpy(), side='right') - 1
        if idx < 0 or (ctime.to_numpy() - self._dataframe[idx]) > self._timestep:
            raise ValueError(f"datetime '{datetime}' is out of range in kline")
        self._cusor = idx

    @staticmethod
    def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime', ascending=True)
        df.columns = df.columns.str.split('.').str[-1]
        return df
