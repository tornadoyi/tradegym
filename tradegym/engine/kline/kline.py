from typing import Optional, Sequence, Union
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from tradegym.engine.core import TObject, PrivateAttr, computed_property
from .quote import Quote


__all__ = ["KLine"]



class KLine(TObject):

    _name: str = PrivateAttr()
    _dataframe: pd.DataFrame = PrivateAttr()
    _timestep: timedelta = PrivateAttr()
    _cusor: int = PrivateAttr(0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dataframe = self.normalize_dataframe(self._dataframe)

    @computed_property
    def name(self) -> str:
        return self._name

    @computed_property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe
    
    @computed_property
    def columns(self) -> Sequence[str]:
        return self._dataframe.columns
    
    @computed_property
    def cursor(self) -> int:
        return self._cusor
    
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
    
    def next(self):
        if self.terminated:
            raise ValueError("Kline is terminated")
        self._cusor += 1

    @staticmethod
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime', ascending=True)
        df.columns = df.columns.str.split('.').str[-1]
        return df
