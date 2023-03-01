import csv
import struct
from operator import itemgetter
from pathlib import Path

# Arquivos
SCHEMA = 'dict_PNADC_022019.csv'    # Arquivo com schema
DATA = 'bruto_PNADC_022019.txt'     # Arquivo com dados brutos
OUTPUT_FILE = 'PNADC_022019.csv'    # Arquivo parseado


def get_struct_unpacker(fieldspecs, istart, iwidth):
    """
    Cria string para struct.unpack usar, com base nos fieldspecs.

    Os fieldspecs são informações obtidas a partir de um arquivo csv que
    funciona como 'schema' da estrutura da base de dados. O csv contém
    os campos 'variavel', 'posicao' (a posição inicial dos valores da
    variável) e 'tamanho' (a quantidade de caracteres a partir da
    posição inicial contendo os valores da variável).

    Exemplo:

        "variavel","posicao","tamanho"
        "Ano",1,4
        "Trimestre",5,1
        "UF",6,2
        "Capital",8,2
        "RM_RIDE",10,2
        "UPA",12,9
        "Estrato",21,7
        "V1008",28,2
        (...)

    Desta forma, este script pode ser usado com qualquer base de dados
    delimitados por posição de caractere/tamanho do campo, bastando
    apenas um novo csv com tais informações: 'variavel', 'posicao' e
    'tamanho'.

    Outputs:
        string (str) no formato "6s2s3s7x7s4x9s"
    """
    unpack_len = 0
    unpack_fmt = ""
    for fieldspec in fieldspecs:
        start = fieldspec[istart] - 1
        end = start + fieldspec[iwidth]
        if start > unpack_len:
            unpack_fmt += str(start - unpack_len) + "x"
        unpack_fmt += str(end - start) + "s"
        unpack_len = end
    struct_unpacker = struct.Struct(unpack_fmt).unpack_from
    return struct_unpacker


# Constrói 'schema'
fieldspecs = []
with open(SCHEMA, newline='') as f:
    reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    next(reader)
    for row in reader:
        fieldspecs.append(
            [int(v) if isinstance(v, float) else v for v in row]
        )

iname, istart, iwidth = 0, 1, 2
fieldspecs.sort(key=itemgetter(istart))
struct_unpacker = get_struct_unpacker(fieldspecs, istart, iwidth)
field_indices = range(len(fieldspecs))

# Aplica 'schema' nos dados
data = []
for line in Path(DATA).open():
    raw_fields = struct_unpacker(line.encode())
    line_data = {}
    for i in field_indices:
        fieldspec = fieldspecs[i]
        fieldname = fieldspec[iname]
        value = str(raw_fields[i].decode().strip())
        line_data[fieldname] = value
    data.append(line_data)


