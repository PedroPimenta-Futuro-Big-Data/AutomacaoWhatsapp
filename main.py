import pyautogui
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import pyperclip

# Configurações
pyautogui.PAUSE = 0.5
TEMPO_ESPERA_ELEMENTO = 10  # Aumentado para 10 segundos
CAMINHO_ASSETS = os.path.join(os.getcwd(), 'assets')

class WhatsAppAutomator:
    def __init__(self):
        self.bloqueio_envio = False
        self.caminho_imagem = None
        self.nome_imagem = None
    

    def buscar_elemento(self, imagem, regiao=None, confianca=0.7):
        inicio = time.time()
        while time.time() - inicio < TEMPO_ESPERA_ELEMENTO:
            try:
                pos = pyautogui.locateOnScreen(
                    os.path.join(CAMINHO_ASSETS, imagem),
                    region=regiao,
                    confidence=confianca,
                    grayscale=True
                )
                if pos:
                    return pos
            except pyautogui.ImageNotFoundException:
                time.sleep(0.5)
        raise Exception(f"Elemento não encontrado: {imagem}")

    def clicar_elemento(self, imagem, regiao=None):
        pos = self.buscar_elemento(imagem, regiao)
        pyautogui.click(pyautogui.center(pos))

    def buscar_grupo(self, turma):
        try:
            janela_whatsapp = pyautogui.getWindowsWithTitle("WhatsApp Web")
            if janela_whatsapp:
                janela_whatsapp[0].activate()
                time.sleep(1)
            
            self.clicar_elemento('lupa.png')  # Foco total na imagem
            time.sleep(1)
            
            pyperclip.copy(turma)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.5)
            pyautogui.press('enter')
        except Exception as e:
            raise RuntimeError(f"Falha ao buscar grupo: {str(e)}")

    # ... (Os outros métodos permanecem iguais)

def carregar_turmas():
    turmas = []
    try:
        with open('turmas.txt', 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    nome, dia = linha.split(',')
                    turmas.append({'nome': nome.strip(), 'dia': dia.strip().lower()})
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar turmas: {str(e)}")
    return turmas

def enviar_mensagem(self, mensagem):
        """Envia o texto da mensagem."""
        pyperclip.copy(mensagem)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(1)
def enviar_para_turma(self, turma, mensagem):  # <--- MÉTODO FALTANDO
        """Fluxo completo para uma turma."""
        try:
            self.buscar_grupo(turma)
            if self.caminho_imagem:
                self.anexar_imagem()
            self.enviar_mensagem(mensagem)
            pyautogui.hotkey('esc')  # Fecha conversa
        except Exception as e:
            raise RuntimeError(f"Erro em {turma}: {str(e)}")


# Interface Gráfica
def criar_interface():
    root = tk.Tk()
    root.title("Automação WhatsApp")
    root.geometry("500x400")

    automator = WhatsAppAutomator()
    todas_turmas = carregar_turmas()
    dias_disponiveis = list(set(t['dia'] for t in todas_turmas)) if todas_turmas else []

    # Frame de seleção de turma
    frame_selecao = ttk.LabelFrame(root, text="Seleção de Turmas")
    frame_selecao.pack(pady=10, padx=10, fill='x')

    modo_selecao = tk.StringVar(value='todas')

    rb_todas = ttk.Radiobutton(frame_selecao, text="Todas as Turmas", variable=modo_selecao, value='todas')
    rb_todas.pack(side='left', padx=5)

    rb_dia = ttk.Radiobutton(frame_selecao, text="Turmas por Dia:", variable=modo_selecao, value='dia')
    rb_dia.pack(side='left', padx=5)

    combo_dias = ttk.Combobox(frame_selecao, values=dias_disponiveis, state='disabled')
    combo_dias.pack(side='left', padx=5)

    def atualizar_combobox(*args):
        combo_dias.config(state='readonly' if modo_selecao.get() == 'dia' else 'disabled')
    modo_selecao.trace_add('write', atualizar_combobox)

    # Frame de imagem
    frame_imagem = ttk.LabelFrame(root, text="Imagem")
    frame_imagem.pack(pady=5, padx=10, fill='x')

    def selecionar_imagem():
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if caminho:
            automator.caminho_imagem = caminho
            automator.nome_imagem = os.path.basename(caminho)
            lbl_imagem.config(text=f"Imagem: {automator.nome_imagem}")

    btn_imagem = ttk.Button(frame_imagem, text="Selecionar Imagem", command=selecionar_imagem)
    btn_imagem.pack(side='left', padx=5)

    lbl_imagem = ttk.Label(frame_imagem, text="Nenhuma imagem selecionada")
    lbl_imagem.pack(side='left', padx=5)

    # Campo de mensagem
    frame_mensagem = ttk.LabelFrame(root, text="Mensagem")
    frame_mensagem.pack(pady=10, padx=10, fill='both', expand=True)

    campo_mensagem = tk.Text(frame_mensagem, height=6)
    campo_mensagem.pack(pady=5, padx=5, fill='both', expand=True)

    # Botão de envio
    def enviar_mensagens():
        if automator.bloqueio_envio:
            return

        try:
            mensagem = campo_mensagem.get("1.0", tk.END).strip()
            if not mensagem:
                messagebox.showerror("Erro", "Digite uma mensagem!")
                return

            if modo_selecao.get() == 'todas':
                turmas_selecionadas = [t['nome'] for t in todas_turmas]
            else:
                dia = combo_dias.get().lower()
                turmas_selecionadas = [t['nome'] for t in todas_turmas if t['dia'] == dia]

            if not turmas_selecionadas:
                messagebox.showwarning("Aviso", "Nenhuma turma selecionada!")
                return

            if not messagebox.askyesno("Confirmar", f"Enviar para {len(turmas_selecionadas)} turmas?"):
                return

            automator.bloqueio_envio = True

            def tarefa_envio():
                try:
                    messagebox.showinfo("Atenção", "Posicione o WhatsApp Web em 5 segundos!")
                    time.sleep(5)
                    
                    for turma in turmas_selecionadas:
                        automator.enviar_para_turma(turma, mensagem)

                    messagebox.showinfo("Sucesso", "Mensagens enviadas!")
                except Exception as e:
                    messagebox.showerror("Erro", str(e))
                finally:
                    automator.bloqueio_envio = False

            threading.Thread(target=tarefa_envio, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Erro", str(e))
            automator.bloqueio_envio = False

    btn_enviar = ttk.Button(root, text="Enviar Mensagens", command=enviar_mensagens)
    btn_enviar.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()