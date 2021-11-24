
import json
import math
import pandas_schema
from pandas_schema import Column
from pandas_schema.validation import (
    CustomElementValidation,
    InListValidation,
    MatchesPatternValidation
)
import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')

from abstract_strategy import AbstractStrategy
import valida
from exceptions import CampoCabecalhoDiferenteException, ValorNaoValidoException


class Organization(AbstractStrategy):

    MSG_CNPJ_INVALIDO = "CNPJ inválido (padrão: 14 dígitos ou 99.999.999/9999-99)"
    MSG_TELEFONE_INVALIDO = "telefone inválido (padrão: (99) 9999-9999 ou (99) 99999-9999)"
    MSG_CEP_INVALIDO = "cep inválido (padrão: 99999-999)"
    MSG_CNES_INVALIDO = "código CNES inválido (padrão: mínimo de 3 dígitos)"
    MSG_NAO_VAZIO = "o campo não pode ser vazio"
    MSG_NAO_CONSTA_NA_LISTA = "valores possíveis são: 'Ativo' ou 'Inativo'"

    CABECALHO_ORGANIZATION = ['Name', 'CNPJ__c', 'COD_PRESATADOR__c', 'StatusPrestador__c', 'Filial__c',
                              'Regional__c', 'Phone', 'RUA__c', 'CEP__c', 'Regiao__c', 'PAIS__c', 'CODIGO_CNES_PRESTADOR__c']

    erros_valores: dict = None

    def executar(self) -> dict:
        self._valida_csv()
        return self._gerar_json()

    def _valida_csv(self):
        if not self._valida_cabecalho():
            raise CampoCabecalhoDiferenteException(
                f'O cabeçalho do arquivo CSV com os nomes dos campos não são válidos ou não existem...\nOs campos de cabeçalho validos e na ordem indicada são:\n{self.CABECALHO_ORGANIZATION}')

        if not self._valida_campos():
            raise ValorNaoValidoException(
                f'Foram identificados valores inválidos em alguns campos do arquivo CSV...\nConfira abaixo os campos identificados como inválidos:', data=self.erros_valores)

    def _valida_cabecalho(self):
        _cabecalho_practitioner = sorted(self.CABECALHO_ORGANIZATION)
        _cabecalho_entrada = sorted(self.cabecalho_entrada)

        return _cabecalho_practitioner == _cabecalho_entrada

    def _valida_campos(self):
        valida_null = [CustomElementValidation(
            lambda d: not math.isnan(d), self.MSG_NAO_VAZIO)]

        schema = pandas_schema.Schema([
            # Name
            Column(self.CABECALHO_ORGANIZATION[0], [MatchesPatternValidation(
                r'.+', message=f'{self.MSG_NAO_VAZIO}')]),
            # CNPJ__c
            Column(self.CABECALHO_ORGANIZATION[1], [MatchesPatternValidation(
                valida.cnpj_re(), message=f'{self.MSG_CNPJ_INVALIDO} ou {self.MSG_NAO_VAZIO}')]),
            # COD_PRESTADOR__c
            Column(self.CABECALHO_ORGANIZATION[2], [
                   MatchesPatternValidation(r'.+', message=f'{self.MSG_NAO_VAZIO}')]),
            # StatusPrestador__c
            Column(self.CABECALHO_ORGANIZATION[3], [InListValidation(
                ['Ativo', 'Inativo'], message=f'{self.MSG_NAO_CONSTA_NA_LISTA} ou {self.MSG_NAO_VAZIO}')]),
            # Filial__c
            Column(self.CABECALHO_ORGANIZATION[4], [
                   MatchesPatternValidation(r'.+')], allow_empty=True),
            # Regional__c
            Column(self.CABECALHO_ORGANIZATION[5], [
                   MatchesPatternValidation(r'.+')], allow_empty=True),
            # Phone
            Column(self.CABECALHO_ORGANIZATION[6], [
                   MatchesPatternValidation(valida.telefone_re(), message=f'{self.MSG_TELEFONE_INVALIDO} ou {self.MSG_NAO_VAZIO}')]),
            # RUA__c
            Column(self.CABECALHO_ORGANIZATION[7], [
                   MatchesPatternValidation(r'.+', message=f'{self.MSG_NAO_VAZIO}')]),
            # CEP__c
            Column(self.CABECALHO_ORGANIZATION[8], [MatchesPatternValidation(
                valida.cep_re(), message=f'{self.MSG_CEP_INVALIDO} ou {self.MSG_NAO_VAZIO}')]),
            # Regiao__c
            Column(self.CABECALHO_ORGANIZATION[9], [
                   MatchesPatternValidation(r'.+')], allow_empty=True),
            # PAIS__c
            Column(self.CABECALHO_ORGANIZATION[10], [
                   MatchesPatternValidation(r'.+')], allow_empty=True),
            # CODIGO_CNES_PRESTADOR__c
            Column(self.CABECALHO_ORGANIZATION[11], [MatchesPatternValidation(
                r'\d{3,}', message=f'{self.MSG_CNES_INVALIDO} ou {self.MSG_NAO_VAZIO}')])
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
            with open('organization_template.json', 'r') as payload:
                payload_lido = json.load(payload)

                payload_lido['identifier'][0]['value'] = str(
                    row['CNPJ__c'])
                payload_lido['name'] = row['Name'].upper()
                payload_lido['address'][0]['city'] = 'SÃO PAULO'

                _rua = row['RUA__c'].split('-')[0].lstrip().rstrip().upper()
                _bairro = row['RUA__c'].split('-')[1].lstrip().rstrip().upper()
                payload_lido['address'][0]['district'] = _bairro
                payload_lido['address'][0]['line'][0] = _rua
                payload_lido['address'][0]['postalCode'] = row['CEP__c']
                payload_lido['telecom'][0]['value'] = row['Phone']

                payload_saida.append(payload_lido.copy())

                payload_lido = {}

        return payload_saida
