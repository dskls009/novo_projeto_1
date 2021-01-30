import PySimpleGUI as sg
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from variaveis import DATABASE

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE

db = SQLAlchemy(app)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kanji = db.Column(db.String(255))
    kana = db.Column(db.String(255))
    english = db.Column(db.String(255))

db.create_all()

cabecalho = ['id', 'kanji', 'kana', 'english']

def iniciar_busca():
    busca = []
    data = []
    for i in range(len(cabecalho)):
            data.append('')
        
    busca.append(data)
    return busca

def atualizar_query():
    data = Card.query.add_columns('id', 'kanji', 'kana', 'english').all()
    lista = []
    col_1 = []
    col_2 = []
    col_3 = []
    col_4 = []
    if len(data) != 0:
        for datum in data:
            col_1.append(datum[1])
            col_2.append(datum[2])
            col_3.append(datum[3])
            col_4.append(datum[4])

        for i in range(len(col_1)):
            lista.append([])
            lista[i].append(col_1[i])
            lista[i].append(col_2[i])
            lista[i].append(col_3[i])
            lista[i].append(col_4[i])
    else:
        for i in range(len(cabecalho)):
            data.append('')
        
        lista.append(data)

    return lista

# sg.theme("SystemDefaultForReal")

req = []
layout = [
    [sg.Input(key='-BUSCA-')],
    [sg.Button("Pesquisar", bind_return_key=True, enable_events=True)],
    [sg.Table(values=iniciar_busca(), headings=cabecalho, key='-RESULT-')],
    [sg.Button("Adicionar")],
    [sg.Table(values=atualizar_query(), headings=cabecalho, key='-TABLE-')]
]

window = sg.Window("titulo", layout)
busca = []
while True:
    event, values = window.read()

    kanji = ''
    kana = ''
    english = ''
    
    col_1 = []
    col_2 = []
    col_3 = []
    col_4 = []
    i = 1

    if event == sg.WINDOW_CLOSED:
        break

    if event == 'Pesquisar' and len(values['-BUSCA-']):
        req = requests.get('https://jisho.org/api/v1/search/words?', params={'keyword':values['-BUSCA-']})
        json = req.json()
        busca = []
        for data in json['data']:
            kanji = ''
            kana = ''
            english = ''
            for listajp in data['japanese']:
                if listajp.get('word'):
                    kanji = kanji+listajp.get('word')+'/'
                kana = kana+listajp.get('reading')+'/'
            for listaen in data['senses']:
                for en in listaen.get('english_definitions'):
                    english = english+en+', '
            kanji = kanji[:-1]
            kana = kana[:-1]
            english = english[:-2]
        
            col_1.append(i)
            col_2.append(kanji)
            col_3.append(kana)
            col_4.append(english)
            i+=1
        for i in range(len(col_1)):
            busca.append([])
            busca[i].append(col_1[i])
            busca[i].append(col_2[i])
            busca[i].append(col_3[i])
            busca[i].append(col_4[i])

        window['-RESULT-'].update(values=busca)
    if event == 'Adicionar':
        for y in busca:
            if not Card.query.filter_by(kanji=y[1], kana=y[2], english=y[3]).first():
                c = Card(kanji=y[1], kana=y[2], english=y[3])
        
                db.session.add(c)
                db.session.commit()
        
        window['-TABLE-'].update(values=atualizar_query())

window.close()
