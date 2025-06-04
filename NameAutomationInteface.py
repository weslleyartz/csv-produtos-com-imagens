import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# Variáveis globais
codigos = []
nomes = []
precos = []
pasta_imagens = ""
extensao = ".png"

# Log
arquivo_log = "log_execucao.txt"
def escrever_log(mensagem):
    with open(arquivo_log, "a", encoding="utf-8") as log:
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{hora}] {mensagem}\n")

# Funções para carregar dados
def carregar_txt(tipo):
    caminho = filedialog.askopenfilename(title=f"Selecione o arquivo de {tipo}",
                                         filetypes=[("Arquivos de texto", "*.txt")])
    if not caminho:
        return
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [linha.strip() for linha in f.readlines()]
            if tipo == "códigos":
                global codigos
                codigos = linhas
            elif tipo == "nomes":
                global nomes
                nomes = linhas
            elif tipo == "preços":
                global precos
                precos = linhas
        escrever_log(f"{tipo.capitalize()} carregados com sucesso: {caminho}")
        messagebox.showinfo("Sucesso", f"{tipo.capitalize()} carregados com sucesso!")
    except Exception as e:
        escrever_log(f"Erro ao carregar {tipo}: {str(e)}")
        messagebox.showerror("Erro", f"Erro ao carregar {tipo}:\n{e}")

# Função para escolher pasta de imagens
def escolher_pasta():
    global pasta_imagens
    pasta = filedialog.askdirectory(title="Selecione a pasta de imagens")
    if pasta:
        pasta_imagens = pasta
        escrever_log(f"Pasta de imagens selecionada: {pasta}")
        messagebox.showinfo("Sucesso", f"Pasta de imagens selecionada:\n{pasta}")

# Função principal para gerar o CSV
def gerar_csv():
    if not (codigos and nomes and precos):
        messagebox.showwarning("Aviso", "Carregue todos os arquivos antes de gerar o CSV.")
        return
    if not pasta_imagens:
        messagebox.showwarning("Aviso", "Selecione a pasta de imagens.")
        return
    if len(codigos) != len(nomes) or len(codigos) != len(precos):
        messagebox.showerror("Erro", "As listas têm tamanhos diferentes.")
        return

    arquivo_csv = "produtos_com_caminhos.csv"
    escrever_log("Iniciando geração do CSV...")

    try:
        with open(arquivo_csv, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Código", "Nome", "Preço", "@Imagem"])

            for codigo, nome, preco in zip(codigos, nomes, precos):
                caminho_arquivo = os.path.join(pasta_imagens, codigo + extensao)
                if os.path.exists(caminho_arquivo):
                    caminho = caminho_arquivo
                    escrever_log(f"Imagem encontrada: {caminho}")
                else:
                    caminho = "Imagem não encontrada"
                    escrever_log(f"Imagem NÃO encontrada para código: {codigo}")
                writer.writerow([codigo, nome, preco, caminho])

        escrever_log("CSV gerado com sucesso.")
        messagebox.showinfo("Sucesso", f"CSV salvo com sucesso: {arquivo_csv}")
    except Exception as e:
        escrever_log(f"Erro ao gerar CSV: {str(e)}")
        messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o CSV.\nVeja o log.")

# Interface gráfica com Tkinter
janela = tk.Tk()
janela.title("Gerador de CSV de Produtos")
janela.geometry("400x300")

tk.Label(janela, text="Importar dados:").pack(pady=5)

tk.Button(janela, text="Carregar Códigos", command=lambda: carregar_txt("códigos")).pack(pady=5)
tk.Button(janela, text="Carregar Nomes", command=lambda: carregar_txt("nomes")).pack(pady=5)
tk.Button(janela, text="Carregar Preços", command=lambda: carregar_txt("preços")).pack(pady=5)

tk.Button(janela, text="Selecionar Pasta de Imagens", command=escolher_pasta).pack(pady=10)

tk.Button(janela, text="Gerar CSV", bg="green", fg="white", command=gerar_csv).pack(pady=20)

janela.mainloop()
