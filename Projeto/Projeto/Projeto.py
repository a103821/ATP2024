import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
from collections import Counter
from datetime import datetime

script_dir = os.getcwd()
bd_artigos = os.path.join(script_dir, "ata_medica_papers.json")
ficheiroexistente="ata_medica_papers.json"
def ascii_art(): # função só para identificar o nome da app
    ascii_art="""
                                                
   _____                      __       ___                  __                    
  / ___/___  ____ ___________/ /_     /   | _________ _____/ ___  ____ ___  __  __
  \__ \/ _ \/ __ `/ ___/ ___/ __ \   / /| |/ ___/ __ `/ __  / _ \/ __ `__ \/ / / /
 ___/ /  __/ /_/ / /  / /__/ / / /  / ___ / /__/ /_/ / /_/ /  __/ / / / / / /_/ / 
/____/\___/\__,_/_/   \___/_/ /_/  /_/  |_\___/\__,_/\__,_/\___/_/ /_/ /_/\__, /  
                                                                         /____/                                                               
"""
    
    
    return ascii_art
def verificarformatodata(data):
    try:
        partes = data.split('-')
        if len(partes) != 3:
            return False
        ano, mes, dia = map(int, partes)
        
        # Verifica se o ano, mês e dia estão dentro dos limites esperados
        if len(str(ano)) != 4 or not (1 <= mes <= 12):
            return False
        
        # Verifica se o ano é válido
        if not (1 <= ano <= 2024):
            return False
        
        # Calcula o número de dias no mês, considerando anos bissextos
        dias_por_mes = {
            1: 31, 2: 29 if (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)) else 28,
            3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31,
            11: 30, 12: 31
        }
        
        # Verifica se o dia está dentro do limite para o mês
        if not (1 <= dia <= dias_por_mes[mes]):
            return False
        
        return True
    except ValueError:
        # Captura erros de conversão, como ao tentar map(int, partes) em strings inválidas
        return False
    except KeyError:
        # Captura acessos inválidos ao dicionário dias_por_mes
        return False
def escolher_estatistica(json_file):# função para criar esteticamente a pagina com os diferentes botões
    data = carrega_data(json_file)
    if data:
        anos_disponiveis = sorted({datetime.strptime(pub.get('publish_date', '').split(' ')[0], '%Y-%m-%d').year for pub in data if 'publish_date' in pub})
    else:
        anos_disponiveis = []

    anos_disponiveis.insert(0, "Todos")  
    
    layout = [
        [sg.Text('Escolha a estatística que deseja visualizar:')],
        [sg.Radio('Publicações por Ano', 'RADIO1', key='-ANO-', enable_events=True)],
        [sg.Radio('Publicações por Mês', 'RADIO1', key='-MES-', enable_events=True)],
        [sg.Radio('Top 20 Autores', 'RADIO1', key='-AUTORES-', enable_events=True)],
        [sg.Radio('Top 20 Palavras-Chave', 'RADIO1', key='-PALAVRAS-', enable_events=True)],
        [sg.Radio('Palavras-Chave mais frequentes em um Ano', 'RADIO1', key='-PALAVRAS_ANO-', enable_events=True)],
        [sg.Radio('Distribuição de Publicações de um Autor por Anos', 'RADIO1', key='-AUTOR_ANOS-', enable_events=True)],
        [sg.Text('Ano:', size=(8, 1)), sg.Combo(anos_disponiveis, default_value="Todos", key='-ANO_SELECIONADO-', disabled=True)],
        [sg.Text('Autor:', size=(8, 1)), sg.InputText(key='-AUTOR-', disabled=True)],
        [sg.Button('Gerar Gráfico'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Escolher Estatística', layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Cancelar'):
            break
        elif event in ('-MES-', '-ANO-', '-AUTORES-', '-PALAVRAS-', '-AUTOR_ANOS-', '-PALAVRAS_ANO-'):
            # Habilitar ou desabilitar campos conforme a opção selecionada
            window['-ANO_SELECIONADO-'].update(disabled=not (values['-MES-'] or values['-PALAVRAS_ANO-']))
            window['-AUTOR-'].update(disabled=not values['-AUTOR_ANOS-'])
        elif event == 'Gerar Gráfico':
            tipo_estatistica = None
            if values['-ANO-']:
                tipo_estatistica = 'Ano'
            elif values['-MES-']:
                tipo_estatistica = 'Mês'
            elif values['-AUTORES-']:
                tipo_estatistica = 'Autores'
            elif values['-PALAVRAS-']:
                tipo_estatistica = 'Palavras-Chave'
            elif values['-AUTOR_ANOS-']:
                tipo_estatistica = 'AutorAnos'
            elif values['-PALAVRAS_ANO-']:
                tipo_estatistica = 'Palavras-Chave por Ano'
            else:
                sg.popup('Por favor, selecione uma estatística.')
                continue

            ano_selecionado = values['-ANO_SELECIONADO-']
            autor_selecionado = values['-AUTOR-']
            gerar_graficos(json_file, tipo_estatistica, ano_selecionado, autor_selecionado)
            break

    window.close()
def gerar_graficos(json_file, tipo_estatistica, ano_selecionado, autor_selecionado):
    data = carrega_data(json_file)
    if not data:
        sg.popup('Nenhuma publicação encontrada para gerar estatísticas!')
        return

    if tipo_estatistica in ['Mês', 'PalavrasAno'] and ano_selecionado != "Todos":
        try:
            ano_selecionado = int(ano_selecionado)
            data = [pub for pub in data if 'publish_date' in pub and datetime.strptime(pub['publish_date'].split(' ')[0], '%Y-%m-%d').year == ano_selecionado]
        except ValueError:
            sg.popup('Ano inválido selecionado!')
            return

    if tipo_estatistica == 'AutorAnos' and autor_selecionado:
        data = [pub for pub in data if any(autor_selecionado.lower() in a.get('name', '').lower() for a in pub.get('authors', []))]

    # Processar os dados
    anos = []
    meses = []
    autores = []
    palavras_chave = []

    for pub in data:
        # Processar data de publicação
        data_publicacao = pub.get('publish_date', '')
        if isinstance(data_publicacao, str):
            data_publicacao = data_publicacao.split(' ')[0]
            try:
                data_obj = datetime.strptime(data_publicacao, '%Y-%m-%d')
                anos.append(data_obj.year)
                meses.append(data_obj.month)
            except ValueError:
                continue  # Ignorar publicações com data inválida

        # Processar autores
        autores.extend([autor['name'] for autor in pub.get('authors', [])])

        # Processar palavras-chave
        keywords = pub.get('keywords', '')
        if isinstance(keywords, str):
            palavras_chave.extend([kw.strip() for kw in keywords.split(',')])
        elif isinstance(keywords, list):
            palavras_chave.extend([kw.strip() for kw in keywords])  

    
    fig, axs = plt.subplots(1, 1, figsize=(10, 6))

    if tipo_estatistica == 'Ano':
        if anos:
            axs.bar(*zip(*Counter(anos).items()))
            axs.set_title('Distribuição por Ano')
            axs.set_xlabel('Ano')
            axs.set_ylabel('Publicações')
        else:
            axs.text(0.5, 0.5, 'Nenhum dado disponível', horizontalalignment='center', verticalalignment='center', fontsize=12)

    elif tipo_estatistica == 'Mês':
        if meses:
            axs.bar(*zip(*Counter(meses).items()))
            titulo = f'Distribuição por Mês ({ano_selecionado if ano_selecionado != "Todos" else "Todos os Anos"})'
            axs.set_title(titulo)
            axs.set_xlabel('Mês')
            axs.set_ylabel('Publicações')
        else:
            axs.text(0.5, 0.5, 'Nenhum dado disponível', horizontalalignment='center', verticalalignment='center', fontsize=12)

    elif tipo_estatistica == 'Autores':
        if autores:
            top_autores = Counter(autores).most_common(20)
            axs.barh([a[0] for a in top_autores], [a[1] for a in top_autores])
            axs.set_title('Top 20 Autores')
            axs.set_xlabel('Número de Publicações')
            axs.invert_yaxis()
        else:
            axs.text(0.5, 0.5, 'Nenhum dado disponível', horizontalalignment='center', verticalalignment='center', fontsize=12)

    elif tipo_estatistica == 'Palavras-Chave':
        if palavras_chave:
            # Filtrar palavras-chave não vazias
            palavras_chave_filtradas = [kw for kw in palavras_chave if kw.strip()]
        
            # Gerar o top 20 das palavras-chave
            top_palavras = Counter(palavras_chave_filtradas).most_common(20)
        
            if top_palavras:
                axs.barh([p[0] for p in top_palavras], [p[1] for p in top_palavras])
                axs.set_title('Top 20 Palavras-Chave')
                axs.set_xlabel('Frequência')
                axs.invert_yaxis()
            else:
                axs.text(0.5, 0.5, 'Nenhum dado disponível', horizontalalignment='center', verticalalignment='center', fontsize=12)
        else:
            axs.text(0.5, 0.5, 'Nenhum dado disponível', horizontalalignment='center', verticalalignment='center', fontsize=12)
    
    
    elif tipo_estatistica == 'AutorAnos':
        dbase = carrega_data(json_file)
        if not autor_selecionado:  
            sg.popup('Nenhum autor selecionado!')  
            return  
        autor_existente = any(autor_selecionado in [a.get("name") for a in artigo.get("authors", [])] for artigo in dbase)
    
        if not autor_existente:
            sg.popup(f'Este autor não existe: {autor_selecionado}')
            return  
        # Contar publicações por ano
        contagem = Counter()
        n_d_count = 0  # Contador para publicações sem data

        for artigo in dbase:
            
            if any(a.get("name") == autor_selecionado for a in artigo.get("authors", [])):
                if "publish_date" in artigo and artigo["publish_date"]:  # Se há uma data de publicação
                    ano = artigo["publish_date"].split('-')[0]  # Extrai o ano
                    contagem[ano] += 1
                else:
                    n_d_count += 1  # Incrementa o contador de publicações sem data

        # Extraindo os anos e as contagens
        if contagem:
            anos_list, publicacoes = zip(*contagem.items())
            anos_list = list(map(int, anos_list))  # Converte os anos para inteiros
            publicacoes = list(publicacoes)

            
            largura_barra = 0.5 if len(anos_list) == 1 else 0.8

            axs.bar(anos_list, publicacoes, width=largura_barra, label='Publicações com Data')

            axs.set_title(f'Distribuição de Publicações de {autor_selecionado} por Anos')
            axs.set_xlabel('Ano')
            axs.set_ylabel('Número de Publicações')
            axs.legend()

            axs.set_xlim(min(anos_list) - 1, max(anos_list) + 2)  # Ajusta os limites
            axs.set_xticks(anos_list) 
            axs.set_xticklabels(anos_list) 

        else:
            
            sg.popup(f'O autor {autor_selecionado} não possui publicações com data definida. '
                    f'Número de publicações sem data: {n_d_count}', title='Informação')
            return  

        # Se houver publicações sem data, exibir uma anotação no gráfico
        if n_d_count > 0:
            axs.text(max(anos_list) + 1, n_d_count * 0.9, f'Publicações sem Data: {n_d_count}',
                    color='orange', fontsize=12, verticalalignment='center')
            



    elif tipo_estatistica == 'Palavras-Chave por Ano':
        if palavras_chave:
            # Filtrar palavras-chave não vazias
            palavras_chave_filtradas = [kw for kw in palavras_chave if kw.strip()]
            
            # Obter as palavras-chave mais frequentes no ano selecionado
            top_palavras = Counter(palavras_chave_filtradas).most_common(10)  # Top 10 
            
            if top_palavras:  
                palavras, frequencias = zip(*top_palavras)
                axs.barh(palavras, frequencias,)  # Cria o gráfico
                titulo = f'Top 10 Palavras-Chave ({ano_selecionado})'
                axs.set_title(titulo)
                axs.set_xlabel('Frequência')
                axs.invert_yaxis()  # Inverter o eixo Y para que o mais frequente fique no topo
            else:
                axs.text(0.5, 0.5, 'Nenhum dado disponível', horizontalalignment='center', verticalalignment='center', fontsize=12)
        else:
            axs.text(0.5, 0.5, 'Nenhum dado disponível', horizontalalignment='center', verticalalignment='center', fontsize=12)


    plt.tight_layout()  # Ajustar o layout para evitar cortes
    layout = [
        [sg.Canvas(key='-CANVAS-', size=(800, 600))],  
        [sg.Button('Fechar')]
    ]

    window = sg.Window('Estatísticas de Publicação', layout, finalize=True, modal=True)

    # Integrar matplotlib no Canvas do PySimpleGUI
    canvas_elem = window['-CANVAS-']
    canvas = FigureCanvasTkAgg(fig, canvas_elem.Widget)
    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

    
    while True:
        event, _ = window.read(timeout=100)
        if event == 'Fechar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
    plt.close(fig)
def editar_publicacao_window(publicacao, json_file, database):

    keywords_str = ', '.join(publicacao.get('keywords', [])) if isinstance(publicacao.get('keywords', []), list) else publicacao.get('keywords', '')#vai buscar a palavra chave e separa-a por virgulas
    layout = [
        [sg.Text('Título:'), sg.InputText(publicacao.get('title', ''), key='-TITLE-')],
        [sg.Text('Resumo:'), sg.Multiline(publicacao.get('abstract', ''), key='-ABSTRACT-', size=(80, 15))],
        [sg.Text('Autores:'), sg.InputText(', '.join([author['name'] for author in publicacao.get('authors', [])]), key='-AUTHORS-')],
        [sg.Text('Palavras-chave:'), sg.InputText(keywords_str, key='-KEYWORDS-')],  
        [sg.Text('DOI:'), sg.InputText(publicacao.get('doi', ''), key='-DOI-')],
        [sg.Text('Data de Publicação:'), sg.InputText(publicacao.get('publish_date', ''), key='-PUBLISH_DATE-')],
        [sg.Text('URL do PDF:'), sg.InputText(publicacao.get('pdf', ''), key='-PDF-')],
        [sg.Text('URL do Artigo:'), sg.InputText(publicacao.get('url', ''), key='-URL-')],
        [sg.Button('Guardar', key='-SAVE-'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Editar Publicação', layout, modal=True)

    while True:
        event, values = window.read()

        if event == '-SAVE-':
            # Verificações antes de salvar
            if not values['-TITLE-']:  # Verifica se o título está vazio
                sg.popup('O título é obrigatório!')
                continue
            
            # Verifica o formato da data (AAAA-MM-DD) e até à data desejada
            if not verificarformatodata(values['-PUBLISH_DATE-']):
                sg.popup('A data deve ser válida e estar no formato AAAA-MM-DD, até á data 2024-12-31!!')
                continue


            # Atualiza os dados da publicação
            publicacao['title'] = values['-TITLE-']
            publicacao['abstract'] = values['-ABSTRACT-']
            publicacao['authors'] = [{'name': name.strip()} for name in values['-AUTHORS-'].split(',') if name.strip()]
            publicacao['keywords'] = [kw.strip() for kw in values['-KEYWORDS-'].split(',') if kw.strip()]  
            publicacao['doi'] = values['-DOI-']
            publicacao['publish_date'] = values['-PUBLISH_DATE-']
            publicacao['pdf'] = values['-PDF-']
            publicacao['url'] = values['-URL-']

            # Salva os dados atualizados no arquivo
            atualiza_data(json_file, database)
            sg.popup('Alterações guardadas com sucesso!')
            break

        elif event == 'Cancelar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
def listar_publicacoes_window(json_file):
    database = carrega_data(json_file)
    if not database:
        sg.popup('Nenhuma publicação encontrada!')
        return

    publicacoes_com_titulo = [pub.get('title', 'Título não especificado') for pub in database]

    layout = [
        [sg.Text('Título'), sg.InputText(key='-TITLE-', enable_events=True)],
        [sg.Text('Lista de Publicações:', font=('Helvetica', 14))],
        [sg.Listbox(values=publicacoes_com_titulo, size=(120, 25), key='-PUBLICATIONS-', enable_events=True)],
        [sg.Button('Detalhes', key='-DETAILS-'), sg.Button('Editar', key='-EDIT-'), sg.Button('Fechar')]
    ]

    window = sg.Window('Lista de Publicações', layout, size=(900, 600), modal=True)

    while True:
        event, values = window.read()

        if event == '-TITLE-':# so vao aparecer publicações em que o título só corresponde ao filtro
            search_text = values['-TITLE-'].lower()
            filtered_publicacoes = [pub for pub in publicacoes_com_titulo if search_text in pub.lower()]
            window['-PUBLICATIONS-'].update(values=filtered_publicacoes)

        elif event == '-DETAILS-':#abrir a publicação do titulo selecionado
            selected = values['-PUBLICATIONS-']
            if selected:
                pub_title = selected[0]
                pub = next((pub for pub in database if pub.get('title') == pub_title), None)
                if pub:
                    detalhes = f"""
Título: {pub.get('title', 'N/A')}\n\n
Resumo: {pub.get('abstract', 'N/A')}\n
Autores:
"""
                    for author in pub.get('authors', []):
                        detalhes += f"  - {author.get('name', 'N/A')}\n"

                    detalhes += f"""
Palavras-chave: {pub.get('keywords', 'N/A')}\n
Data de Publicação: {pub.get('publish_date', 'N/A')}\n
DOI: {pub.get('doi', 'N/A')}

URL do PDF: {pub.get('pdf', 'N/A')}
URL do Artigo: {pub.get('url', 'N/A')}
"""
                    sg.popup_scrolled(detalhes.strip(), title='Detalhes da Publicação', size=(60, 20))
                else:
                    sg.popup('Publicação não encontrada.')
            else:
                sg.popup('Por favor, selecione uma publicação.')

        elif event == '-EDIT-':#o que acontece se se carregar em editar
            selected = values['-PUBLICATIONS-']
            if selected:
                pub_title = selected[0]
                pub = next((pub for pub in database if pub.get('title') == pub_title), None)
                if pub:
                    editar_publicacao_window(pub, json_file, database)
                else:
                    sg.popup('Publicação não encontrada.')
            else:
                sg.popup('Por favor, selecione uma publicação.')

        elif event == 'Fechar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
def consulta_window(json_file):
    layout = [
        [sg.Text('Escolha o tipo de consulta:')],
        [sg.Button('Por Título'), sg.Button('Por Autor'), sg.Button('Por Afiliação'), sg.Button('Por Data'), sg.Button('Por Palavras-chave')],
        [sg.Button('Voltar')]
    ]

    window = sg.Window('Consulta de Publicações', layout)

    while True:
        event, _ = window.read()

        if event == 'Por Título':
            consulta_por_titulo(json_file)
        elif event == 'Por Autor':
            consulta_por_autor(json_file)
        elif event == 'Por Afiliação':
            consulta_por_afiliacao(json_file)
        elif event == 'Por Data':
            consulta_por_data(json_file)
        elif event == 'Por Palavras-chave':
            consulta_por_palavras_chave(json_file)
        elif event == 'Voltar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
def consulta_por_titulo(json_file):
    database = carrega_data(json_file)
    layout = [
        [sg.Text('Digite o título:'), sg.InputText(key='-TITLE-')],
        [sg.Button('Buscar'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Consulta por Título', layout)

    while True:
        event, values = window.read()

        if event == 'Buscar':
            titulo = values['-TITLE-'].lower()
            resultados = [artigo for artigo in database if 'title' in artigo and titulo in artigo['title'].lower()]
            if resultados:
                detalhes = "\n\n".join(f"Título: {artigo['title']}\nResumo: {artigo.get('abstract', 'N/A')}" for artigo in resultados)
                sg.popup_scrolled(detalhes, title='Resultados da Consulta')
            else:
                sg.popup('Nenhum artigo encontrado com este título.')
        elif event == 'Cancelar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
def consulta_por_autor(json_file):
    database = carrega_data(json_file)
    autores = []
    for artigo in database:
        for autor in artigo.get("authors", []):
            if "name" in autor and autor["name"] not in autores:
                autores.append(autor["name"])

    layout = [
        [sg.Text("Digite o nome do autor ou selecione abaixo:")],
        [sg.Input(key="-SEARCH-", enable_events=True)],
        [sg.Listbox(values=autores, size=(50, 10), key="-AUTORES-", enable_events=True)],
        [sg.Button("Pesquisar"), sg.Button("Fechar")]
    ]

    window = sg.Window("Consulta por Autor", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Fechar":
            break

        if event == "-SEARCH-":
            search_text = values["-SEARCH-"].lower()
            filtered_autores = [a for a in autores if search_text in a.lower()]
            window["-AUTORES-"].update(values=filtered_autores)

        if event == "Pesquisar":
            selected = values["-AUTORES-"]
            if not selected:
                sg.popup("Nenhum autor selecionado!")
                continue
            autor_selecionado = selected[0]
            artigos = [
                artigo for artigo in database
                if any(a.get("name", "").lower() == autor_selecionado.lower() for a in artigo.get("authors", []))
            ]
            
            if artigos:
                artigos_layout = [
                    [sg.Text(f"Artigos de {autor_selecionado}:")],
                    [sg.Listbox(values=[artigo.get('title', 'N/A') for artigo in artigos], size=(60, 15), key="-ARTIGOS-", enable_events=True)],
                    [sg.Button("Selecionar Artigo"), sg.Button("Voltar")]
                ]
                
                artigos_window = sg.Window("Selecionar Artigo", artigos_layout)

                while True:
                    artigos_event, artigos_values = artigos_window.read()

                    if artigos_event == sg.WINDOW_CLOSED or artigos_event == "Voltar":
                        break

                    if artigos_event == "Selecionar Artigo":
                        selected_artigo = artigos_values["-ARTIGOS-"]
                        if not selected_artigo:
                            sg.popup("Nenhum artigo selecionado!")
                            continue
                        
                        artigo_selecionado = next(artigo for artigo in artigos if artigo.get('title') == selected_artigo[0])

                        detalhes = [
                         f"Título: {artigo_selecionado.get('title', 'N/A')}",
                         f"Resumo: {artigo_selecionado.get('abstract', 'N/A')}",
                         f"Palavras-chave: {', '.join(artigo_selecionado.get('keywords', '').split(', ')) if isinstance(artigo_selecionado.get('keywords', '') , str) else 'N/A'}",
                         f"DOI: {artigo_selecionado.get('doi', 'N/A')}",
                         f"PDF: {artigo_selecionado.get('pdf', 'N/A')}",
                         f"Data de Publicação: {artigo_selecionado.get('publish_date', 'N/A')}",
                         f"URL: {artigo_selecionado.get('url', 'N/A')}"
                            ]

                        sg.popup_scrolled("\n\n".join(detalhes), title="Detalhes do Artigo", size=(60, 20))

                artigos_window.close()
            else:
                sg.popup("Nenhum artigo encontrado para este autor!")

    window.close()
def consulta_por_afiliacao(json_file):
    database = carrega_data(json_file)
    afiliacoes = []

    
    for artigo in database:
        for autor in artigo.get("authors", []):
            if "affiliation" in autor and autor["affiliation"] not in afiliacoes:
                afiliacoes.append(autor["affiliation"])

    layout = [
        [sg.Text("Digite a afiliação ou selecione abaixo:")],
        [sg.Input(key="-SEARCH-", enable_events=True)],
        [sg.Listbox(values=afiliacoes, size=(50, 10), key="-AFILIACOES-", enable_events=True)],
        [sg.Button("Pesquisar"), sg.Button("Fechar")]
    ]

    window = sg.Window("Consulta por Afiliação", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Fechar":
            break

        if event == "-SEARCH-":
            search_text = values["-SEARCH-"].lower()
            filtered_afiliacoes = [a for a in afiliacoes if search_text in a.lower()]
            window["-AFILIACOES-"].update(values=filtered_afiliacoes)

        if event == "Pesquisar":
            selected = values["-AFILIACOES-"]
            if not selected:
                sg.popup("Nenhuma afiliação selecionada!")
                continue
            afiliacao_selecionada = selected[0]
            artigos = [
                artigo for artigo in database
                if any(a.get("affiliation", "").lower() == afiliacao_selecionada.lower() for a in artigo.get("authors", []))
            ]
            if artigos:
                detalhes = "\n\n".join(
                    f"Título: {artigo.get('title', 'N/A')}\n"
                    f"Resumo: {artigo.get('abstract', 'N/A')}\n"
                    f"Palavras-chave: {', '.join(artigo.get('keywords', [])) if isinstance(artigo.get('keywords'), list) else artigo.get('keywords', 'N/A')}\n"
                    f"DOI: {artigo.get('doi', 'N/A')}\n"
                    f"PDF: {artigo.get('pdf', 'N/A')}\n"
                    f"Data de Publicação: {artigo.get('publish_date', 'N/A')}\n"
                    f"URL: {artigo.get('url', 'N/A')}\n"
                    for artigo in artigos
                )

                sg.popup_scrolled(detalhes, title="Detalhes do Artigo", size=(60, 20))
            else:
                sg.popup("Nenhum artigo encontrado para esta afiliação!")
    window.close()
def consulta_por_data(json_file):
    database = carrega_data(json_file)
    layout = [
        [sg.Text('Digite a data de publicação (YYYY-MM-DD):'), sg.InputText(key='-DATE-')],
        [sg.Button('Buscar'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Consulta por Data', layout)

    while True:
        event, values = window.read()

        if event == 'Buscar':
            data_procurada = values['-DATE-'].strip()  
            resultados = [
                artigo for artigo in database
                if 'publish_date' in artigo and artigo['publish_date'] == data_procurada
            ]
            if resultados:
                
                artigos_layout = [
                    [sg.Text(f"Artigos publicados em {data_procurada}:")],
                    [sg.Listbox(values=[artigo.get('title', 'N/A') for artigo in resultados], size=(50, 10), key='-ARTIGOS-', enable_events=True)],
                    [sg.Button('Visualizar'), sg.Button('Voltar')]
                ]

                artigos_window = sg.Window('Selecionar Artigo', artigos_layout)

                while True:
                    artigos_event, artigos_values = artigos_window.read()

                    if artigos_event == sg.WINDOW_CLOSED or artigos_event == 'Voltar':
                        break

                    if artigos_event == 'Visualizar':
                        selected_artigo = artigos_values['-ARTIGOS-']
                        if not selected_artigo:
                            sg.popup('Nenhum artigo selecionado!')
                            continue

                        
                        artigo_selecionado = next(artigo for artigo in resultados if artigo.get('title') == selected_artigo[0])

                        
                        detalhes = [
                            f"Título: {artigo_selecionado.get('title', 'N/A')}",
                            f"Resumo: {artigo_selecionado.get('abstract', 'N/A')}",
                            f"Palavras-chave: {', '.join(artigo_selecionado.get('keywords', '').split(', ')) if isinstance(artigo_selecionado.get('keywords', ''), str) else 'N/A'}",
                            f"DOI: {artigo_selecionado.get('doi', 'N/A')}",
                            f"PDF: {artigo_selecionado.get('pdf', 'N/A')}",
                            f"Data de Publicação: {artigo_selecionado.get('publish_date', 'N/A')}",
                            f"URL: {artigo_selecionado.get('url', 'N/A')}"
                        ]
                        sg.popup_scrolled("\n\n".join(detalhes), title="Detalhes do Artigo", size=(60, 20))

                artigos_window.close()
            else:
                sg.popup('Nenhum artigo encontrado para esta data.')
        elif event == 'Cancelar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
def consulta_por_palavras_chave(json_file):
    database = carrega_data(json_file)
    layout = [
        [sg.Text('Digite a palavra-chave:'), sg.InputText(key='-KEYWORD-')],
        [sg.Button('Buscar'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Consulta por Palavras-chave', layout)

    while True:
        event, values = window.read()

        if event == 'Buscar':
            palavra_chave = values['-KEYWORD-'].lower()

            resultados = [
                artigo for artigo in database 
                if 'keywords' in artigo 
                and (isinstance(artigo['keywords'], list) or isinstance(artigo['keywords'], str)) 
                and palavra_chave in (kw.lower() for kw in (artigo['keywords'] if isinstance(artigo['keywords'], list) else artigo['keywords'].split(', ')))
            ]

            if resultados:
                resultados_layout = [
                    [sg.Text(f"Resultados para: '{palavra_chave}'")],
                    [sg.Listbox(values=[artigo['title'] for artigo in resultados], size=(60, 15), key='-RESULTADOS-', enable_events=True)],
                    [sg.Button('Selecionar Artigo'), sg.Button('Voltar')]
                ]

                resultados_window = sg.Window('Resultados da Consulta', resultados_layout)

                while True:
                    resultados_event, resultados_values = resultados_window.read()

                    if resultados_event == sg.WINDOW_CLOSED or resultados_event == 'Voltar':
                        break

                    if resultados_event == 'Selecionar Artigo':
                        selected_artigo = resultados_values['-RESULTADOS-']
                        if not selected_artigo:
                            sg.popup("Nenhum artigo selecionado!")
                            continue
                        
                        artigo_selecionado = next(artigo for artigo in resultados if artigo['title'] == selected_artigo[0])

                        
                        detalhes = (
                            f"Título: {artigo_selecionado.get('title', 'N/A')}\n\n"
                            f"Resumo: {artigo_selecionado.get('abstract', 'N/A')}\n\n"
                            f"Palavras-chave: {', '.join(artigo_selecionado.get('keywords', [])) if isinstance(artigo_selecionado.get('keywords', []) , list) else artigo_selecionado.get('keywords', 'N/A')}\n\n"  # Formata as palavras-chave
                            f"DOI: {artigo_selecionado.get('doi', 'N/A')}\n\n"
                            f"PDF: {artigo_selecionado.get('pdf', 'N/A')}\n\n"
                            f"Data de Publicação: {artigo_selecionado.get('publish_date', 'N/A')}\n\n"
                            f"URL: {artigo_selecionado.get('url', 'N/A')}"
                        )
                        sg.popup_scrolled(detalhes, title="Detalhes do Artigo", size=(60, 20))

                resultados_window.close()
            else:
                sg.popup('Nenhum artigo encontrado com esta palavra-chave.')

        elif event == 'Cancelar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
def remover_publicacao_window(json_file):
    database = carrega_data(json_file)
    
    if not database:
        sg.popup('Nenhuma publicação encontrada para remover!')
        return

    publicacoes_com_titulo = [pub['title'] for pub in database if 'title' in pub]

    if not publicacoes_com_titulo:
        sg.popup('Nenhuma publicação válida encontrada!')
        return

    layout = [ 
        [sg.Text('Filtro por Título'), sg.InputText(key='-TITLE-', enable_events=True)],
        [sg.Text('Selecione uma publicação para remover:', font=('Helvetica', 14))],
        [sg.Listbox(values=publicacoes_com_titulo, size=(50, 10), key='-PUBLICATIONS-')],
        [sg.Button('Remover'), sg.Button('Cancelar')]
    ]
    window = sg.Window('Remover Publicação', layout)

    while True:
        event, values = window.read()

        if event == '-TITLE-':
            search_text = values['-TITLE-'].lower()
            filtered_publicacoes = [pub for pub in publicacoes_com_titulo if search_text in pub.lower()]
            window['-PUBLICATIONS-'].update(values=filtered_publicacoes)

        elif event == 'Remover':
            selected = values['-PUBLICATIONS-']
            if selected:
                titulo = selected[0]
                database = [artigo for artigo in database if artigo.get('title') != titulo]
                atualiza_data(json_file, database)
                sg.popup(f'Publicação "{titulo}" removida com sucesso!')
                break

        elif event == 'Cancelar' or event == sg.WINDOW_CLOSED:
            break

    window.close()
def autores_window():
    autores = []
    while True:
        autor_layout = [
            [sg.Text('Nome do Autor'), sg.InputText(key='-AUTHOR-')],
            [sg.Text('Afiliação'), sg.InputText(key='-AFFILIATION-')],
            [sg.Button('Adicionar'), sg.Button('Concluir')]
        ]
        autor_window = sg.Window('Adicionar Autores', autor_layout)
        event, values = autor_window.read()
        if event == 'Adicionar':
            if values['-AUTHOR-'] and values['-AFFILIATION-']:
                autores.append({"name": values['-AUTHOR-'], "affiliation": values['-AFFILIATION-']})
                sg.popup("Autor adicionado com sucesso!")
            else:
                sg.popup("Por favor, preencha todos os campos!")
        elif event == 'Concluir' or event == sg.WINDOW_CLOSED:
            autor_window.close()
            break
        autor_window.close()
    return autores
def criar_publicacao_window(json_file):
    layout = [
        [sg.Text('Título'), sg.InputText(key='-TITLE-')],
        [sg.Text('Resumo'), sg.Multiline(size=(80, 15), key='-ABSTRACT-')],
        [sg.Text('Palavras-chave (separadas por vírgulas)'), sg.InputText(key='-KEYWORDS-')],
        [sg.Text('DOI'), sg.InputText(key='-DOI-')],
        [sg.Text('Data de Publicação (AAAA-MM-DD)'), sg.InputText(key='-DATE-')],
        [sg.Text('URL do PDF'), sg.InputText(key='-PDF-')],
        [sg.Text('URL do Artigo'), sg.InputText(key='-ARTICLEURL-')],
        [sg.Column([[sg.Button('Adicionar Autores'), sg.Button('Guardar'), sg.Button('Cancelar')]], justification='center')]
    ]
    window = sg.Window('Criar Publicação', layout,)

    autores = []
    while True:
        event, values = window.read()
        if event == 'Adicionar Autores':
            autores = autores_window()
        elif event == 'Guardar':
            if not values['-TITLE-']: 
                sg.popup('O título é obrigatório!')
                continue
            if not verificarformatodata(values['-DATE-']):
                sg.popup('A data deve ser válida e estar no formato AAAA-MM-DD, até á data 2024-12-31!')
                continue
            
            database = carrega_data(json_file)
            keywords = values['-KEYWORDS-'].strip()
            
            publicacao = {
                "title": values['-TITLE-'],
                "abstract": values['-ABSTRACT-'],
                "keywords": keywords,  
                "doi": values['-DOI-'],
                "pdf": values['-PDF-'],
                "publish_date": values['-DATE-'],
                "url": values['-ARTICLEURL-'],
                "authors": autores
            }
            
            database.append(publicacao)
            atualiza_data(json_file, database)
            sg.popup('Publicação guardada com sucesso!')
        elif event == 'Cancelar' or event == sg.WINDOW_CLOSED:
            break
    window.close()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bd_artigos = os.path.join(script_dir, "ata_medica_papers.json")

    layout = [
        [sg.Push(), sg.Text('Bem Vindo ao', font=('Helvetica', 20)), sg.Push()],
        [sg.Push(), sg.Text('Search Academy!', font=('Helvetica', 24,'bold italic')), sg.Push()],
        [sg.Push(), sg.Text('Selecione uma opção abaixo:', font=('Helvetica', 14)), sg.Push()],
        [sg.Column(
            [
                [sg.Button('Criar Publicação', size=(30, 2))],
                [sg.Button('Listar Publicações', size=(30, 2))],
                [sg.Button('Consulta', size=(30, 2))],
                [sg.Button('Remover Publicação', size=(30, 2))],
                [sg.Button('Estatísticas de Publicação', size=(30, 2))],
                [sg.Button('Sair', size=(30, 2))]
            ],
            justification='center', element_justification='center'
        )]
    ]

    window = sg.Window('Gerenciador de Publicações', layout, size=(400, 440), element_justification='center')

    while True:
        event, _ = window.read()
        if event == 'Criar Publicação':
            criar_publicacao_window(bd_artigos)
        elif event == 'Listar Publicações':
            listar_publicacoes_window(bd_artigos)
        elif event == 'Consulta':
            consulta_window(bd_artigos)
        elif event == 'Remover Publicação':
            remover_publicacao_window(bd_artigos)
        elif event == 'Estatísticas de Publicação':
            escolher_estatistica(bd_artigos)
        elif event == 'Sair' or event == sg.WINDOW_CLOSED:
            break
    window.close()

def carrega_data(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [pub for pub in data if 'title' in pub]  
    except (FileNotFoundError, json.JSONDecodeError):
        return []
def atualiza_data(json_file, data):
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return '\n\033[4m\033[1mInformação salva com sucesso\033[0m'
def carrega_novadata(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            novadata = json.load(file)
        return [pub for pub in novadata if 'title' in pub] 
    except (FileNotFoundError, json.JSONDecodeError):
        return []
def verificaestrutura(data,novadata):#verifica se está numa lista
    if isinstance(data, list) and isinstance(novadata, list):
        return True
    else:
        raise ValueError("\n\033[1mA estrutura dos dados não é compatível.\033[0m")
def unir_dados(data, novadata):
    data.extend(novadata)
    return data
def importardados(ficheiroexistente,novoficheiro):
    data=carrega_data(ficheiroexistente)
    novadata=carrega_novadata(novoficheiro)
    verificaestrutura(data,novadata)
    newinfo=unir_dados(data,novadata)
    atualiza_data(ficheiroexistente,newinfo)
    return "\n\033[1mDados importados com sucesso\033[0m"
def pesquisardados(data):
    resultados = []
    N=int(input("\nInsira o \033[1mnúmero\033[0m de artigos que pretende exportar:"))
    if N <= 0:
            return "\033[1mPor favor, insira um número positivo.\033[0m"
    while N>0:
        DOI=str(input("\nInsira o \033[1mdoi\033[0m dos artigos que pretende exportar:\n"))
        encontrado = False
        for artigo in data:
            if artigo["doi"]==DOI:
                if artigo not in resultados:
                    resultados.append(artigo)
                encontrado = True
        if encontrado:
                print("\033[1mArtigo adicionado aos resultados.\033[0m")
        else:
                print("\033[1mDOI não encontrado.\033[0m")
        N = N-1
                 
    return resultados
def exportarpesquisa(caminhoficheiro, resultados):#acrescentar os dados no ficheiro pretendido
    with open(caminhoficheiro, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
def exportardadosparciais(ficheiroexistente, caminhoficheiro):  
    data3 = carrega_data(ficheiroexistente)# guardar a informação do ficheiro já existente
    data4=carrega_data(caminhoficheiro) #guardar informação do novo ficheiro
    pesquisa = pesquisardados(data3) #executando a função pesquisa selecionamos os dados que queremos exportar
    newinfo=unir_dados(data4,pesquisa) #juntar os dados da pesquisa com os dados do ficheiro para a qual vamos exportar para não se perder informação
    exportarpesquisa(caminhoficheiro, newinfo) #dump
    
    return "\033[1mDados exportados com sucesso.\033[0m"
def autores():
    listaautores=[]
    dicautor={}
    numautores=input("Insira o \033[1mnúmero\033[0m de autores do seu artigo:")
    if numautores.isdigit():
        numautores=int(numautores)
        while numautores>0:
            autor=str(input("Insira o \033[1mNOME\033[0m do \033[1mautor\033[0m:"))
            afiliacao=str(input("Insira a \033[1mAFILIAÇÃO\033[1m do respetivo \033[1mautor\033[0m:"))
            dicautor={
                "name":autor,
                "affiliation":afiliacao
            }
            listaautores.append(dicautor)
            numautores -=1
    elif numautores=="":
        print("Estes artigo não terá autores.")
        return listaautores
    else:
        print("O valor inserido deve ser um número!")
        return listaautores

    return listaautores
def criapublicacao(titulo,resumo,palavraschave,DOI,autors,pdfurl,data,artigourl):
    database=carrega_data(bd_artigos)
    if verificarformatodata(data)==False:
        return f"\n\033[1mO formato de data inserido não é aceite.\n\nDeve ser do tipo: XXXX-XX-XX, sendo que os X's apenas tomam os valores inteiros possíveis de cada mês.\033[0m"
    else:
        diccriado={
            "abstract": resumo,
            "keywords": palavraschave,
            "authors": autors,
            "doi":DOI,
            "pdf":pdfurl,
            "publish_date":data,
            "title":titulo,
            "url":artigourl
        }
    database.append(diccriado)
    atualiza_data(bd_artigos, database)
    return f"\n\033[1mPublicação adicionada com sucesso.\033[0m"

def consultaautor():
    database=carrega_data(bd_artigos)
    listaartigos=[]
    procura=str(input("Insira o \033[1mNOME do AUTOR\033[0m do artigo que procura:"))
    for artigo in database:
            for author in artigo["authors"]:
                if author["name"]==procura:
                    listaartigos.append(artigo)
    for e in listaartigos:
        for chave,valor in e.items():
            print(f"\033[1m{chave}\033[0m : {valor}")
    return listaartigos                  
def consultatitulo():
    database=carrega_data(bd_artigos)
    procura=str(input("Insira o \033[1mTÍTULO\033[0m do artigo que procura:"))
    for artigo in database:
        if 'title' in artigo and artigo["title"]==procura:
            for chave,valor in artigo.items():
                print(f"\033[1m{chave}\033[0m : {valor}")
            return artigo
    return "Artigo não encontrado"
def consultaafiliacao():
    database=carrega_data(bd_artigos)
    listaartigos=[]
    procura=str(input("Insira a \033[1mAFILIAÇÃO\033[0m que procura:"))
    for artigo in database:
        for author in artigo["authors"]:
            if 'affiliation' in author and author["affiliation"]==procura:
                listaartigos.append(artigo)
    for e in listaartigos:
        for chave,valor in e.items():
            print(f"\033[1m{chave}\033[0m : {valor}")
    return listaartigos
def consultadata():
    database=carrega_data(bd_artigos)
    listaartigos=[]
    procura=str(input("Insira a \033[1mDATA\033[0m do artigo que está á procura:"))
    for artigo in database:
        if 'publish_date' in artigo and artigo["publish_date"]==procura:
            listaartigos.append(artigo)
    for e in listaartigos:
        for chave,valor in e.items():
            print(f"\033[1m{chave}\033[0m : {valor}")
    return listaartigos
def consultapalchav():
    database=carrega_data(bd_artigos)
    listaartigo=[]
    procura=str(input("Insira a \033[1mPALAVRAS-CHAVE\033[0m que procura:\n"))
    
    for artigo in database:
        if "keywords" in artigo:
            keywords = [kw.strip() for kw in artigo['keywords'].split(',') if kw.strip()]
            if procura in keywords:
                listaartigo.append(artigo)
    
    if listaartigo:
        for e in listaartigo:
            print("\n\033[1mArtigo encontrado:\033[0m")
            for chave,valor in e.items():
                print(f"\033[1m{chave}\033[0m : {valor}")
    
    else:
        print("\n\033[1mNenhum artigo encontrado com essa palavra-chave.\033[0m")
    
    return listaartigo
def removepublicacao(titulo):
    database=carrega_data(bd_artigos)
    database_filtrado = [artigo for artigo in database if 'title' in artigo and artigo['title'] != titulo]
    if len(database_filtrado) == len(database):
        return f"\033[1mNenhuma\033[0m publicação \033[1mencontrada\033[0m com o título \033[1m'{titulo}'\033[0m"
    print(atualiza_data(bd_artigos,database_filtrado))
    return f"Publicação removida com sucesso."
def consultapublicacao(titulo):
    listaartigos=[]
    database=carrega_data(bd_artigos)
    for artigo in database:
        if 'title' in artigo and artigo["title"]==titulo:
            listaartigos.append(artigo)
    for e in listaartigos:
        for chave,valor in e.items():
            print(f"\033[1m{chave}\033[0m : {valor}")
    return f"Foram encontrados \033[1m{len(listaartigos)}\033[0m artigos:\n", listaartigos
def estatisticapalchav():
    database=carrega_data(bd_artigos)
    keywords_count = {}
    
    for artigo in database:
        keywords = artigo.get("keywords", "")
        if keywords:
            keywords_list = keywords.split(", ")
            for keyword in keywords_list:
                if keyword in keywords_count:
                    keywords_count[keyword] += 1
                else:
                    keywords_count[keyword] = 1
    for chave,valor in keywords_count.items():
        print(f'\033[1m{chave}\033[0m:{valor}')

    return keywords_count
def estatisticapubautor():
    database=carrega_data(bd_artigos)
    dicionario_autores = {}

    for artigo in database:
        for autor in artigo["authors"]:
            nome_autor = autor["name"]
            if nome_autor in dicionario_autores:
                dicionario_autores[nome_autor] += 1
            else:
                dicionario_autores[nome_autor] = 1

    for chave,valor in dicionario_autores.items():
        print(f'\033[1m{chave}\033[0m:{valor}')

    return dicionario_autores
def estatisticapubano():
    database=carrega_data(bd_artigos)
    dicionario_data={}
    for artigo in database:
        if 'publish_date' in artigo:
            data=artigo["publish_date"][:4]
            if data in dicionario_data:
                 dicionario_data[data] += 1
            else:
                 dicionario_data[data] = 1
    for chave,valor in dicionario_data.items():
        print(f'\033[1m{chave}\033[0m:{valor}')
 
    return dicionario_data
def atualizapublicacoes():
    database=carrega_data(bd_artigos)
    a1=str(input("\nInsira o \033[1mDOI\033[0m do artigo que pretende alterar:"))
    for artigo in database:
        if artigo["doi"]==a1:
            for chave,valor in artigo.items():
                print(f"\033[1m{chave}\033[0m : {valor}")
            a2=str(input("\nInsira o que pretende alterar:\n 1-\033[1mPalavras-chave\033[0m\n 2-\033[1mResumo\033[0m\n 3-\033[1mData de publicação\033[0m\n 4-\033[1mAutores\033[0m\n 5-\033[1mAfiliações\033[0m"))
            if a2=="1":
                keywords=str(input("Insira o que \033[1mpretende ter como palavras-chave\033[0m deste artigo:"))
                artigo["keywords"]=keywords
                atualiza_data(bd_artigos, database)
                for chave,valor in artigo.items():
                    print(f"\033[1m{chave}\033[0m : {valor}")
                return f"\033[1m\nPublicação atualizada com sucesso.\033[0m"


            if a2=="2":
                resumo=str(input("\nInsira o que \033[1mpretende ter como resumo\033[0m deste artigo:"))
                artigo["abstract"]=resumo
                atualiza_data(bd_artigos, database)
                for chave,valor in artigo.items():
                    print(f"\033[1m{chave}\033[0m : {valor}")
                return f"\n\033[1mPublicação atualizada com sucesso.\033[0m"

            if a2=="3":
                data=str(input("\nInsira a \033[1mnova data\033[0m da sua publicação:"))
                if verificarformatodata(data)==True:
                    artigo["publish_date"]=data
                    atualiza_data(bd_artigos, database)
                    for chave,valor in artigo.items():
                        print(f"\033[1m{chave}\033[0m : {valor}")   
                    return "\033[1m\nPublicação atualizada com sucesso\033[0m"
                else:
                    return "A data inserida não está no formato adequado."

            if a2=="4":
                a3=str(input("\nQual é \033[1mo autor que quer alterar?\033[0m"))
                found=False
                for autor in artigo["authors"]:
                    if autor["name"]==a3:
                        novoautor=str(input("\nInsira o \033[1mnovo autor\033[0m:"))
                        autor["name"]=novoautor
                        atualiza_data(bd_artigos, database)
                        found=True
                        for chave,valor in artigo.items():
                            print(f"\033[1m{chave}\033[0m : {valor}")
                        return f"\n\033[1mPublicação atualizada com sucesso.\033[1m"
                if not found:
                        return f"\nEsse autor \033[1mnão está presente\033[0m neste artigo."
            if a2=="5":
                a4=str(input("\nPretende \033[1malterar as afiliações\033[1m de que \033[1mautor?\033[0m"))
                found=False
                for autor in artigo["authors"]:
                    if autor["name"]==a4:
                        novaafiliacao=str(input("\nInsira a \033[1mnova afiliação\033[0m do autor escolhido:"))
                        autor["affiliation"]=novaafiliacao
                        atualiza_data(bd_artigos, database)
                        found=True
                        for chave,valor in artigo.items():
                            print(f"\033[1m{chave}\033[0m : {valor}")
                        return f"\033[1m\nPublicação atualizada com sucesso.\033[0m"
                if not found:
                        return f"\033[1m\nEsse autor não está presente neste artigo.\033[0m"
            else:
                return f"\033[1m\nEssa opção não exist.\033[0me"
            
        
    return f"\033\n[1mNão existe nenhuma publicação com esse DOI na nossa base de dados.\033[0m"
def listarautores():
    listaautores=[]
    listaartigos=[]

    database=carrega_data(bd_artigos)
    for artigo in database:
        for author in artigo["authors"]:
            if author["name"] not in listaautores:
                listaautores.append(author["name"])
    for autor in listaautores:
        print(f"{autor}")
    
    escolha=str(input("Insira o nome do autor que pretende consultar:\n"))
    for e in listaautores:
        if e == escolha:
            for artigo in database:
                for author in artigo["authors"]:
                    if author["name"]==e:
                        listaartigos.append(artigo)

    for a in listaartigos:
        for chave,valor in a.items():
            print(f"\033[1m{chave}\033[0m : {valor}")

    return listaartigos
def menu():
    print("\n\033[1m------------------\033[4mBem-Vindo á Search Academy\033[0m\033[1m------------------\033[0m\n\n        Se deseja aceder á aplicação use o comando \033[4m\033[1mHelp\033[0m\n        Se deseja sair escreva o comando \033[4m\033[1mLeave\033[0m\n")
    res=input(" Insira o comando desejado:\n--->")
    if res=="Help":
        res1=0 
        while res!=11: 
        
            print("\033[1m\n\n\n-------------------------------- Que operação pretende realizar? --------------------------------\033[0m\n\n1-\033[1mCriar publicação\033[0m               2-\033[1mConsultar publicações\033[0m               3-\033[1mConsultar uma publicação\033[0m\n\n4-\033[1mEliminar uma publicação\033[0m        5-\033[1mRelatório de Estatísticas\033[0m           6-\033[1mListar Autores\033[0m\n\n7-\033[1mImportar artigos\033[0m               8-\033[1mExportar artigos\033[0m                    9-\033[1mInterface Gráfica\033[0m\n\n10-\033[1mAtualizar publicações\033[0m         11-\033[1mLeave\033[0m")
            res1=input("\nQue funcionalidade pretendes usar?\n")
            if res1=="1":
                titulo=str(input("Insira o \033[1mTÍTULO\033[0m do artigo:"))
                resumo=str(input("Insira o \033[1mRESUMO\033[0m do seu artigo:"))
                palavraschave=str(input("Insira as \033[1mPALAVRAS-CHAVE\033[0m do seu artigo, \033[1mseparando-as com virgulas\033[0m:"))
                DOI=str(input("Insira o \033[1mDOI\033[0m do seu artigo:"))
                autors = autores()
                pdfurl=str(input("Insira o \033[1mLINK DO PDF:\033[0m"))
                data=str(input("Insira a \033[1mDATA\033[0m da publicação:"))
                artigourl=str(input("Insira o \033[1mLINK\033[0m do artigo:"))
                
                return print(criapublicacao(titulo,resumo,palavraschave,DOI,autors,pdfurl,data,artigourl)),menu()

            elif res1=="2":
                filtro=input("Pretende usar que \033[1mFILTRO\033[0m? \n 1-\033[1mTÍTULO\033[0m \n 2-\033[1mAUTOR\033[0m \n 3-\033[1mAFILIAÇÃO\033[0m \n 4-\033[1mDATA\033[0m \n 5-\033[1mPALAVRAS-CHAVE\033[0m")
                if filtro=="1":
                    consultatitulo()
                    return menu()

                if filtro=="2":
                    consultaautor()
                    return menu()

                if filtro=="3":
                    consultaafiliacao()
                    return menu()

                if filtro=="4":
                    consultadata()
                    return menu()

                if filtro=="5":
                    consultapalchav()
                    return menu()

                else:
                    print("\n\nEsse filtro não existe!")
                    return menu()

            elif res1=="3":
                titulo=str(input("Insira o \033[1mTÍTULO\033[0m da publicação que procura:\n"))
                consultapublicacao(titulo)
                menu()

            elif res1=="4":
                titulo=str(input("Insira o \033[1mTÍTULO\033[0m da publicação a remover\n"))
                print(removepublicacao(titulo))
                menu()

            
            elif res1=="5":
                relatorio=str(input("Insira o \033[1mRELATÓRIO\033[0m que pretende:\n 1-Relatório da \033[1mfrequência de palavras-chave\033[0m\n 2-Relatório do \033[1mnúmero de publicações por autor\033[0m\n 3-Relatório de \033[1mpublicações por ano\033[0m"))
                if relatorio=="1":
                    estatisticapalchav()
                    menu()
                if relatorio=="2":
                    estatisticapubautor()
                    menu()
                if relatorio=="3":
                    estatisticapubano()
                    menu()
                if relatorio=="4":
                    menu()
                else:
                    return "\n\n\033[1mEssa opção não existe experimente outra\033[0m"

            elif res1=="6":
                listarautores()
                menu()

            elif res1=="7":
                novoficheiro=str(input("Insira o \033[1mnome do ficheiro\033[0m que quer \033[1mimportar\033[0m:"))
                print(importardados(ficheiroexistente,novoficheiro))
                menu()

            elif res1=="8":
                caminhoficheiro=str(input("Insira o \033[1mnome do ficheiro\033[0m para qual pretende \033[1mexportar\033[0m:"))
                print(exportardadosparciais(ficheiroexistente,caminhoficheiro))
                menu()
            elif res1 == "9":
                print("\033[1mAbrindo a interface gráfica...\033[0m")
                main()
            elif res1=="10":
                print(atualizapublicacoes())
                menu()
            elif res1=="11":
                print("Obrigado por ter utilizado a Search Academy")
                return print(ascii_art()),print("\n\033[1m-----------------------------------Até já-----------------------------------\033[0m\n\n")
            else:
                print("Comando não reconhecido, tente novamente!")

    elif res=="Leave":
            return print(ascii_art()),print("\n\033[1m-----------------------------------Até já-----------------------------------\033[0m\n\n")

    else:
            print("\n\n\033[4m\033[1mComando não reconhecido, tente outra vez\033[0m\n")
            menu()

menu()