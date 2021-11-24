
import json
import math
from typing import Tuple
import pandas_schema
from pandas_schema import Column
from pandas_schema.validation import (
    CustomElementValidation,
    InListValidation,
    DateFormatValidation,
    MatchesPatternValidation,
    IsDtypeValidation
)

from abstract_strategy import AbstractStrategy
import valida
from exceptions import CampoCabecalhoDiferenteException, ValorNaoValidoException


class Practitioner(AbstractStrategy):

    MSG_EMAIL_INVALIDO = "e-mail inválido"
    MSG_CEP_INVALIDO = "cep inválido (padrão: 99999-999)"
    MSG_CRM_INVALIDO = "código CRM inválido (padrão: CRM 99999 ou CRM-99999)"
    MSG_CBO_INVALIDO = "código CBO inválido (padrão: 6 dígitos numéricos (ex.: 999999))"
    MSG_UF_INVALIDO = "código UF inválido (padrão: 2 letras (ex.: SP))"
    MSG_NAO_VAZIO = "o campo não pode ser vazio"
    MSG_NAO_CONSTA_NA_LISTA = "valores possíveis são: 'true' ou 'false'"

    CABECALHO_PRACTITIONER = [
        'Name', 'CRM', 'UF', 'Especialidade', 'Ativo', 'CBO', 'Email', 'Rua', 'CEP']

    erros_valores: dict = None

    def executar(self) -> dict:
        self._valida_csv()
        return self._gerar_json()

    def _valida_csv(self):
        if not self._valida_cabecalho():
            raise CampoCabecalhoDiferenteException(
                f'O cabeçalho do arquivo CSV com os nomes dos campos não são válidos ou não existem...\nOs campos de cabeçalho validos e na ordem indicada são:\n{self.CABECALHO_PRACTITIONER}')

        if not self._valida_campos():
            raise ValorNaoValidoException(
                f'Foram identificados valores inválidos em alguns campos do arquivo CSV...\nConfira abaixo os campos identificados como inválidos:', data=self.erros_valores)

    def _valida_cabecalho(self):
        _cabecalho_practitioner = sorted(self.CABECALHO_PRACTITIONER)
        _cabecalho_entrada = sorted(self.cabecalho_entrada)

        return _cabecalho_practitioner == _cabecalho_entrada

    def _valida_campos(self):
        valida_null = [CustomElementValidation(
            lambda d: not math.isnan(d), self.MSG_NAO_VAZIO)]

        schema = pandas_schema.Schema([
            # Name
            Column(self.CABECALHO_PRACTITIONER[0], [MatchesPatternValidation(
                r'.+', message=f'{self.MSG_NAO_VAZIO}')]),
            # CRM
            Column(self.CABECALHO_PRACTITIONER[1], [MatchesPatternValidation(
                valida.crm_re(), message=f'{self.MSG_CRM_INVALIDO} ou {self.MSG_NAO_VAZIO}')]),
            # UF
            Column(self.CABECALHO_PRACTITIONER[2], allow_empty=True),
            # Especialidade
            Column(self.CABECALHO_PRACTITIONER[3], allow_empty=True),
            # Ativo
            Column(self.CABECALHO_PRACTITIONER[4], allow_empty=True),
            # CBO
            Column(self.CABECALHO_PRACTITIONER[5], [
                   MatchesPatternValidation(valida.cbo_re(), message=f'{self.MSG_CBO_INVALIDO} ou {self.MSG_NAO_VAZIO}')]),
            # Email
            Column(self.CABECALHO_PRACTITIONER[6], allow_empty=True),
            # Rua
            Column(self.CABECALHO_PRACTITIONER[7], allow_empty=True),
            # CEP
            Column(self.CABECALHO_PRACTITIONER[8], allow_empty=True),
        ])

        try:
            self.erros_valores = schema.validate(self.csv_)

            if self.erros_valores:
                return False
        except Exception as e:
            raise e

        return True

    def _gerar_json(self) -> dict:
        payload_saida: list = []

        for index, row in self.csv_.iterrows():
            with open('practitioner_template.json', 'r') as payload:
                payload_lido = json.load(payload)

                payload_lido['identifier'][0]['value'] = str(
                    row['CBO'])
                payload_lido['identifier'][1]['value'] = row['CRM']
                payload_lido['name'][0]['family'] = row['Name'].split(
                )[-1].upper()
                payload_lido['name'][0]['given'][0] = row['Name'].split()[
                    0].upper()
                payload_lido['name'][0]['text'] = row['Name'].upper()
                payload_lido['qualification'][0]['code']['coding'][2]['code'] = row['CBO']
                payload_lido['qualification'][0]['code']['text'] = f'CBO-{row["CBO"]}-SP'

                payload_saida.append(payload_lido.copy())

                payload_lido = {}

        return payload_saida
