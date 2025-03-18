import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configurações
class Config:
    TEMPO_ESPERA_ELEMENTO = 10
    TEMPO_ESPERA_LOGIN = 60
    CAMINHO_ASSETS = os.path.join(os.getcwd(), 'assets')
    EXTENSOES_IMAGEM = ('.png', '.jpg', '.jpeg')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='whatsapp_automator.log',
    encoding='utf-8'
)

class WhatsAppAutomator:
    def __init__(self):
        self._driver = None
        self._bloqueio_envio = False
        self._caminho_midia = None
        self._tipo_midia = None  # 'imagem' ou 'documento'

    @property
    def bloqueio_envio(self):
        return self._bloqueio_envio

    @bloqueio_envio.setter
    def bloqueio_envio(self, value):
        self._bloqueio_envio = value

    def iniciar_driver(self):
        """Inicia o navegador Chrome e aguarda o login manual"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-notifications")
            options.add_argument("--start-maximized")
            options.add_experimental_option("detach", True)

            # Configuração corrigida do ChromeDriver
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(
                service=service,
                options=options
            )

            self._driver.get("https://web.whatsapp.com")

            WebDriverWait(self._driver, Config.TEMPO_ESPERA_LOGIN).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                )
            )
            logging.info("Login realizado com sucesso")
            return True
        except Exception as e:
            logging.error(f"Falha crítica: {str(e)}")
            messagebox.showerror("Erro Fatal", 
                "Verifique:\n"
                "1. Conexão com internet\n"
                "2. Chrome atualizado\n"
                "3. Permissões de arquivo")
            return False

    def _buscar_elemento(self, by, selector, timeout=Config.TEMPO_ESPERA_ELEMENTO):
        """Espera e retorna um elemento com tratamento de erro"""
        try:
            return WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException:
            logging.error(f"Elemento não encontrado: {selector}")
            raise

    def _limpar_pesquisa(self):
        """Limpa o campo de pesquisa de conversas"""
        search_box = self._buscar_elemento(
            By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'
        )
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        time.sleep(1)

    def buscar_grupo(self, turma):
        """Procura e seleciona um grupo pelo nome"""
        try:
            self._limpar_pesquisa()
            search_box = self._buscar_elemento(
                By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'
            )
            search_box.send_keys(turma)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)
            return True
        except Exception as e:
            logging.error(f"Erro ao buscar grupo {turma}: {str(e)}")
            return False

    def _anexar_midia(self):
        """Anexa mídia ao chat atual"""
        try:
            btn_anexar = self._buscar_elemento(By.XPATH, '//div[@title="Anexar"]')
            btn_anexar.click()
            time.sleep(1)

            input_midia = self._buscar_elemento(
                By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
            )
            input_midia.send_keys(self._caminho_midia)
            time.sleep(2)

            btn_enviar = self._buscar_elemento(By.XPATH, '//span[@data-icon="send"]')
            btn_enviar.click()
            time.sleep(2)
            return True
        except Exception as e:
            logging.error(f"Erro ao anexar mídia: {str(e)}")
            return False

    def enviar_mensagem(self, mensagem):
        """Envia mensagem de texto para o chat atual"""
        try:
            caixa_mensagem = self._buscar_elemento(
                By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
            )
            caixa_mensagem.send_keys(mensagem + Keys.ENTER)
            time.sleep(1)
            return True
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem: {str(e)}")
            return False

    def enviar_para_turma(self, turma, mensagem):
        """Fluxo completo de envio para uma turma"""
        try:
            if not self.buscar_grupo(turma):
                return False
            
            if self._caminho_midia and not self._anexar_midia():
                return False
            
            if mensagem and not self.enviar_mensagem(mensagem):
                return False
            
            return True
        except Exception as e:
            logging.error(f"Falha no envio para {turma}: {str(e)}")
            return False

class WhatsAppGUI:
    def __init__(self, root):
        self.root = root
        self.automator = WhatsAppAutomator()
        self.turmas = self._carregar_turmas()
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface gráfica"""
        self.root.title("Automação WhatsApp Pro")
        self.root.geometry("600x500")
        self._criar_widgets()
        self._configurar_layout()

    def _criar_widgets(self):
        """Cria todos os componentes da interface"""
        self.frame_controle = ttk.LabelFrame(self.root, text="Controle")
        self.frame_config = ttk.LabelFrame(self.root, text="Configurações")
        self.frame_mensagem = ttk.LabelFrame(self.root, text="Mensagem")
        self.frame_status = ttk.LabelFrame(self.root, text="Status")

        # Widgets de controle
        self.btn_iniciar = ttk.Button(
            self.frame_controle, 
            text="Iniciar Navegador", 
            command=self._iniciar_navegador
        )
        self.btn_enviar = ttk.Button(
            self.frame_controle,
            text="Iniciar Envio",
            command=self._iniciar_envio,
            state=tk.DISABLED
        )

        # Widgets de configuração
        self.var_modo = tk.StringVar(value='todas')
        self.combo_dias = ttk.Combobox(self.frame_config, state=tk.DISABLED)
        self._atualizar_dias()

        self.rb_todas = ttk.Radiobutton(
            self.frame_config,
            text="Todas as Turmas",
            variable=self.var_modo,
            value='todas'
        )
        self.rb_dia = ttk.Radiobutton(
            self.frame_config,
            text="Filtrar por Dia:",
            variable=self.var_modo,
            value='dia'
        )
        self.btn_midia = ttk.Button(
            self.frame_config,
            text="Selecionar Mídia",
            command=self._selecionar_midia
        )
        self.lbl_midia = ttk.Label(self.frame_config, text="Nenhum arquivo selecionado")

        # Widgets de mensagem
        self.txt_mensagem = tk.Text(self.frame_mensagem, height=8)
        self.scroll = ttk.Scrollbar(self.frame_mensagem, command=self.txt_mensagem.yview)
        self.txt_mensagem.configure(yscrollcommand=self.scroll.set)

        # Widgets de status
        self.lbl_status = ttk.Label(self.frame_status, text="Pronto")
        self.progresso = ttk.Progressbar(
            self.frame_status, 
            orient=tk.HORIZONTAL, 
            mode='determinate'
        )

    def _configurar_layout(self):
        """Organiza os widgets na interface"""
        # Layout frames
        self.frame_controle.pack(pady=5, fill=tk.X, padx=10)
        self.frame_config.pack(pady=5, fill=tk.X, padx=10)
        self.frame_mensagem.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)
        self.frame_status.pack(pady=5, fill=tk.X, padx=10)

        # Layout controle
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        self.btn_enviar.pack(side=tk.LEFT, padx=5)

        # Layout configuração
        self.rb_todas.grid(row=0, column=0, padx=5, sticky=tk.W)
        self.rb_dia.grid(row=0, column=1, padx=5, sticky=tk.W)
        self.combo_dias.grid(row=0, column=2, padx=5)
        self.btn_midia.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.lbl_midia.grid(row=1, column=1, columnspan=2, padx=5, sticky=tk.W)
        
        self.frame_config.columnconfigure([0,1,2], weight=1)

        # Layout mensagem
        self.txt_mensagem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Layout status
        self.lbl_status.pack(side=tk.TOP, fill=tk.X)
        self.progresso.pack(fill=tk.X)

    def _atualizar_dias(self):
        """Atualiza a lista de dias disponíveis"""
        dias = list({t['dia'] for t in self.turmas}) if self.turmas else []
        self.combo_dias['values'] = dias
        self.combo_dias.state(['!disabled' if self.var_modo.get() == 'dia' else 'disabled'])

    def _selecionar_midia(self):
        """Seleciona arquivo de mídia para envio"""
        caminho = filedialog.askopenfilename(filetypes=[
            ("Imagens", " ".join(f"*{ext}" for ext in Config.EXTENSOES_IMAGEM)),
            ("Todos os arquivos", "*.*")
        ])
        if caminho:
            self.automator._caminho_midia = caminho
            self.lbl_midia.config(text=f"Arquivo: {os.path.basename(caminho)}")

    def _iniciar_navegador(self):
        """Inicia o navegador em uma thread separada"""
        def tarefa_iniciar():
            self.btn_iniciar.config(state=tk.DISABLED)
            if self.automator.iniciar_driver():
                self.btn_enviar.config(state=tk.NORMAL)
                self._atualizar_status("Navegador pronto - Faça o login no WhatsApp Web")
            else:
                messagebox.showerror("Erro", "Falha ao iniciar o navegador")
            self.btn_iniciar.config(state=tk.NORMAL)

        threading.Thread(target=tarefa_iniciar, daemon=True).start()

    def _iniciar_envio(self):
        """Inicia o processo de envio das mensagens"""
        if self.automator.bloqueio_envio:
            return

        mensagem = self.txt_mensagem.get("1.0", tk.END).strip()
        if not mensagem:
            messagebox.showwarning("Aviso", "Digite a mensagem a ser enviada!")
            return

        turmas_selecionadas = self._obter_turmas_selecionadas()
        if not turmas_selecionadas:
            messagebox.showwarning("Aviso", "Nenhuma turma selecionada!")
            return

        if not messagebox.askyesno("Confirmar", f"Deseja enviar para {len(turmas_selecionadas)} turmas?"):
            return

        self.automator.bloqueio_envio = True
        self._atualizar_interface_envio(True)

        threading.Thread(target=self._executar_envio, args=(turmas_selecionadas, mensagem), daemon=True).start()

    def _executar_envio(self, turmas, mensagem):
        """Executa o envio em segundo plano"""
        total = len(turmas)
        for idx, turma in enumerate(turmas, 1):
            try:
                sucesso = self.automator.enviar_para_turma(turma['nome'], mensagem)
                status = "✓" if sucesso else "✗"
                self._atualizar_status(f"Enviando {idx}/{total} - {turma['nome']} {status}")
                self._atualizar_progresso(idx/total * 100)
            except Exception as e:
                logging.error(f"Erro crítico: {str(e)}")

        self._atualizar_interface_envio(False)
        messagebox.showinfo("Concluído", "Processo finalizado!")
        self._resetar_interface()

    def _obter_turmas_selecionadas(self):
        """Retorna a lista de turmas selecionadas"""
        if self.var_modo.get() == 'todas':
            return self.turmas
        return [t for t in self.turmas if t['dia'] == self.combo_dias.get().lower()]

    def _atualizar_status(self, mensagem):
        """Atualiza a mensagem de status na GUI"""
        self.root.after(0, self.lbl_status.config, {'text': mensagem})

    def _atualizar_progresso(self, valor):
        """Atualiza a barra de progresso"""
        self.root.after(0, self.progresso.config, {'value': valor})

    def _atualizar_interface_envio(self, enviando):
        """Atualiza o estado dos componentes durante o envio"""
        state = tk.DISABLED if enviando else tk.NORMAL
        self.btn_enviar.config(state=state)
        self.btn_iniciar.config(state=state)
        self.txt_mensagem.config(state=tk.DISABLED if enviando else tk.NORMAL)

    def _resetar_interface(self):
        """Restaura a interface ao estado inicial"""
        self.automator.bloqueio_envio = False
        self._atualizar_interface_envio(False)
        self._atualizar_progresso(0)
        self._atualizar_status("Pronto")

    @staticmethod
    def _carregar_turmas():
        """Carrega as turmas do arquivo de configuração"""
        try:
            with open('turmas.txt', 'r', encoding='utf-8') as f:
                return [{
                    'nome': linha.split(',')[0].strip(),
                    'dia': linha.split(',')[1].strip().lower()
                } for linha in f if linha.strip() and len(linha.split(',')) >= 2]
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'turmas.txt' não encontrado!")
            return []
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler turmas: {str(e)}")
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppGUI(root)
    root.mainloop()