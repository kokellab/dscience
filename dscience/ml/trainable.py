import abc
from datetime import datetime
from pathlib import Path
from typing import Type
import numpy as np
import pandas as pd
from dscience.tools.filesys_tools import FilesysTools
from dscience.core import PathLike


class AbstractSaveLoad(metaclass=abc.ABCMeta):
    def save(self, path: PathLike) -> None:
        raise NotImplementedError()

    # noinspection PyAttributeOutsideInit
    def load(self, path: PathLike):
        raise NotImplementedError()


class SaveableTrainable(AbstractSaveLoad):
    """
    A simpler saveable.=
    Saves and loads a .info file with these properties.
    To implement, just override save() and load(), and have each call its supermethod
    """

    def __init__(self):
        self.info = {}

    def save(self, path: PathLike) -> None:
        FilesysTools.save_json(self.info, path.with_suffix(path.suffix + ".info"))

    def load(self, path: PathLike):
        path = Path(path)
        self.info = FilesysTools.load_json(path.with_suffix(path.suffix + ".info"))

        def fix(key, value):
            if key in ["started", "finished"]:
                return datetime.isoformat(value)
            elif isinstance(value, list):
                return np.array(value)
            else:
                return value

        self.info = {k: fix(k, v) for k, v in self.info.items()}
        return self


class SaveableTrainableCsv(SaveableTrainable, metaclass=abc.ABCMeta):
    def save(self, path: PathLike):
        path = Path(path)
        super().save(path)
        self.data.to_csv(path)

    # noinspection PyAttributeOutsideInit
    def load(self, path: PathLike):
        path = Path(path)
        super().load(path)
        self.data = pd.read_csv(path)
        return self


class SaveLoadCsv(AbstractSaveLoad, metaclass=abc.ABCMeta):
    """
    Has an attribute (property) called `data`.
    """

    @property
    @abc.abstractmethod
    def data(self) -> pd.DataFrame:
        raise NotImplementedError()

    @data.setter
    def data(self, df: pd.DataFrame):
        raise NotImplementedError()

    @property
    def df_class(self) -> Type[pd.DataFrame]:
        return pd.DataFrame

    def save(self, path: PathLike):
        if not isinstance(self.data, self.df_class):
            raise TypeError("Type {} is not a {}".format(type(self.data), self.df_class))
        path = Path(path)
        pd.DataFrame(self.data).to_csv(path)

    def load(self, path: PathLike):
        path = Path(path)
        self.data = self.df_class(pd.read_csv(path))


__all__ = ["AbstractSaveLoad", "SaveableTrainable", "SaveableTrainableCsv", "SaveLoadCsv"]
