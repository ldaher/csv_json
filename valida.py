from datetime import datetime


def data():
    return '%d/%m/%Y'


def cpf_re():
    return '^\d{3}\.\d{3}\.\d{3}\-\d{2}$'


def cnpj_re():
    return '^(\d{1,2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}|\d{14})$'


def crm_re():
    return '^(CRM\s\d{5,6}|CRM\-\d{5,6})$'


def cbo_re():
    return '^\d{6}$'


def email_re():
    return '^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'


def telefone_re():
    return '^\(\d{2}\)\s\d{4,5}\-\d{4}$'


def cep_re():
    return '^\d{4,5}\-\d{3}$'

def uf_re():
    return '^\D{2}$'
