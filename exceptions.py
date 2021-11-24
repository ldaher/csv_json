from pandas_schema import ValidationWarning

class CampoCabecalhoDiferenteException(Exception):
    pass


class CabecalhoNaoPresenteException(Exception):
    pass


class ValorNaoValidoException(Exception):

    def __init__(self, *args: object, data: ValidationWarning) -> None:
        super().__init__(*args)
        self.data = data
    pass
