from typing import Optional, Sequence, Union, Dict
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from tradegym.engine.core import ISerializer
from .quote import Quote


__all__ = ["KLine"]



class KLine(ISerializer):
    def __init__(self, name: str, dataframe: pd.DataFrame, timestep: timedelta, cursor: Optional[int] = None):
        self._name = name
        self._dataframe: pd.DataFrame = self.normalize_dataframe(dataframe)
        self._timestep = timestep
        self._cusor = 0 if cursor is None else cursor

    @property
    def name(self) -> str:
        return self._name

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe
    
    @property
    def columns(self) -> Sequence[str]:
        return self._dataframe.columns
    
    @property
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
    
    def to_dict(self):
        d = super().to_dict()
        d.update(
            name=self._name,
            dataframe=self._dataframe.to_dict(),
            timestep=self._timestep.total_seconds(),
            cursor=self._cusor
        )
        return d
    
    def from_dict(cls, data: Dict):
        return cls(
            name=data['name'],
            dateframe=pd.DataFrame.from_dict(data['dataframe']), 
            timestep=timedelta(seconds=data['timestep']), 
            cursor=data.get('cursor', None)
        )