from abc import ABCMeta, abstractclassmethod
from json import encoder
import os
import re
import csv
import json
from pathlib import Path
import pandas as pd
from exceptions import CabecalhoNaoPresenteException


class AbstractStrategy(metaclass=ABCMeta):

    NOVA_LINHA = os.linesep
    SEPARADOR_DIR = os.sep

    csv_: pd.DataFrame = None
    cabecalho_entrada: list = list()

    @abstractclassmethod
    def executar(self) -> dict:
        pass

    def entrada(self):
        while True:
            local = input("Informe a localização do arquivo CSV: ")

            if self._valida_caminho(local, 'csv'):
                try:
                    ler_arq = open(
                        local, 'r', newline=self.NOVA_LINHA, encoding='UTF-8')
                    prim_linha = ler_arq.readline().rstrip()

                    if csv.Sniffer().has_header(prim_linha):
                        if self.cabecalho_entrada:
                            self.cabecalho_entrada = list()

                        for cab in prim_linha.split(','):
                            self.cabecalho_entrada.append(cab)
                            
                        ler_arq.seek(0)
                    else:
                        raise CabecalhoNaoPresenteException(
                            'Arquivo CSV informado parece não possuir cabeçalho com o nome dos campos...')

                    self.csv_ = pd.read_csv(ler_arq, dtype=str)

                    break
                except FileNotFoundError:
                    print('Arquivo não encontrado. Tente novamente...')
            else:
                print(
                    'Caminho digitado não é válido. Insira uma caminho válido para o arquivo ".csv"...')

    def saida(self, json_: dict) -> dict:
        while True:
            local = input(
                'Informe o local aonde deseja salvar o arquivo JSON: ')

            if self._valida_caminho(local, 'json'):
                try:
                    is_arquivo_existe = Path(local)

                    if is_arquivo_existe.is_file():
                        is_deseja_subescrever = input(
                            "Um arquivo com o nome informado já existe. Deseja substituir [s|n]? ")

                        _regex = re.compile('(s|n)')

                        if _regex.search(is_deseja_subescrever.lower()):
                            if is_deseja_subescrever == 'n':
                                continue

                    with open(local, mode='w', newline=self.NOVA_LINHA) as escreve_arq:
                        json.dump(json_, escreve_arq, indent=4, ensure_ascii=False)
                        print(
                            f'Arquivo {escreve_arq.name} salvo com sucesso...')
                        break

                except Exception as e:
                    print(
                        f'Ocorreu um erro no processo de escrita do arquivo JSON...\n{e}')
                    continue
            else:
                print('Caminho ou extensão de arquivo inválidos. Certique-se que o caminho é válido, a extensão seja ".json" e tente novamente...')

    def _valida_caminho(self, local: str, extensao: str) -> bool:
        regex = re.compile(f'^\D\:?\{self.SEPARADOR_DIR}?.+?\.{extensao}$')

        if regex.search(local):
            return True

        return False
