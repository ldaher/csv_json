from enum import Enum


class Entidades(Enum):
    PACIENT = 1, 'Pacient'
    PRACTITIONER = 2, 'Practitioner'
    ORGANIZATION = 3, 'Organization'

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, capitalized: str = None):
        self._capitalized_ = capitalized

    def __str__(self):
        return self.value

    @property
    def capitalized(self):
        return self._capitalized_

