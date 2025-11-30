import re
import threading
import time

import requests
from bs4 import BeautifulSoup

import links_alvos

URL = links_alvos.url
URL_ALVO = links_alvos.url_alvo

LINK_ENCONTRADOS = []
TELEFONES = []

def requisicao(url):
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            # print(f'>>>> request {url} deu certo')
            return resposta.text
        else:
            print('Erro ao fazer requisição', resposta.status_code)
    except Exception as e:
        print('Erro na requisão: ', e)

def parsing_html(html_bruto):
    try:
        soup = BeautifulSoup(html_bruto, 'html.parser')
        return soup
    except Exception as e:
        print('Erro ao fazer parsing: ', e)
        return None

def encontrar_links(soup):
    cards_pai = soup.find('div', class_=links_alvos.class_container_de_links)
    cards = cards_pai.find_all('a')

    links = []
    for card in cards:
        try:
            link = card['href']
            links.append(link)
        except:
            pass

    return links

def encontrar_telefones(soup):
    try:
        descricao = soup.find_all('div', class_=links_alvos.class_container_de_texto)[2].p.get_text().strip()
        # [2] - esse trecho foi adaptado para a situação de exemplo
    except Exception as e:
        print('Erro: descrição não encontrada no site -', e)
        return None
    regex = re.findall(r"\(?0?[(]?([1-9]{2})[)]?[ -.]?(9[ -.]?)(\d{4})[ -.]?(\d{4})", descricao)
    if regex:
        return regex

def descobrir_telefones():
    while True:
        try:
            link = LINK_ENCONTRADOS.pop(0)
        except:
            return None
        resposta_anuncio = requisicao(URL + link)
        if resposta_anuncio:
            soup_anuncio = parsing_html(resposta_anuncio)
            if soup_anuncio:
                telefone = encontrar_telefones(soup_anuncio)
                if telefone:
                    print('/////Telefone encontrado:', telefone)
                    TELEFONES.append(telefone)
                    salvar_telefones(telefone)

def salvar_telefones(telefone):
    for n in range(len(telefone)):
        str_telefone = f'({telefone[n][0]}) {telefone[n][1]} {telefone[n][2]}-{telefone[n][3]}\n'
        # print('str tel - ', str_telefone)
        
        try:
            with open('telefones.csv', 'a') as arq:
                arq.write(str_telefone)
        except Exception as e:
            print('Erro ao salvar telefones')

def criar_executar_threads(numero):
    threads_ = []
    for i in range(numero):
        t = threading.Thread(target = descobrir_telefones)
        threads_.append(t)
    
    for t in threads_:
        t.start()
    
    for t in threads_:
        t.join()

def contar_telefones_encontrados():
    count = 0
    for n in range(len(TELEFONES)):
        for telefone in TELEFONES[n]:
            count += 1
    return count

if __name__ == '__main__':
    print('--------------------------------')
    print('Bem vindo ao Web Crawler de números de telefone!')
    print('--------------------------------')
    resposta_busca = requisicao(URL_ALVO)
    if resposta_busca:
        soup_busca = parsing_html(resposta_busca)
        if soup_busca:
            LINK_ENCONTRADOS = encontrar_links(soup_busca)
            print('Quantas threads você quer utilizar para realizar a varredura?')
            num_threads = input()
            print('Deseja registrar quanto o programa vai demorar?')
            contar_tempo = input('(s/n): ')
            contar_tempo = True if contar_tempo == 's' else False
            if contar_tempo:
                start_time = time.perf_counter()
            criar_executar_threads(int(num_threads))

            print('\nTELEFONES:\n', TELEFONES)
            if contar_tempo:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                numero_de_telefones_encontrados = contar_telefones_encontrados()
                print(f'{numero_de_telefones_encontrados} telefones encontrados em {execution_time:.2f}s')