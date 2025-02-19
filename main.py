import pyautogui
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import shutil
import os

caminho_imagem = None
nome_imagem=  None
arquivo_temp = None  # Variável para armazenar uma cópia temporária do arquivo

pyautogui.PAUSE = 1
bloqueio_envio = False

import pyperclip  ### para uso do mesmo


def enviar_mensagem_whatsapp(turma, mensagem):
    try:
        pyautogui.click(x=309, y=204)  # Clique no campo de busca
        time.sleep(1)

        pyperclip.copy(turma)
        pyautogui.hotkey("ctrl", "v")  # Cola a mensagem no WhatsApp Web
        time.sleep(1.5)

        pyautogui.press('enter')  # Seleciona a turmaimagemCarnaval.jpeg
        time.sleep(1)

        if arquivo_temp:  # Se uma imagem foi selecionada, anexa pelo botão do WhatsApp
            # Clicar no botão de "Anexar Arquivo" (Ajuste as coordenadas se necessário)
            pyautogui.click(x=516, y=698)
            time.sleep(1)

            # Clicar na opção "Fotos e vídeos"
            pyautogui.click(x=581, y=428)
            time.sleep(2)

            # Digitar o caminho da imagem
            pyperclip.copy(nome_imagem)
            pyautogui.hotkey("ctrl", "v")  # Cola o caminho no explorador de arquivos
            time.sleep(1)

            # Pressionar Enter para confirmar o envio da imagem
            pyautogui.press('enter')
            time.sleep(2)

        # Copiar e colar a mensagem
        pyperclip.copy(mensagem)
        pyautogui.hotkey("ctrl", "v")  # Cola a mensagem no WhatsApp Web
        time.sleep(1)

        pyautogui.press('enter')  # Envia a mensagem
        time.sleep(1)
        pyautogui.hotkey('esc')  # Fecha a conversa
        time.sleep(1)

    except Exception as e:
        raise RuntimeError(f"Erro ao enviar para {turma}: {str(e)}")


def carregar_turmas():
    turmas = []
    try:
        with open('turmas.txt', 'r', encoding='utf-8') as arquivo:  ###Add encoding='utf-8' para carateres especiais
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    nome, dia = linha.split(',')
                    turmas.append({'nome': nome.strip(), 'dia': dia.strip().lower()})
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar turmas: {str(e)}")
    return turmas


def enviar_mensagens():
    global bloqueio_envio

    if bloqueio_envio:
        return

    try:
        mensagem = campo_mensagem.get("1.0", tk.END).strip()
        if not mensagem:
            messagebox.showerror("Erro", "Digite uma mensagem para enviar!")
            return

        turmas_selecionadas = []

        if modo_selecao.get() == 'todas':
            turmas_selecionadas = [t['nome'] for t in todas_turmas]
        else:
            dia = combo_dias.get().lower()
            turmas_selecionadas = [t['nome'] for t in todas_turmas if t['dia'] == dia]

        if not turmas_selecionadas:
            messagebox.showwarning("Aviso", "Nenhuma turma selecionada!")
            return

        confirmacao = messagebox.askyesno(
            "Confirmar",
            f"Pronto para enviar para {len(turmas_selecionadas)} turmas?\n\n"
            "Deixe o WhatsApp Web ABERTO e VISÍVEL!\n"
            "Não use o computador durante o envio!"
        )

        if not confirmacao:
            return

        bloqueio_envio = True

        def tarefa_envio():
            try:
                messagebox.showinfo(
                    "Atenção",
                    "O envio começará em 5 segundos!\n"
                    "POSICIONE O WHATSAPP WEB AGORA!"
                )

                time.sleep(5)

                for turma in turmas_selecionadas:
                    enviar_mensagem_whatsapp(turma, mensagem)

                messagebox.showinfo("Sucesso", "Todas mensagens enviadas!")

            except Exception as e:
                messagebox.showerror("Erro", str(e))

            finally:
                global bloqueio_envio
                bloqueio_envio = False

        threading.Thread(target=tarefa_envio, daemon=True).start()

    except Exception as e:
        messagebox.showerror("Erro", str(e))
        bloqueio_envio = False


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