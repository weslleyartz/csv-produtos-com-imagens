📄 Licença: [GNU AGPL v3.0](LICENSE)


# 🧾 Gerador de CSV de Produtos com Caminho de Imagens

Este projeto é um gerador de CSV automatizado com interface gráfica, feito em Python, que permite:

- Importar listas de códigos, nomes e preços a partir de arquivos `.txt`
- Selecionar uma pasta de imagens com nomes correspondentes aos códigos
- Gerar automaticamente um arquivo `CSV` contendo todas as informações, incluindo o caminho da imagem, pronto para uso em sistemas de e-commerce, catálogos ou integrações de marketing

---


📹 Tutorial em Vídeo
   Assista ao vídeo abaixo para ver como utilizar o gerador de CSV e integrar com o Adobe InDesign para criar catálogos automaticamente:

   https://www.youtube.com/watch?v=####



## 📦 Funcionalidades

- Interface gráfica simples via `Tkinter`
- Geração de log (`log_execucao.txt`) com todas as ações e erros
- Verificação automática de correspondência entre código e imagem
- Suporte a UTF-8 com BOM (`utf-8-sig`) no CSV final para compatibilidade com Excel
- Exportação de arquivo `produtos_com_caminhos.csv` com colunas: `Código`, `Nome`, `Preço` e `@Imagem`

---

## 🖼️ Estrutura Esperada

**Arquivos de entrada:**
- `codigos.txt`: uma lista de códigos, um por linha
- `nomes.txt`: uma lista de nomes de produtos, um por linha
- `precos.txt`: uma lista de preços, um por linha (ex: `R$ 999,90` como texto)
- Imagens: dentro de uma pasta, com nomes correspondentes aos códigos e extensão `.png`

---

## 🛠️ Como Usar

1. Clone ou baixe o repositório.

2. Execute o script Python:
   
   <pre> python gerador_csv.py </pre>

3. Na interface gráfica:

Clique nos botões para importar os arquivos .txt

Escolha a pasta com as imagens dos produtos

Clique em "Gerar CSV"

O CSV será salvo na mesma pasta do script com o nome:

produtos-com-imagens.csv


## 🧾 Licença

Este projeto está licenciado sob a **GNU Affero General Public License v3.0**.

Você pode:
- Usar para fins comerciais
- Modificar e redistribuir
- Utilizar em projetos fechados desde que **o código-fonte completo seja disponibilizado**

🔗 [Leia a licença completa aqui](LICENSE)

© 2025 Weslley Carvalho de Souza (weslleycs97)
