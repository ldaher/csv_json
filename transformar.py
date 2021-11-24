import csv
import pandas as pd

from exceptions import ValorNaoValidoException
from abstract_strategy import AbstractStrategy


class Transformar:

    def __init__(self, strategy: AbstractStrategy) -> None:
        self._strategy = strategy

    def executar(self):
        try:
            self._strategy.entrada()
            json_ = self._strategy.executar()
            self._strategy.saida(json_)
        except ValorNaoValidoException as e:
            erros = {'row': [], 'column': [], 'value': [], 'message': []}

            for d in e.data:
                erros['row'].append(d.row + 2)
                erros['column'].append(d.column)
                erros['value'].append('vazio' if str(d.value) == 'nan' else str(d.value))
                erros['message'].append(d.message)

            pd.set_option('display.max_colwidth', None)

            erros_saida = pd.DataFrame(data=erros)
            erros_saida.columns = ['Linha', 'Coluna',
                                   'Valor Informado', 'Mensagem']
            erros_saida.style.set_properties(
                subset=['Mensage'], **{'width': '1000px'})

            print(f'{e}\n{erros_saida}')
        except Exception as e:
            print(e)
