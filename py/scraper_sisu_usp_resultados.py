import os
import time
import csv

from selenium import webdriver

cols = [
    'ies', 'campus', 'curso', 'grau_turno', 'modalidade',
    'classificacao', 'nome', 'inscricao', 'nota'
]

codigos = [
    96518, 96519, 96520, 96521, 96522, 96523, 96524, 96525, 96527, 96528,
    96530, 96531, 96532, 96533, 96534, 96535, 96536, 96537, 96537, 96540,
    96541, 96542, 96543, 96544, 96545, 96546, 96547, 96548, 96549, 96550,
    96551, 96552, 96553, 96554, 96554, 96555, 96562, 96564, 96565, 96567,
    96568, 96569, 96570, 96571, 96572, 96573, 96573, 96574, 96576, 96577,
    96578, 96579, 96580, 96581, 96582, 96583, 96584, 96585, 96586, 96587,
    96588, 96589, 96590, 96591, 96592, 96593, 96595, 96596, 96597, 96598,
    96599, 96600, 96601, 96602, 96605, 96606, 96607, 96608, 96609, 96610,
    96611, 96612, 96613, 96614, 96615, 96616, 96617, 96618, 96620, 96621,
    96622, 96623, 96624, 96625, 96626, 96627, 96628, 96629, 96630, 96631,
    96632, 96634, 96635, 96636, 96637, 96638, 96639, 96640, 96641, 96642,
    96643, 96644, 96645, 96646, 96647, 96648, 96649, 96650, 96651, 96652,
    96653, 96654, 96655, 96656, 96657, 96658, 96659, 96660, 96661, 96662,
    96663, 96664, 96665, 96666, 96667, 96668, 96670, 96671, 96672, 96673,
    96674, 96675, 96676, 96677, 96678, 96679, 96680, 96681, 96682, 96683,
    96684, 96685, 96686, 96687, 96688, 96689, 96690, 96693, 96710, 96713,
    96714, 96715, 96716, 96717, 96718, 96719, 96720, 96721, 96722, 96723,
    96724, 96725, 96728, 96729, 96730
]

start = time.time()

if not os.path.exists('arquivos_csv'):
    os.makedirs('arquivos_csv')

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
prefs = {
    'profile.default_content_setting_values.automatic_downloads': 1,
    'profile.managed_default_content_settings.images': 2
}
options.add_experimental_option('prefs', prefs)

browser = webdriver.Chrome('chromedriver', chrome_options=options)

for codigo in codigos:
    time.sleep(0.1)
    browser.get(f'http://www.sisu.mec.gov.br/selecionados?co_oferta={codigo}')
    with open(f'arquivos_csv/sisu_resultados_usp_final.csv', 'a') as file:
        dw = csv.DictWriter(file, fieldnames=cols, lineterminator='\n')
        dw.writeheader()
        ies = browser.find_element_by_xpath('//div[@class ="nome_ies_p"]').text.strip()
        campus = browser.find_element_by_xpath('//div[@class ="nome_campus_p"]').text.strip()
        curso = browser.find_element_by_xpath('//div[@class ="nome_curso_p"]').text.strip()
        grau_turno = browser.find_element_by_xpath('//div[@class = "grau_turno_p"]').text.strip()
        tabelas = browser.find_elements_by_xpath('//table[@class = "resultado_selecionados"]')
        for t in tabelas:
            modalidade = t.find_element_by_xpath('tbody//tr//th[@colspan = "4"]').text.strip()
            aprovados = t.find_elements_by_xpath('tbody//tr')
            for a in aprovados[2:]:
                linha = a.find_elements_by_class_name('no_candidato')
                classificacao = linha[0].text.strip()
                nome = linha[1].text.strip()
                inscricao = linha[2].text.strip()
                nota = linha[3].text.strip().replace(',', '.')
                dw.writerow({
                    'ies': ies, 'campus': campus, 'curso': curso,
                    'grau_turno': grau_turno, 'modalidade': modalidade,
                    'classificacao': classificacao, 'nome': nome,
                    'inscricao': inscricao, 'nota': nota
                })

browser.quit()
end = time.time()
print(f'{len(codigos)} páginas raspadas em {end - start} segundos.')
