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
    # ... (código anterior permanece igual)
    
    def iniciar_driver(self):
        """Inicia o navegador Chrome com Selenium"""
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        
        # Configuração correta para Selenium 4+
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),  # Corrigido aqui
            options=options
        )
        self.driver.get("https://web.whatsapp.com")
        input("Faça o login no WhatsApp Web e pressione Enter...")

    def buscar_elemento(self, by, selector, timeout=TEMPO_ESPERA_ELEMENTO):
        """Espera e retorna um elemento"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector)))
    
    def buscar_grupo(self, turma):
        """Localiza e entra no grupo"""
        try:
            # Localizar barra de pesquisa
            search_box = self.buscar_elemento(
                By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            
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

# ... (O restante da interface gráfica permanece igual, exceto pela inicialização do driver)

def criar_interface():
    root = tk.Tk()
    root.title("Automação WhatsApp")
    root.geometry("500x400")

    automator = WhatsAppAutomator()
    automator.iniciar_driver()  # Novo: Inicia o navegador

    # ... (O restante do código da interface permanece igual)
