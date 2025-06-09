import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Variáveis Globais ---
codigos = []
nomes = []
precos = []
pasta_imagens = ""

# --- Funções de Log e de Busca de Imagens ---

# Log
arquivo_log = "log_execucao.txt"
def escrever_log(mensagem):
    """Escreve uma mensagem com data e hora no arquivo de log."""
    with open(arquivo_log, "a", encoding="utf-8") as log:
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{hora}] {mensagem}\n")

def mapear_imagens_por_codigo(pasta):
    """
    Escaneia a pasta de imagens e cria um dicionário onde cada chave é um
    código base e o valor é uma lista ordenada dos caminhos de imagem.
    Ex: {'12345': ['caminho/12345-1.jpg', 'caminho/12345-2.jpg']}
    """
    mapa_imagens = {}
    if not os.path.isdir(pasta):
        escrever_log(f"AVISO: A pasta de imagens '{pasta}' não foi encontrada ou não é um diretório.")
        return mapa_imagens

    for nome_arquivo in os.listdir(pasta):
        # Ignora arquivos que não são de imagem (pode ajustar as extensões)
        if not nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue

        # Extrai o nome do arquivo sem a extensão
        nome_sem_ext = os.path.splitext(nome_arquivo)[0]
        
        # Tenta extrair o código base (parte antes do último hífen)
        if '-' in nome_sem_ext:
            codigo_base = nome_sem_ext.rsplit('-', 1)[0]
        else:
            codigo_base = nome_sem_ext

        caminho_completo = os.path.normpath(os.path.join(pasta, nome_arquivo))

        # Se o código base ainda não está no mapa, cria uma lista para ele
        if codigo_base not in mapa_imagens:
            mapa_imagens[codigo_base] = []
        
        mapa_imagens[codigo_base].append(caminho_completo)

    # Garante que as listas de imagens estejam ordenadas para cada código
    # Isso é crucial para pegar -1, -2, -3 na ordem correta.
    for codigo in mapa_imagens:
        mapa_imagens[codigo].sort()
        
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
            # Lê as linhas e remove espaços em branco/quebras de linha extras
            linhas = [linha.strip() for linha in f if linha.strip()]
            
            if tipo == "códigos":
                codigos = linhas
            elif tipo == "nomes":
                nomes = linhas
            elif tipo == "preços":
                precos = linhas
                
        escrever_log(f"{tipo.capitalize()} carregados com sucesso do arquivo: {caminho}")
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
        escrever_log(f"Pasta de imagens selecionada: {pasta}")
        messagebox.showinfo("Sucesso", f"Pasta de imagens selecionada:\n{pasta}")

def gerar_csv():
    """Função principal que gera o arquivo CSV final."""
    # Validações iniciais
    if not (codigos and nomes and precos):
        messagebox.showwarning("Aviso", "Por favor, carregue os arquivos de códigos, nomes e preços antes de gerar o CSV.")
        return
    if not pasta_imagens:
        messagebox.showwarning("Aviso", "Por favor, selecione a pasta de imagens.")
        return
    if not (len(codigos) == len(nomes) == len(precos)):
        messagebox.showerror("Erro de Dados", f"As listas têm tamanhos diferentes!\n"
                                              f"Códigos: {len(codigos)}\n"
                                              f"Nomes: {len(nomes)}\n"
                                              f"Preços: {len(precos)}")
        return

    arquivo_csv = "produtos_com_caminhos.csv"
    escrever_log("Iniciando geração do CSV...")

    # 1. Mapeia todas as imagens da pasta ANTES de iniciar o loop
    mapa_de_imagens = mapear_imagens_por_codigo(pasta_imagens)
    escrever_log(f"Mapeadas {sum(len(v) for v in mapa_de_imagens.values())} imagens em {len(mapa_de_imagens)} códigos base.")

    # 2. Cria um contador para rastrear o uso de cada código repetido
    contagem_uso_codigos = {}

    try:
        with open(arquivo_csv, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["Código", "Nome", "Preço", "@Imagem"])

            for codigo, nome, preco in zip(codigos, nomes, precos):
                
                # Pega o índice da imagem a ser usada para este código (0 para a primeira vez, 1 para a segunda, etc.)
                indice_da_imagem = contagem_uso_codigos.get(codigo, 0)
                
                caminho_final = "Imagem não encontrada"

                # Verifica se o código existe no nosso mapa de imagens
                if codigo in mapa_de_imagens:
                    # Verifica se ainda há imagens disponíveis para este índice
                    if indice_da_imagem < len(mapa_de_imagens[codigo]):
                        caminho_final = mapa_de_imagens[codigo][indice_da_imagem]
                        escrever_log(f"Para o código {codigo} (ocorrência {indice_da_imagem + 1}), encontrou: {caminho_final}")
                    else:
                        escrever_log(f"AVISO: Código {codigo} repetido, mas não há mais imagens (solicitada a {indice_da_imagem + 1}ª, mas só existem {len(mapa_de_imagens[codigo])}).")
                else:
                    escrever_log(f"AVISO: Nenhuma imagem encontrada para o código base: {codigo}")

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
    janela.title("Gerador de CSV de Produtos v2.0")
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