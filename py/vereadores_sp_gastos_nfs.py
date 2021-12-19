import datetime
import json
import io
import os
import requests

import pandas as pd
import urllib.request as request
from shutil import rmtree
from bs4 import BeautifulSoup as bs
from PyPDF2 import PdfFileWriter, PdfFileReader

DATA_DIR = os.path.join(os.getcwd(), 'data')
NFS_DIR = os.path.join(DATA_DIR, 'notas_fiscais')

COL_DESPESAS = [
    'chave', 'nome_arquivo', 'centro_custo', 'departamento',
    'tipo_departamento', 'vereador', 'ano', 'mes', 'despesa', 'cnpj',
    'fornecedor', 'valor'
]

ANO_ATUAL = datetime.datetime.now().year


def estrutura():
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if os.path.exists(NFS_DIR):
        rmtree(NFS_DIR)
    os.mkdir(NFS_DIR)


def gastos():
    gastos = pd.DataFrame(columns=COL_DESPESAS)
    base_url = 'https://app-sisgvconsulta-prd.azurewebsites.net/ws/ws2.asmx/'

    for ano in range(2017, ANO_ATUAL + 1):
        for mes in range(1, 13):
            print(f'Baixando dados de {mes}/{ano}')
            vereador_url = f'ObterDebitoVereadorJSON?ano={ano}&mes={mes}'
            lideranca_url = f'ObterDebitoLiderancaJSON?ano={ano}&mes={mes}'

            json_data = request.urlopen(base_url + vereador_url).read()
            if json_data:
                gastos = gastos.append(parse_gastos(json_data))

            json_data = request.urlopen(base_url + lideranca_url).read()
            if json_data:
                gastos = gastos.append(parse_gastos(json_data))

    arquivo = os.path.join(DATA_DIR, 'gastos_vereadores.csv')
    gastos.to_csv(arquivo, sep=';', encoding='utf-8', index=False)


def parse_gastos(json_data):
    df = pd.DataFrame(columns=COL_DESPESAS)
    data = json.loads(json_data)

    for i in data:
        chave = i['Chave']
        nome_arquivo = i['NomeArquivo']
        centro_custo = i['CENTROCUSTOSID']
        departamento = i['DEPARTAMENTO']
        tipo_departamento = i['TIPODEPARTAMENTO']
        vereador = i['VEREADOR']
        ano = i['ANO']
        mes = i['MES']
        despesa = i['DESPESA']
        cnpj = i['CNPJ']
        fornecedor = i['FORNECEDOR']
        valor = i['VALOR']

        df.loc[len(df)] = [
            chave, nome_arquivo, centro_custo, departamento, tipo_departamento,
            vereador, ano, mes, despesa, cnpj, fornecedor, valor
        ]

    return df


def notas():
    url = 'http://www.camara.sp.gov.br/wp-content/uploads/contas_vereadores/'

    for ano in range(2017, ANO_ATUAL + 1):
        ano_url = f'contas_ano_{ano}.html'
        ano_pg = bs(request.urlopen(url + ano_url).read(), 'html.parser')
        print(f'Baixando nfs de {ano}. Isso vai levar algum tempo...')
        for vereador in ano_pg.find_all('a'):
            nome = vereador.text.replace(' ', '').replace('/', '')
            vereador_pg = bs(request.urlopen(url + vereador.get('href')).read(), 'html.parser')
            vereador_dir = os.path.join(NFS_DIR, nome)
            for n in vereador_pg.find_all('a'):
                if (not os.path.exists(vereador_dir)):
                    os.mkdir(vereador_dir)

                seq = 1
                mes = n.text.split(' ')[0].lower()
                base_arquivo = f'{ano}-{mes}-{seq}.pdf'

                pdf_url = n.get('href')
                pdf = PdfFileReader(io.BytesIO(requests.get(pdf_url).content))
                for num_pgs in range(pdf.numPages):
                    pdf_out = open(os.path.join(vereador_dir, base_arquivo), 'wb')
                    writer = PdfFileWriter()
                    writer.addPage(pdf.getPage(num_pgs))
                    writer.write(pdf_out)
                    seq += 1


if __name__ == "__main__":
    estrutura()
    gastos()
    notas()
