import json
import math
import pandas_schema
from pandas_schema import Column
from pandas_schema.validation import (
    CustomElementValidation,
    InListValidation,
    DateFormatValidation,
    MatchesPatternValidation
)

from abstract_strategy import AbstractStrategy
import valida
from exceptions import CampoCabecalhoDiferenteException, ValorNaoValidoException


class Pacient(AbstractStrategy):

    MSG_DATA_INVALIDA = "data inválida"
    MSG_CPF_INVALIDO = "CPF inválido"
    MSG_EMAIL_INVALIDO = "e-mail inválido"
    MSG_NAO_VAZIO = "o campo não pode ser vazio"
    MSG_NAO_CONSTA_NA_LISTA = "valores possíveis são: 'Masculino' ou 'Feminino'"

    CABECALHO_PATIENT = ['Name', 'NUM_CARTEIRA_1__c', 'NUM_CPF__c', 'FRM_DATA_NASCIMENTO__c',
                         'Phone', 'DSC_EMAIL__c', 'COD_BENEF_UNICO__c', 'FRM_SEXO__c']

    erros_valores: dict = None

    def executar(self) -> dict:
        self._valida_csv()
        return self._gerar_json()

    def _valida_csv(self):
        if not self._valida_cabecalho():
            raise CampoCabecalhoDiferenteException(
                f'O cabeçalho do arquivo CSV com os nomes dos campos não são válidos ou não existem...\nOs campos de cabeçalho validos e na ordem indicada são:\n{self.CABECALHO_PATIENT}')

        if not self._valida_campos():
            raise ValorNaoValidoException(
                f'Foram identificados valores inválidos em alguns campos do arquivo CSV...\nConfira abaixo os campos identificados como inválidos:', data=self.erros_valores)

    def _valida_cabecalho(self):
        _cabecalho_patient = sorted(self.CABECALHO_PATIENT)
        _cabecalho_entrada = sorted(self.cabecalho_entrada)

        return _cabecalho_patient == _cabecalho_entrada

    def _valida_campos(self):
        valida_null = [CustomElementValidation(
            lambda d: not math.isnan(d), self.MSG_NAO_VAZIO)]

        schema = pandas_schema.Schema([
            Column(self.CABECALHO_PATIENT[0], [MatchesPatternValidation(
                r'.+', message=f'{self.MSG_NAO_VAZIO}')]),
            Column(self.CABECALHO_PATIENT[1], [MatchesPatternValidation(
                r'.+', message=f'{self.MSG_NAO_VAZIO}')]),
            Column(self.CABECALHO_PATIENT[2], [MatchesPatternValidation(
                valida.cpf_re(), message=f'{self.MSG_CPF_INVALIDO} ou {self.MSG_NAO_VAZIO}')]),
            # validando a data no formato en.US
            Column(self.CABECALHO_PATIENT[3], [DateFormatValidation(
                '%m/%d/%Y', message=f'{self.MSG_DATA_INVALIDA} ou {self.MSG_NAO_VAZIO}')]),
            Column(self.CABECALHO_PATIENT[4], [
                   MatchesPatternValidation(r'.+')], allow_empty=True),
            Column(self.CABECALHO_PATIENT[5], [MatchesPatternValidation(
                valida.email_re(), message=f'{self.MSG_EMAIL_INVALIDO} ou {self.MSG_NAO_VAZIO}')]),
            Column(self.CABECALHO_PATIENT[6], [MatchesPatternValidation(
                r'.+', message=f'{self.MSG_NAO_VAZIO}')]),
            Column(self.CABECALHO_PATIENT[7], [InListValidation(
                ['Masculino', 'Feminino'], message=f'{self.MSG_NAO_CONSTA_NA_LISTA} ou {self.MSG_NAO_VAZIO}')])
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
            with open('pacient_template.json', 'r') as payload:
                payload_lido = json.load(payload)
                
                payload_lido['identifier'][0]['value'] = str(row['NUM_CARTEIRA_1__c'])
                payload_lido['identifier'][1]['value'] = row['NUM_CPF__c']
                payload_lido['name'][0]['family'] = row['Name'].split()[-1].upper()
                payload_lido['name'][0]['given'][0] = row['Name'].split()[0].upper()
                payload_lido['name'][0]['text'] = row['Name'].upper()
                payload_lido['gender'] = 'female' if row['FRM_SEXO__c'] == 'Feminino' else 'male'
                # assinalando a data no formato en.US
                payload_lido['birthDate'] = row['FRM_DATA_NASCIMENTO__c']
                payload_lido['telecom'][0]['value'] = row['DSC_EMAIL__c']
                payload_lido['telecom'][1]['value'] = "" if math.isnan(row['Phone']) else row['Phone']

                payload_saida.append(payload_lido.copy())

                payload_lido = {}

        return payload_saida
