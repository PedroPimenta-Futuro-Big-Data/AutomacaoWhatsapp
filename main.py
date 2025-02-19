import pyautogui
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import pyperclip
import shutil

# Configurações
pyautogui.PAUSE = 0.5
TEMPO_ESPERA_ELEMENTO = 5
CAMINHO_ASSETS = os.path.join(os.getcwd(), 'assets')

class WhatsAppAutomator:
    def __init__(self):
        self.bloqueio_envio = False
        self.caminho_imagem = None
        self.nome_imagem = None

    def buscar_elemento(self, imagem, regiao=None, confianca=0.9):
        """Procura por uma imagem na tela dentro de um timeout."""
        inicio = time.time()
        while time.time() - inicio < TEMPO_ESPERA_ELEMENTO:
            pos = pyautogui.locateOnScreen(
                os.path.join(CAMINHO_ASSETS, imagem),
                region=regiao,
                confidence=confianca,
                grayscale=True
            )
            if pos:
                return pos
            time.sleep(0.5)
        raise Exception(f"Elemento não encontrado: {imagem}")

    def clicar_elemento(self, imagem, regiao=None):
        """Encontra e clica no elemento desejado."""
        pos = self.buscar_elemento(imagem, regiao)
        pyautogui.click(pyautogui.center(pos))

    def buscar_grupo(self, turma):
        """Localiza e seleciona o grupo no WhatsApp."""
        try:
            self.clicar_elemento('lupa.png')  # Ícone de busca
        except:
            pyautogui.hotkey('ctrl', 'f')  # Fallback: Atalho de busca
        pyperclip.copy(turma)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.press('enter')

    def anexar_imagem(self):
        """Anexa a imagem selecionada."""
        self.clicar_elemento('anexar.png')  # Ícone de clipe
        time.sleep(1)
        self.clicar_elemento('fotos_videos.png')  # Opção "Fotos e Vídeos"
        time.sleep(1)
        pyperclip.copy(self.caminho_imagem)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(2)  # Espera upload

    def enviar_mensagem(self, mensagem):
        """Envia o texto da mensagem."""
        pyperclip.copy(mensagem)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(1)

    def enviar_para_turma(self, turma, mensagem):
        """Fluxo completo para uma turma."""
        try:
            self.buscar_grupo(turma)
            if self.caminho_imagem:
                self.anexar_imagem()
            self.enviar_mensagem(mensagem)
            pyautogui.hotkey('esc')  # Fecha conversa
        except Exception as e:
            raise RuntimeError(f"Erro em {turma}: {str(e)}")

# ... (O restante da interface gráfica segue similar, com ajustes para usar a nova classe)


# Interface gráfica
root = tk.Tk()
root.title("Automação WhatsApp")
root.geometry("500x400")
root.iconbitmap("logo.ico")

# Carregar turmas
todas_turmas = carregar_turmas()
dias_disponiveis = list(set(t['dia'] for t in todas_turmas)) if todas_turmas else []

#### Frame de seleção de turma
frame_selecao = ttk.LabelFrame(root, text="Seleção de Turmas")
frame_selecao.pack(pady=10, padx=10, fill='x')

modo_selecao = tk.StringVar(value='todas')

rb_todas = ttk.Radiobutton(frame_selecao, text="Todas as Turmas",
                           variable=modo_selecao, value='todas')
rb_todas.pack(side='left', padx=5)

rb_dia = ttk.Radiobutton(frame_selecao, text="Turmas por Dia:",
                         variable=modo_selecao, value='dia')
rb_dia.pack(side='left', padx=5)

combo_dias = ttk.Combobox(frame_selecao, values=dias_disponiveis, state='disabled')
combo_dias.pack(side='left', padx=5)


def atualizar_combobox(*args):
    combo_dias.config(state='readonly' if modo_selecao.get() == 'dia' else 'disabled')


modo_selecao.trace_add('write', atualizar_combobox)


#### Frame de seleção de Imagem ####
def selecionar_imagem():
    global caminho_imagem, arquivo_temp, nome_imagem
    caminho_imagem = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
    nome_imagem = os.path.basename(caminho_imagem)  # Pega apenas o nome do arquivo
    print(nome_imagem)

    if nome_imagem:
        lbl_imagem.config(text="Imagem selecionada: " + nome_imagem)

        # Criar uma cópia temporária para manipulação
        pasta_temp = os.path.join(os.getcwd(), "temp")  # Criar uma pasta temp no diretório atual
        if not os.path.exists(pasta_temp):
            os.makedirs(pasta_temp)

        arquivo_temp = os.path.join(pasta_temp, nome_imagem)  # Usar apenas o nome do arquivo
        shutil.copy(caminho_imagem, arquivo_temp)  # Copiar imagem para pasta temporária

# Botão para selecionar imagem
frame_imagem = ttk.LabelFrame(root, text="Imagem")
frame_imagem.pack(pady=5, padx=10, fill='x')

btn_imagem = ttk.Button(frame_imagem, text="Selecionar Imagem", command=selecionar_imagem)
btn_imagem.pack(side='left', padx=5)

lbl_imagem = ttk.Label(frame_imagem, text="Nenhuma imagem selecionada")
lbl_imagem.pack(side='left', padx=5)


#### Campo de mensagem ####
frame_mensagem = ttk.LabelFrame(root, text="Mensagem")
frame_mensagem.pack(pady=10, padx=10, fill='both', expand=True)

campo_mensagem = tk.Text(frame_mensagem, height=6)
campo_mensagem.pack(pady=5, padx=5, fill='both', expand=True)

# Botão de envio
btn_enviar = ttk.Button(root, text="Enviar Mensagens", command=enviar_mensagens)
btn_enviar.pack(pady=10)

root.mainloop()