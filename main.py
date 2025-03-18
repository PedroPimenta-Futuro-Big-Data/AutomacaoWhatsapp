import requests
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from threading import Thread

class WhatsAppAutomation:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação WhatsApp - ZAPI")
        self.root.geometry("800x600")
        
        # Variáveis de configuração
        self.instance_id = "3DB18FB2C14400BEAA31FE2787F59778"
        self.instance_token = "03A12EBE18E895CB7F1FE6D0"
        self.client_token = "Fc451362c2d2449659383fe1fcc7816adS"
        self.running = False
        self.groups = []
        
        # Configurar interface
        self.create_widgets()
        self.configure_grid()
        
    def create_widgets(self):
        # Frame de configuração
        config_frame = ttk.LabelFrame(self.root, text="Configurações da API")
        config_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Campos de entrada para tokens (opcional)
        ttk.Label(config_frame, text="Instance ID:").grid(row=0, column=0, padx=5, pady=2)
        self.instance_id_entry = ttk.Entry(config_frame)
        self.instance_id_entry.insert(0, self.instance_id)
        self.instance_id_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Botão para carregar grupos
        self.btn_load = ttk.Button(config_frame, text="Carregar Grupos", command=self.load_groups_thread)
        self.btn_load.grid(row=0, column=2, padx=5, pady=2)
        
        # Lista de grupos
        self.group_list = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.group_list.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Área de mensagem
        msg_frame = ttk.LabelFrame(self.root, text="Mensagem")
        msg_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.message_entry = scrolledtext.ScrolledText(msg_frame, height=5)
        self.message_entry.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Controles
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        
        self.btn_start = ttk.Button(control_frame, text="Iniciar Envio", command=self.start_sending)
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(control_frame, text="Parar", command=self.stop_sending, state=tk.DISABLED)
        self.btn_stop.pack(side="left", padx=5)
        
        # Logs
        self.log_area = scrolledtext.ScrolledText(self.root, height=10)
        self.log_area.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        
    def configure_grid(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(4, weight=1)
        
    def log(self, message):
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        
    def load_groups_thread(self):
        Thread(target=self.load_groups, daemon=True).start()
        
    def load_groups(self):
        try:
            self.btn_load.config(state=tk.DISABLED)
            self.log("Carregando grupos...")
            
            url = f"https://api.z-api.io/instances/{self.instance_id}/token/{self.instance_token}/chats"
            headers = {
                "Content-Type": "application/json",
                "client-token": self.client_token
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            groups = [chat for chat in response.json() if chat['isGroup']]
            self.groups = groups
            
            self.group_list.delete(0, tk.END)
            for group in groups:
                self.group_list.insert(tk.END, group['name'])
                
            self.log(f"{len(groups)} grupos carregados com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar grupos: {str(e)}")
            self.log(f"Erro ao carregar grupos: {str(e)}")
        finally:
            self.btn_load.config(state=tk.NORMAL)
            
    def start_sending(self):
        if not self.running:
            selected = self.group_list.curselection()
            message = self.message_entry.get("1.0", tk.END).strip()
            
            if not selected:
                messagebox.showwarning("Aviso", "Selecione pelo menos um grupo!")
                return
                
            if not message:
                messagebox.showwarning("Aviso", "Digite uma mensagem!")
                return
                
            self.running = True
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            Thread(target=self.send_messages, args=(selected, message), daemon=True).start()
            
    def stop_sending(self):
        self.running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.log("Envio interrompido pelo usuário")
        
    def send_messages(self, selected, message):
        url = f"https://api.z-api.io/instances/{self.instance_id}/token/{self.instance_token}/send-text"
        headers = {
            "Content-Type": "application/json",
            "client-token": self.client_token
        }
        
        success = 0
        errors = 0
        
        for index in selected:
            if not self.running:
                break
                
            group = self.groups[index]
            payload = {
                "phone": group['id'],
                "message": message
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                self.log(f"Mensagem enviada para {group['name']}")
                success += 1
            except Exception as e:
                self.log(f"Erro ao enviar para {group['name']}: {str(e)}")
                errors += 1
                
            time.sleep(5)  # Intervalo entre envios
            
        self.running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.log(f"Processo concluído! Sucessos: {success}, Erros: {errors}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppAutomation(root)
    root.mainloop()