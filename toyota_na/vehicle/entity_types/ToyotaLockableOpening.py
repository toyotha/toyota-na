from .ToyotaOpening import ToyotaOpening


class ToyotaLockableOpening(ToyotaOpening):
    _locked: bool

    def __init__(self, closed: bool = False, locked: bool = False):
        ToyotaOpening.__init__(self, closed)
        self._locked = locked

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value):
        self._locked = value

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(closed={self._closed}, locked={self._locked})"
        )
