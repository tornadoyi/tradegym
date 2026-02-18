from typing import Optional, Sequence, Union
import numpy as np
from datetime import datetime
import pandas as pd
from tradegym.engine.core import TObject, Field, writable
from .quote import Quote


__all__ = ["KLine"]



class KLine(TObject):

    code: str = Field()
    timestep: float = Field()
    cursor: int = Field(0)

    dataframe: pd.DataFrame = Field(None, exclude=True)

    @property
    def dataframe(self) -> pd.DataFrame:
        return self.dataframe

    @property
    def columns(self) -> Sequence[str]:
        return self.dataframe.columns

    @property
    def quote(self) -> Quote:
        return Quote.deserialize(self.dataframe.iloc[self.cursor].to_dict())
    
    @property
    def terminated(self) -> bool:
        return self.cursor + 1 >= len(self.dataframe)
    
    def __len__(self) -> int:
        return len(self.dataframe)
    
    def __getitem__(self, index: int) -> pd.Series:
        return self.dataframe.iloc[index]

    @writable    
    def setup(self, dataframe: pd.DataFrame):
        self.dataframe = self.normalize_dataframe(dataframe)
        td = self.dataframe.iloc[1]["datetime"] - self.dataframe.iloc[0]["datetime"]
        assert td.total_seconds() == self.timestep, ValueError(f"timestep mismatch for code '{self.code}', expect {self.timestep}, got {td.total_seconds()}")
    
    @writable
    def reset(self, datetime: Union[datetime, str, pd.Timestamp]):
        ctime = pd.to_datetime(datetime)
        exact_match = self.dataframe.index[self.dataframe['datetime'] == ctime]
        if len(exact_match) > 0:
            self.cursor = exact_match[0]
            return
        mask = (self.dataframe['datetime'] < ctime)
        if not mask.any():
            raise ValueError(f"datetime '{datetime}' is out of range in kline, code: '{self.code}' timestep: '{self.timestep}'")
        self.cursor = self.dataframe.loc[mask, 'datetime'].idxmax()

    @writable
    def tick(self, datetime: Union[datetime, str, pd.Timestamp]):
        ctime = pd.to_datetime(datetime)
        if ctime < self.dataframe.iloc[self.cursor]['datetime']:
            raise ValueError(f"Try to locate a previous datetime '{ctime}', current datetime '{self.dataframe[self.cursor]['datetime']}'")
        elif ctime == self.dataframe.iloc[self.cursor]['datetime']:
            return
        else:
            if self.cursor + 1 >= len(self.dataframe):
                return
            if ctime == self.dataframe.iloc[self.cursor+1]['datetime']:
                self.cursor += 1

    @staticmethod
    def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime', ascending=True)
        df.columns = df.columns.str.split('.').str[-1]
        return df
