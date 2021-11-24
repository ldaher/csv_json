import re
import sys

from transformar import Transformar
from entidades_enum import Entidades
from pacient_impl import Pacient
from practitioner_impl import Practitioner
from organization_impl import Organization


class Menu:

    def show(self):
        opcao = None

        while True:
            opcao = input(
                f'Opções:\n1) Gerar Payload\n2) Sair\n: ')
            rg = re.compile('^(1|2)$')

            if not rg.search(opcao):
                print('Escolha uma das opções disponíveis...')
            else:
                opcao = int(opcao)
                break

        def um():
            self._escolher_entidade()

        def dois():
            sys.exit(0)

        switcher = {
            1: um,
            2: dois
        }

        switcher.get(opcao)()

    def _escolher_entidade(self):
        entidade = None

        print('Selecione a entidade:')
        i = 1
        for name, member in Entidades.__members__.items():
            id = member.value
            print(f'{id}) {Entidades(id).capitalized}')
            i = + 1
        while True:
            valor = input(': ')

            rg = re.compile(f'(^[1-{len(Entidades)}]$)')

            if rg.search(valor):
                break

            print('Escolha uma das opções disponíveis...')

        self._transformar(Entidades(int(valor)))

    def _transformar(self, entidade: Entidades):
        def pacient():
            return Pacient()

        def practitioner():
            return Practitioner()

        def organization():
            return Organization()

        switcher = {
            1: pacient,
            2: practitioner,
            3: organization,
        }

        _strategy = switcher.get(entidade.value)()

        _transformar = Transformar(_strategy)
        _transformar.executar()
        self.show()
