import os, json, time
from io import BytesIO
from zipfile import ZipFile
import requests as r

data_dir = 'fotos_tse_2020'
estados = 'AC AC AM RR PA AP TO MA PI CE RN PB PE AL SE BA MG ES RJ SP PR SC RS MS MT GO'

url_base = 'http://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/'
path = 'buscar/2020/{}/2030402020/candidato/{}'
url = url_base + path

zip_path = 'http://agencia.tse.jus.br/estatistica/sead/odsele/consulta_cand/'
zip_file = 'consulta_cand_2020.zip'
file = zip_path + zip_file
zipfile = ZipFile(BytesIO(r.get(file).content))


def fetch_data():
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for e in estados.split(' '):
        cid = []
        cand = []
        for l in zipfile.open('consulta_cand_2020_{}.csv'.format(e)).readlines():
            linha = l.decode('latin-1').split(';')
            cid.append(linha[11].replace('"', ''))
            cand.append(linha[15].replace('"', ''))

        lista = [(cand[i],cid[i]) for i in range(0,len(cand))]
        lista.pop(0)
        for x in lista:
            time.sleep(0.1)
            link = url.format(x[1], x[0])
            try:
                data = r.get(link).json()
                for k, v in data.items():
                    if k == "fotoUrl":
                        image = r.get(v)
                        if image.status_code == 200:
                            filename = '{}_{}_{}.jpg'.format(e, x[1], x[0])
                            with open('{}/{}'.format(data_dir, filename), 'wb') as f:
                                f.write(image.content)
            except:
                pass


if __name__ == '__main__':
    fetch_data()
