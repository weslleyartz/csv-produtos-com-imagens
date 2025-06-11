import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import re

# --- Variáveis Globais ---
codigos = []
nomes = []
precos = []
pasta_imagens = ""


# --- Funções de Log e de Busca de Imagens ---

arquivo_log = "log_execucao.txt"
def escrever_log(mensagem):
    """Escreve uma mensagem com data e hora no arquivo de log."""
    with open(arquivo_log, "a", encoding="utf-8") as log:
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{hora}] {mensagem}\n")

def mapear_imagens_por_codigo(pasta, lista_codigos_produtos):
    """
    Escaneia a pasta de imagens e cria um dicionário onde cada chave é um
    código de produto (da sua lista) e o valor é uma lista ordenada dos
    caminhos de imagem que começam com esse código.
    Ex: {'123456': ['caminho/123456.jpg', 'caminho/123456-1.jpg', 'caminho/123456-7-12.jpg']}
    """
    mapa_imagens = {codigo: [] for codigo in lista_codigos_produtos} # Inicializa com todos os códigos de produto
    escrever_log(f"Iniciando mapeamento de imagens na pasta: {pasta}")
    if not os.path.isdir(pasta):
        escrever_log(f"AVISO: A pasta de imagens '{pasta}' não foi encontrada ou não é um diretório.")
        return {} # Retorna um dicionário vazio se a pasta não existir

    for nome_arquivo in os.listdir(pasta):
        # Ignora arquivos que não são de imagem (pode ajustar as extensões)
        if not nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            escrever_log(f"IGNORANDO: '{nome_arquivo}' - não é um arquivo de imagem suportado.")
            continue

        # Extrai o nome do arquivo sem a extensão
        nome_sem_ext = os.path.splitext(nome_arquivo)[0]
        caminho_completo = os.path.normpath(os.path.join(pasta, nome_arquivo))

        # Tenta encontrar um código de produto que o nome do arquivo "comece"
        encontrado_para_codigo = False
        for codigo_produto in lista_codigos_produtos:
            # Verifica se o nome do arquivo (sem extensão) começa com o código do produto
            # E se o que vem depois do código é um hífen, um underscore, ou se não há nada (exata correspondência)
            if nome_sem_ext.startswith(codigo_produto):
                suffix_start_index = len(codigo_produto)
                
                # Se o nome do arquivo tem exatamente o tamanho do código (ex: "123456" para "123456.jpg")
                # OU se o caractere após o código é um hífen ou underscore
                if (len(nome_sem_ext) == suffix_start_index or
                    (suffix_start_index < len(nome_sem_ext) and 
                     (nome_sem_ext[suffix_start_index] == '-' or nome_sem_ext[suffix_start_index] == '_'))):
                    
                    mapa_imagens[codigo_produto].append(caminho_completo)
                    escrever_log(f"DEBUG: Mapeado arquivo '{nome_arquivo}' para código de produto '{codigo_produto}'.")
                    encontrado_para_codigo = True
                    break # Interrompe a busca por este nome de arquivo se já foi mapeado para um código
        
        if not encontrado_para_codigo:
            escrever_log(f"AVISO: Arquivo '{nome_arquivo}' não corresponde a nenhum código de produto na lista.")

    # Garante que as listas de imagens estejam ordenadas para cada código
    for codigo in mapa_imagens:
        mapa_imagens[codigo].sort()
        if mapa_imagens[codigo]: # Log apenas se houver imagens mapeadas
            escrever_log(f"DEBUG: Código '{codigo}' tem imagens mapeadas (ordenadas): {mapa_imagens[codigo]}")
        
    escrever_log(f"Mapeamento de imagens concluído. Total de códigos de produto com imagens encontradas: {sum(1 for v in mapa_imagens.values() if v)}")
    return mapa_imagens

# --- Funções da Interface ---

def carregar_txt(tipo):
    """Carrega dados de arquivos .txt para as listas globais."""
    caminho = filedialog.askopenfilename(title=f"Selecione o arquivo de {tipo}",
                                         filetypes=[("Arquivos de texto", "*.txt")])
    if not caminho:
        return
    
    global codigos, nomes, precos
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [linha.strip() for linha in f if linha.strip()]
            
            if tipo == "códigos":
                codigos.clear() 
                codigos.extend(linhas)
                escrever_log(f"VERIFICAR ESTADO: Após carregar códigos, len(codigos) = {len(codigos)}")
            elif tipo == "nomes":
                nomes.clear()
                nomes.extend(linhas)
                escrever_log(f"VERIFICAR ESTADO: Após carregar nomes, len(nomes) = {len(nomes)}")
            elif tipo == "preços":
                precos.clear()
                precos.extend(linhas)
                escrever_log(f"VERIFICAR ESTADO: Após carregar preços, len(precos) = {len(precos)}")
                
        escrever_log(f"{tipo.capitalize()} carregados com sucesso do arquivo: {caminho} ({len(linhas)} linhas)")
        messagebox.showinfo("Sucesso", f"{len(linhas)} {tipo} carregados com sucesso!")
    except Exception as e:
        escrever_log(f"Erro ao carregar o arquivo de {tipo}: {str(e)}")
        messagebox.showerror("Erro", f"Erro ao carregar {tipo}:\n{e}")

def escolher_pasta():
    """Permite ao usuário selecionar a pasta onde as imagens estão salvas."""
    global pasta_imagens
    pasta = filedialog.askdirectory(title="Selecione a pasta de imagens")
    if pasta:
        pasta_imagens = pasta
        escrever_log(f"VERIFICAR ESTADO: Pasta de imagens selecionada: {pasta}")
        messagebox.showinfo("Sucesso", f"Pasta de imagens selecionada:\n{pasta}")

def gerar_csv():
    """Função principal que gera o arquivo CSV final."""
    escrever_log("VERIFICAR ESTADO: Iniciando validação para gerar CSV.")
    escrever_log(f"VERIFICAR ESTADO: Estado atual das listas - Códigos: {len(codigos)}, Nomes: {len(nomes)}, Preços: {len(precos)}")
    escrever_log(f"VERIFICAR ESTADO: Pasta de imagens: '{pasta_imagens}'")

    # Validações iniciais
    if not (codigos and nomes and precos):
        messagebox.showwarning("Aviso", "Por favor, carregue os arquivos de códigos, nomes e preços antes de gerar o CSV.")
        escrever_log("AVISO: Tentativa de gerar CSV sem todos os arquivos carregados.")
        return
    if not pasta_imagens:
        messagebox.showwarning("Aviso", "Por favor, selecione a pasta de imagens.")
        escrever_log("AVISO: Tentativa de gerar CSV sem pasta de imagens selecionada.")
        return
    if not (len(codigos) == len(nomes) == len(precos)):
        messagebox.showerror("Erro de Dados", f"As listas têm tamanhos diferentes!\n"
                                             f"Códigos: {len(codigos)}\n"
                                             f"Nomes: {len(nomes)}\n"
                                             f"Preços: {len(precos)}")
        escrever_log(f"ERRO: Listas de dados com tamanhos diferentes - Códigos: {len(codigos)}, Nomes: {len(nomes)}, Preços: {len(precos)}")
        return

    arquivo_csv = "produtos_com_caminhos.csv"
    escrever_log("Iniciando geração do CSV...")

    # 1. Mapeia todas as imagens da pasta ANTES de iniciar o loop, passando a lista de códigos
    mapa_de_imagens = mapear_imagens_por_codigo(pasta_imagens, codigos)
    escrever_log(f"Mapeamento inicial concluído. {sum(len(v) for v in mapa_de_imagens.values())} imagens foram associadas a {len(mapa_de_imagens)} códigos de produto.")

    # 2. Cria um contador para rastrear o uso de cada código repetido
    contagem_uso_codigos = {}

    try:
        with open(arquivo_csv, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["Código", "Nome", "Preço", "@Imagem"])

            for i, (codigo, nome, preco) in enumerate(zip(codigos, nomes, precos)):
                escrever_log(f"PROCESSANDO Linha {i+1}: Código do TXT: '{codigo}'")
                
                # Pega o índice da imagem a ser usada para este código (0 para a primeira vez, 1 para a segunda, etc.)
                indice_da_imagem = contagem_uso_codigos.get(codigo, 0)
                
                caminho_final = "Imagem não encontrada" # Valor padrão se não encontrar a imagem

                # Verifica se o código existe no nosso mapa de imagens e se há imagens disponíveis para ele
                if codigo in mapa_de_imagens and mapa_de_imagens[codigo]:
                    escrever_log(f"DEBUG: Código '{codigo}' (do TXT) encontrado no mapa de imagens com {len(mapa_de_imagens[codigo])} imagens disponíveis.")
                    
                    # Verifica se ainda há imagens disponíveis para este índice
                    if indice_da_imagem < len(mapa_de_imagens[codigo]):
                        caminho_final = mapa_de_imagens[codigo][indice_da_imagem]
                        escrever_log(f"DEBUG: Para o código '{codigo}' (ocorrência {indice_da_imagem + 1}), utilizando imagem: '{caminho_final}'")
                    else:
                        escrever_log(f"AVISO: Código '{codigo}' repetido, mas não há mais imagens únicas (solicitada a {indice_da_imagem + 1}ª, mas só existem {len(mapa_de_imagens[codigo])} mapeadas).")
                else:
                    escrever_log(f"AVISO: Nenhuma imagem mapeada encontrada para o código do TXT: '{codigo}'.")

                writer.writerow([codigo, nome, preco, caminho_final])

                # Incrementa o contador para a próxima vez que este código aparecer
                contagem_uso_codigos[codigo] = indice_da_imagem + 1

        escrever_log("CSV gerado com sucesso.")
        messagebox.showinfo("Sucesso", f"Arquivo CSV gerado com sucesso:\n{os.path.abspath(arquivo_csv)}")
    except Exception as e:
        escrever_log(f"ERRO CRÍTICO ao gerar CSV: {str(e)}")
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro crítico ao gerar o CSV.\nConsulte o arquivo 'log_execucao.txt' para detalhes.")

# --- Configuração da Interface Gráfica com Tkinter ---
if __name__ == "__main__":
    janela = tk.Tk()
    janela.title("Gerador de CSV de Produtos v2.5 (Debug Final)") 
    janela.geometry("450x350")
    janela.resizable(False, False)

    # Frame principal para organizar os widgets
    frame = tk.Frame(janela, padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    # Título
    tk.Label(frame, text="Gerador de CSV para Produtos", font=("Helvetica", 16, "bold")).pack(pady=(0, 20))

    # Botões de Carregamento
    tk.Button(frame, text="1. Carregar Arquivo de Códigos", command=lambda: carregar_txt("códigos"), width=30).pack(pady=5)
    tk.Button(frame, text="2. Carregar Arquivo de Nomes", command=lambda: carregar_txt("nomes"), width=30).pack(pady=5)
    tk.Button(frame, text="3. Carregar Arquivo de Preços", command=lambda: carregar_txt("preços"), width=30).pack(pady=5)

    # Botão de Seleção de Pasta
    tk.Button(frame, text="4. Selecionar Pasta de Imagens", command=escolher_pasta, width=30).pack(pady=(15, 5))
    
    # Botão Principal de Ação
    tk.Button(frame, text="Gerar Arquivo CSV", bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), command=gerar_csv, width=30, height=2).pack(pady=(20, 10))

    # Iniciar a aplicação
    janela.mainloop()
