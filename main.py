import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configurações
TEMPO_ESPERA_ELEMENTO = 10  # Segundos
CAMINHO_ASSETS = os.path.join(os.getcwd(), 'assets')

class WhatsAppAutomator:
    def __init__(self):
        self.bloqueio_envio = False
        self.caminho_imagem = None
        self.nome_imagem = None
        self.driver = None  # Garanta que está inicializado

    def iniciar_driver(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-notifications")
            options.add_argument("--start-maximized")
            options.add_experimental_option("detach", True)  # Mantém o navegador aberto após a execução

            self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
            )
            self.driver.get("https://web.whatsapp.com")
        
            # Aguarde o login MANUAL do usuário
            WebDriverWait(self.driver, 60).until(
            lambda d: d.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            )
            print("Login realizado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao iniciar o navegador: {str(e)}")
            self.driver = None

    def buscar_elemento(self, by, selector, timeout=TEMPO_ESPERA_ELEMENTO):
        """Espera e retorna um elemento"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector)))
    
    def buscar_grupo(self, turma):
        try:
            if not self.driver:
                raise RuntimeError("O navegador não foi iniciado corretamente. Reinicie o programa.")

            # Aguarda até que a barra de pesquisa esteja carregada
            search_box = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                )
            )
            # Limpar e pesquisar
            search_box.click()
            time.sleep(1)
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)
            search_box.send_keys(turma)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            
        except Exception as e:
            raise RuntimeError(f"Falha ao buscar grupo: {str(e)}")

    def anexar_imagem(self):
        """Anexa uma imagem"""
        try:
            # Clicar no botão de anexar
            btn_anexar = self.buscar_elemento(
                By.XPATH, '//div[@title="Anexar"]')
            btn_anexar.click()
            time.sleep(1)

            # Selecionar input de arquivo
            input_imagem = self.buscar_elemento(
                By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
            input_imagem.send_keys(self.caminho_imagem)
            time.sleep(2)

            # Enviar imagem
            btn_enviar = self.buscar_elemento(
                By.XPATH, '//span[@data-icon="send"]')
            btn_enviar.click()
            time.sleep(2)

        except Exception as e:
            raise RuntimeError(f"Erro ao anexar imagem: {str(e)}")

    def enviar_mensagem(self, mensagem):
        """Envia mensagem de texto"""
        try:
            caixa_mensagem = self.buscar_elemento(
                By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            caixa_mensagem.click()
            caixa_mensagem.send_keys(mensagem)
            caixa_mensagem.send_keys(Keys.ENTER)
            time.sleep(1)
        except Exception as e:
            raise RuntimeError(f"Erro ao enviar mensagem: {str(e)}")

    def enviar_para_turma(self, turma, mensagem):
        """Fluxo completo para uma turma"""
        try:
            self.buscar_grupo(turma)
            if self.caminho_imagem:
                self.anexar_imagem()
            self.enviar_mensagem(mensagem)
        except Exception as e:
            raise RuntimeError(f"Erro em {turma}: {str(e)}")
        
        
def carregar_turmas():  # <--- FUNÇÃO ADICIONADA
    turmas = []
    try:
        with open('turmas.txt', 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    nome, dia = linha.split(',')
                turmas.append({'nome': nome.strip(), 'dia': dia.strip().lower()})
    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'turmas.txt' não encontrado!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar turmas: {str(e)}")
    return turmas

# ... (O restante da interface gráfica permanece igual, exceto pela inicialização do driver)

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