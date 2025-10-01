#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatizador WhatsApp - Versão Final
Arquivo original: automatizador_whatsapp_interface.py
"""

import time
import threading
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class AutomatizadorWhatsApp:
    def __init__(self):
        self.driver = None
        self.lista_numeros = []
        self.rodando = False
        
        # Constantes específicas do código original
        self.PAUSA_ENTRE_ENVIOS = 20
        self.INTERVALO_DIGITACAO = 0.1
        self.TEMPO_ESPERA_ABERTURA = 15
        
                # Controles de estado
        self.rodando = False
        self.driver = None
        self.lista_numeros = []
        self.logs_mostrados = set()  # Controla logs únicos
        
        # Interface
        self.root = tk.Tk()
        self.root.title("🚀 Automatizador WhatsApp - Selenium")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # Variáveis da interface
        self.status_var = tk.StringVar(value="Pronto para iniciar")
        self.pausa_var = tk.StringVar(value="20")
        self.contador_chars = tk.StringVar(value="Caracteres: 0")
        self.contador_contatos = tk.StringVar(value="Total: 0 contatos")
        self.log_expandido = False
        self.modo_headless = tk.BooleanVar(value=False)  # Nova variável para modo em segundo plano
        
        self.criar_interface()
        
    def criar_interface(self):
        """Cria a interface gráfica completa baseada no código original"""
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       background='#007ACC',
                       foreground='white')
        style.map('Accent.TButton',
                 background=[('active', '#005A9E')])
        
        # Configurar grid principal
        self.root.configure(highlightthickness=0)
        
        # Canvas com scroll para interface completa
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Configurar canvas scroll
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind('<Configure>', configure_canvas)
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Frame principal com padding
        main_frame = ttk.Frame(self.scrollable_frame, padding="30")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === TÍTULO ===
        title_label = ttk.Label(main_frame, 
                               text="🚀 Automatizador WhatsApp",
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky="ew")
        
        # === AVISOS IMPORTANTES ===
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ AVISOS IMPORTANTES", padding="15")
        warning_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 25))
        warning_frame.columnconfigure(0, weight=1)
        
        warning_text = ttk.Label(warning_frame, 
                                text="⚠️ O script sempre abrirá um Chrome com perfil limpo\n"
                                     "⚠️ Será necessário escanear o QR Code do WhatsApp Web para fazer login\n"
                                     "⚠️ Este método pode violar os Termos de Serviço do WhatsApp\n"
                                     "⚠️ Use com EXTREMA moderação para evitar bloqueio da conta",
                                foreground="red")
        warning_text.grid(row=0, column=0, sticky="ew")
        
        # === MENSAGEM ===
        msg_frame = ttk.LabelFrame(main_frame, text="💬 Mensagem a Enviar", padding="15")
        msg_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 25))
        msg_frame.columnconfigure(0, weight=1)
        
        self.texto_mensagem = tk.Text(msg_frame, height=7, wrap=tk.WORD, font=('Arial', 10))
        self.texto_mensagem.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Texto padrão
        texto_padrao = ("Ola! Esta e uma mensagem de teste automatizada.\n\n"
                       "*Funcionalidades suportadas:*\n"
                       "- Links: https://www.google.com\n"
                       "- *Negrito*, _italico_, ~riscado~\n"
                       "- Quebras de linha\n\n"
                       "Por favor, ignore se ja recebeu. Estou testando um novo sistema.\n\n"
                       "Obrigado!")
        self.texto_mensagem.insert("1.0", texto_padrao)
        
        # Contador de caracteres
        chars_frame = ttk.Frame(msg_frame)
        chars_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        chars_frame.columnconfigure(1, weight=1)
        
        self.contador_chars = tk.StringVar(value="Caracteres: 0")
        ttk.Label(chars_frame, textvariable=self.contador_chars, font=('Arial', 9)).grid(row=0, column=0, sticky="ew")
        
        # Dica de formatação
        ttk.Label(chars_frame, 
                 text="💡 Dicas: *negrito* _itálico_ ~riscado~ + links funcionam! Emojis: use com moderação",
                 font=('Arial', 8, 'italic'),
                 foreground="blue").grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Bind para atualizar contador
        self.texto_mensagem.bind('<KeyRelease>', self.atualizar_contador)
        
        # === LISTA DE CONTATOS ===
        contatos_frame = ttk.LabelFrame(main_frame, text="📋 Lista de Contatos", padding="15")
        contatos_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 25))
        contatos_frame.columnconfigure(1, weight=1)
        
        # Botão para selecionar arquivo
        self.btn_arquivo = ttk.Button(contatos_frame, 
                                     text="📁 Selecionar Arquivo Excel",
                                     command=self.selecionar_arquivo,
                                     width=25)
        self.btn_arquivo.grid(row=0, column=0, padx=(0, 15), pady=(0, 10))
        
        # Label do arquivo selecionado
        self.label_arquivo = ttk.Label(contatos_frame, 
                                      text="Nenhum arquivo selecionado",
                                      foreground="gray",
                                      font=('Arial', 10))
        self.label_arquivo.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        
        # Treeview para mostrar contatos
        self.tree_contatos = ttk.Treeview(contatos_frame, columns=("numero",), show="headings", height=10)
        self.tree_contatos.heading("numero", text="Números de Telefone")
        self.tree_contatos.column("numero", width=200, anchor="center")
        self.tree_contatos.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Scrollbar para treeview
        tree_scroll = ttk.Scrollbar(contatos_frame, orient="vertical", command=self.tree_contatos.yview)
        tree_scroll.grid(row=1, column=2, sticky="ns", pady=(0, 10))
        self.tree_contatos.configure(yscrollcommand=tree_scroll.set)
        
        # Contador de contatos
        ttk.Label(contatos_frame, 
                 textvariable=self.contador_contatos,
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # === CONFIGURAÇÕES ===
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configurações", padding="10")
        config_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Pausa entre envios
        ttk.Label(config_frame, text="Pausa entre envios (segundos):").grid(row=0, column=0, sticky="w", pady=(0, 10))
        pausa_entry = ttk.Entry(config_frame, textvariable=self.pausa_var, width=10)
        pausa_entry.grid(row=0, column=1, padx=(10, 0), sticky="w", pady=(0, 10))
        
        # Modo de execução do Chrome
        ttk.Label(config_frame, text="Modo de execução:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        chrome_mode_frame = ttk.Frame(config_frame)
        chrome_mode_frame.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        
        ttk.Checkbutton(chrome_mode_frame, 
                       text="🔇 Executar Chrome em segundo plano (mais rápido)",
                       variable=self.modo_headless,
                       command=self.atualizar_modo_chrome).pack(anchor="w")
        
        self.label_modo = ttk.Label(chrome_mode_frame, 
                                   text="💻 Modo visual: Chrome será visível (mais lento, mas você pode acompanhar)",
                                   font=('Arial', 8, 'italic'),
                                   foreground="blue")
        self.label_modo.pack(anchor="w", pady=(5, 0))
        
        # === CONTROLES ===
        controls_frame = ttk.LabelFrame(main_frame, text="🎛️ Controles de Automação", padding="15")
        controls_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Configurar grid dos controles
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(2, weight=1)
        
        # Frame para os botões principais
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        # Botões de controle - organizados em linha
        self.btn_iniciar = ttk.Button(buttons_frame,
                                     text="🚀 INICIAR AUTOMAÇÃO",
                                     command=self.iniciar_automacao,
                                     style='Accent.TButton',
                                     width=22)
        self.btn_iniciar.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.btn_teste = ttk.Button(buttons_frame,
                                   text="🧪 TESTE (1 contato)",
                                   command=self.teste_um_contato,
                                   width=20)
        self.btn_teste.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.btn_parar = ttk.Button(buttons_frame,
                                   text="⏹️ PARAR",
                                   command=self.parar_automacao,
                                   state='disabled',
                                   width=15)
        self.btn_parar.grid(row=0, column=2, padx=(10, 0), sticky="e")
        
        # Barra de progresso
        self.progress = ttk.Progressbar(controls_frame, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(controls_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        # === LOG ===
        log_frame = ttk.LabelFrame(main_frame, text="📝 Log de Atividades", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Controles do log
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        log_controls.columnconfigure(1, weight=1)
        
        self.btn_toggle_log = ttk.Button(log_controls,
                                        text="🔽 Expandir Log",
                                        command=self.toggle_log)
        self.btn_toggle_log.grid(row=0, column=0, sticky="ew")
        
        ttk.Button(log_controls,
                  text="🗑️ Limpar",
                  command=self.limpar_log).grid(row=0, column=2, sticky="ew", padx=(10, 0))
        
        # Área de log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=4, width=60)
        self.log_text.grid(row=1, column=0, sticky="ew")
        
        # Configurar tags para cores
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="blue")
        
        # Log inicial reduzido
        self.log_text.configure(height=7)
        
        # === RODAPÉ ===
        footer_separator = ttk.Separator(main_frame, orient='horizontal')
        footer_separator.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        footer_label = ttk.Label(main_frame,
                                text="Desenvolvido por Victor Vasconcelos - 61984385187",
                                font=('Arial', 9, 'italic'),
                                foreground="gray")
        footer_label.grid(row=8, column=0, columnspan=2)
        
        self.atualizar_contador()
        
    def atualizar_modo_chrome(self):
        """Atualiza descrição do modo Chrome selecionado"""
        if self.modo_headless.get():
            self.label_modo.configure(
                text="🚀 Modo segundo plano: Chrome executará invisível (muito mais rápido!)",
                foreground="green"
            )
        else:
            self.label_modo.configure(
                text="💻 Modo visual: Chrome será visível (mais lento, mas você pode acompanhar)",
                foreground="blue"
            )
    def atualizar_contador(self, event=None):
        """Atualiza contador de caracteres"""
        texto = self.texto_mensagem.get("1.0", tk.END).strip()
        self.contador_chars.set(f"Caracteres: {len(texto)}")
        
    def toggle_log(self):
        """Expande/recolhe a área de log"""
        if not self.log_expandido:
            self.log_text.configure(height=12)
            self.btn_toggle_log.configure(text="🔼 Recolher Log")
            self.log_expandido = True
        else:
            self.log_text.configure(height=4)
            self.btn_toggle_log.configure(text="🔽 Expandir Log")
            self.log_expandido = False
            
    def limpar_log(self):
        """Limpa o log de atividades"""
        self.log_text.delete("1.0", tk.END)
        self.log("Log limpo", "info")
        
    def log(self, mensagem, tipo="info", unico=False):
        """Adiciona mensagem ao log com timestamp e controle de repetição"""
        if unico:
            # Para logs únicos, verifica se já foi mostrado
            if mensagem in self.logs_mostrados:
                return  # Não mostra novamente
            else:
                self.logs_mostrados.add(mensagem)
        
        timestamp = time.strftime("%H:%M:%S")
        linha = f"[{timestamp}] {mensagem}\n"
        
        self.log_text.insert(tk.END, linha, tipo)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def limpar_logs_unicos(self):
        """Limpa o cache de logs únicos para permitir nova exibição"""
        self.logs_mostrados.clear()
        
    def selecionar_arquivo(self):
        """Seleciona arquivo Excel com lista de contatos"""
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo Excel com os contatos",
            filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
        )
        
        if arquivo:
            try:
                # Carrega o arquivo Excel
                df = pd.read_excel(arquivo)
                
                # Verifica se tem coluna "Numero"
                if 'Numero' not in df.columns:
                    messagebox.showerror("Erro", "O arquivo deve ter uma coluna chamada 'Numero'")
                    return
                
                # Extrai números válidos
                numeros = df['Numero'].astype(str).tolist()
                self.lista_numeros = [num.strip() for num in numeros if num.strip() and num != 'nan']
                
                # Limpa treeview e adiciona novos números
                for item in self.tree_contatos.get_children():
                    self.tree_contatos.delete(item)
                
                for numero in self.lista_numeros:
                    self.tree_contatos.insert("", "end", values=(numero,))
                
                # Atualiza labels
                self.label_arquivo.configure(text=f"Arquivo carregado: {len(self.lista_numeros)} ({len(self.lista_numeros)} contatos)",
                                            foreground="green")
                self.contador_contatos.set(f"Total: {len(self.lista_numeros)} contatos")
                
                self.log(f"Arquivo carregado: {arquivo} ({len(self.lista_numeros)} contatos)", "success")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
                self.log(f"Erro ao carregar arquivo: {str(e)}", "error")
                
    def configurar_driver(self):
        """Configura driver Chrome com perfil temporário"""
        try:
            modo_desc = "segundo plano (headless)" if self.modo_headless.get() else "visual"
            self.log(f"Configurando Chrome WebDriver em modo {modo_desc}...", "info")
            
            # Criar diretório temporário para perfil
            temp_dir = None
            profile_dir = None
            try:
                temp_dir = tempfile.mkdtemp(prefix="whatsapp_automation_")
                self.log(f"Criando perfil temporário em: {temp_dir}", "info")
                
                options = Options()
                options.add_argument(f"--user-data-dir={temp_dir}")
                options.add_argument("--profile-directory=AutomationProfile")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument("--disable-extensions")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
                # Configurações específicas do modo
                if self.modo_headless.get():
                    # Modo segundo plano: inicia visível para login, depois fica headless
                    options.add_argument("--window-size=800,600")
                    options.add_argument("--window-position=200,200")
                    self.log("🚀 Modo segundo plano: Chrome visível para login, depois ficará invisível", "info")
                else:
                    # Modo visual (padrão) - janela de tamanho normal, não maximizada
                    options.add_argument("--window-size=1200,800")
                    options.add_argument("--window-position=100,100")
                    self.log("💻 Modo visual ativado - Chrome será visível", "info")
                
                # Otimizações gerais para performance
                options.add_argument("--disable-background-networking")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-client-side-phishing-detection")
                options.add_argument("--disable-default-apps")
                options.add_argument("--disable-hang-monitor")
                options.add_argument("--disable-popup-blocking")
                options.add_argument("--disable-prompt-on-repost")
                options.add_argument("--disable-sync")
                options.add_argument("--metrics-recording-only")
                options.add_argument("--no-first-run")
                options.add_argument("--safebrowsing-disable-auto-update")
                options.add_argument("--password-store=basic")
                
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                
                # Remove assinatura de automação
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                self.log("✅ Chrome configurado com sucesso!", "success")
                if not self.modo_headless.get():
                    self.log("🔑 Será necessário escanear o QR Code para fazer login", "info")
                else:
                    self.log("🔑 QR Code será carregado automaticamente - aguarde instruções", "info")
                
                return driver
                
            except Exception as e:
                self.log(f"❌ Erro ao configurar Chrome: {str(e)}", "error")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro ao configurar Chrome: {str(e)}", "error")
            return None
    def verificar_whatsapp_logado(self, driver):
        """Verifica se o WhatsApp Web está logado com verificação melhorada"""
        try:
            # Primeiro verifica se há QR Code visível (indica não logado)
            seletores_qr = [
                "//div[@data-testid='qrcode']",
                "//canvas[contains(@aria-label, 'Scan')]",
                "//div[contains(@class, 'qr-code')]"
            ]
            
            qr_visivel = False
            for seletor_qr in seletores_qr:
                try:
                    qr_elements = driver.find_elements(By.XPATH, seletor_qr)
                    for qr_element in qr_elements:
                        if qr_element.is_displayed():
                            qr_visivel = True
                            break
                    if qr_visivel:
                        break
                except:
                    continue
            
            if qr_visivel:
                self.log("🔍 QR Code ainda visível - aguardando escaneamento", "info")
                return False
            
            # Verifica elementos que confirmam interface logada
            seletores_logado = [
                # Lista de conversas
                "//div[@data-testid='chat-list']",
                "//div[contains(@class, 'chat-list')]",
                
                # Header principal
                "//div[@data-testid='chatlist-header']",
                "//header[contains(@class, 'app-header')]",
                
                # Campo de busca
                "//div[@data-testid='search-input']",
                "//div[contains(@title, 'Pesquisar')]",
                
                # Menu principal
                "//div[@data-testid='menu']",
                "//span[contains(@title, 'Menu')]",
                
                # Qualquer conversa
                "//div[contains(@class, 'chat') and @data-testid]",
                
                # Área de conversas geral
                "//div[contains(@class, 'app-wrapper-web')]//div[contains(@class, 'two')]"
            ]
            
            elementos_encontrados = 0
            for i, seletor in enumerate(seletores_logado):
                try:
                    elementos = driver.find_elements(By.XPATH, seletor)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            elementos_encontrados += 1
                            break
                except Exception as e:
                    continue
            
            # Aceita login com pelo menos 1 elemento válido (mais flexível)
            if elementos_encontrados >= 1:
                return True
            else:
                return False
                
        except Exception as e:
            self.log(f"Erro na verificação de login: {str(e)}", "error")
            return False
            
    def aguardar_login_whatsapp(self, driver, timeout=300):
        """Aguarda login no WhatsApp Web com verificação flexível"""
        try:
            self.log("🔍 Aguardando carregamento inicial da página...", "info")
            
            # Aguarda página básica carregar
            wait = WebDriverWait(driver, 45)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(3)
            
            # Aguarda elementos básicos do WhatsApp Web aparecerem
            self.log("⏳ Aguardando interface do WhatsApp Web carregar...", "info")
            try:
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='qrcode']")),
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='chat-list']")),
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'app-wrapper-web')]")),
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='chatlist-header']"))
                ))
                self.log("✅ Interface do WhatsApp Web carregada", "success")
            except:
                self.log("⚠️ Interface demorou para carregar, continuando verificação...", "warning")
            
            time.sleep(5)
            
            # Verifica se já está logado desde o início
            self.log("🔍 Verificando se já está logado...", "info")
            if self.verificar_whatsapp_logado(driver):
                self.log("🎉 Usuário já estava logado!", "success")
                time.sleep(5)  # Aguarda estabilizar
                return True
            
            # Processo de aguardo de login
            self.log("� WhatsApp não está logado. Por favor, escaneie o QR Code no seu celular.", "warning")
            self.log("⏰ Aguardando até 5 minutos para você escanear o QR Code...", "info")
            
            # Mensagem específica para modo headless
            if self.modo_headless.get():
                self.log("🚀 Modo segundo plano: Chrome visível para QR Code, depois será minimizado", "info")
                self.log("📱 Escaneie o QR Code - após login o Chrome ficará em segundo plano", "warning")
            
            tempo_inicial = time.time()
            ultima_verificacao = 0
            qr_detectado = False
            qr_log_mostrado = False  # Controla log único do QR Code
            contador_verificacoes = 0
            log_aguardo_mostrado = False  # Controla log único
            
            while time.time() - tempo_inicial < timeout:
                if not self.rodando:
                    self.log("❌ Processo cancelado pelo usuário", "warning")
                    return False
                
                # Informa sobre QR Code se detectado (apenas uma vez)
                if not qr_detectado and not qr_log_mostrado:
                    try:
                        qr_elements = driver.find_elements(By.XPATH, 
                            "//div[@data-testid='qrcode'] | //canvas[contains(@aria-label, 'Scan')]")
                        for qr_element in qr_elements:
                            if qr_element.is_displayed():
                                self.log("📱 QR Code detectado - escaneie com WhatsApp do seu celular", "info", unico=True)
                                qr_detectado = True
                                qr_log_mostrado = True
                                break
                    except:
                        pass
                
                # Verifica login a cada 3 segundos (mais frequente)
                if time.time() - ultima_verificacao > 3:
                    contador_verificacoes += 1
                    
                    if self.verificar_whatsapp_logado(driver):
                        elementos_encontrados = len([el for seletor in [
                            "//div[@data-testid='chat-list']",
                            "//div[@data-testid='chatlist-header']", 
                            "//div[contains(@class, 'app-wrapper-web')]//div[contains(@class, 'two')]"
                        ] for el in driver.find_elements(By.XPATH, seletor) if el.is_displayed()])
                        
                        self.log(f"✅ Login confirmado! ({elementos_encontrados} elementos da interface encontrados)", "success")
                        self.log("🎉 Login detectado! Aguardando estabilização da interface...", "success")
                        
                        # Aguarda estabilização (mais tempo)
                        for i in range(15):
                            if not self.rodando:
                                return False
                            time.sleep(1)
                            self.log(f"Estabilizando interface... {i+1}/15s", "info")
                            self.root.update_idletasks()
                        
                        # Verificação final de estabilidade
                        if self.verificar_whatsapp_logado(driver):
                            self.log("✅ Login confirmado e interface estável!", "success")
                            
                            # Se modo segundo plano ativado, minimizar Chrome após login
                            if self.modo_headless.get():
                                try:
                                    self.log("🚀 Login concluído! Enviando Chrome para segundo plano...", "info")
                                    
                                    # Método 1: Minimizar completamente
                                    driver.minimize_window()
                                    time.sleep(1)
                                    
                                    # Método 2: Posicionar fora da tela
                                    driver.set_window_position(-2000, -2000)
                                    driver.set_window_size(100, 100)
                                    time.sleep(1)
                                    
                                    self.log("✅ Chrome em segundo plano - automação invisível ativada", "success")
                                except Exception as e:
                                    self.log(f"⚠️ Não foi possível ocultar completamente: {str(e)}", "warning")
                            
                            time.sleep(3)  # Aguarda final
                            return True
                        else:
                            self.log("⚠️ Interface ainda instável, aguardando mais...", "warning")
                    else:
                        # Mostrar log apenas uma vez
                        if not log_aguardo_mostrado:
                            self.log("⏳ Aguardando login...", "info", unico=True)
                            log_aguardo_mostrado = True
                    
                    ultima_verificacao = time.time()
                
                # Status a cada 30 segundos
                tempo_decorrido = int(time.time() - tempo_inicial)
                if tempo_decorrido % 30 == 0 and tempo_decorrido > 0:
                    minutos_restantes = int((timeout - tempo_decorrido) / 60)
                    segundos_restantes = (timeout - tempo_decorrido) % 60
                    self.log(f"⏱️ Aguardando login... (Tempo restante: {minutos_restantes}m {segundos_restantes}s)", "info")
                
                time.sleep(1)
                self.root.update_idletasks()
            
            self.log("⏰ Tempo limite para login excedido! Tente novamente.", "error")
            return False
            
        except Exception as e:
            self.log(f"Erro durante aguardo de login: {str(e)}", "error")
            return False
    def enviar_mensagem_selenium(self, driver, numero, mensagem):
        """Envia mensagem usando Selenium - método direto simples com divisão inteligente"""
        try:
            self.log(f"Iniciando envio para {numero}...", "info")
            
            # URL direto com o telefone da lista
            url_conversa = f"https://web.whatsapp.com/send?phone={numero}"
            self.log(f"Abrindo conversa: {url_conversa}", "info")
            
            # Navegar diretamente para a URL
            driver.get(url_conversa)
            
            # Aguardar a página carregar
            self.log("Aguardando página carregar...", "info", unico=True)
            time.sleep(8)
            
            # Verificar se apareceu o diálogo "Usar o WhatsApp Web" e fechar
            try:
                self.log("Procurando diálogo 'Usar o WhatsApp Web'...", "info", unico=True)
                usar_web_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Usar o WhatsApp Web') or contains(text(), 'Use WhatsApp Web')]"))
                )
                usar_web_button.click()
                time.sleep(3)
                self.log("✓ Diálogo 'Usar o WhatsApp Web' fechado", "success", unico=True)
            except:
                self.log("Nenhum diálogo encontrado, continuando...", "info", unico=True)
            
            # Aguardar elementos da conversa aparecerem
            self.log("Aguardando caixa de texto aparecer...", "info", unico=True)
            
            # Aguarda a caixa de texto da conversa aparecer
            wait = WebDriverWait(driver, 20)
            caixa_texto = None
            
            try:
                # Usar o seletor que funcionou nos testes
                caixa_texto = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
                )
                self.log("✅ Caixa de texto encontrada!", "success")
            except Exception as e:
                self.log(f"❌ ERRO: Não foi possível encontrar caixa de texto: {str(e)}", "error")
                return False
            
            # LÓGICA INTELIGENTE DE DIVISÃO DE MENSAGEM
            self.log("🤖 Analisando estrutura da mensagem...", "info", unico=True)
            
            # Verifica se há parágrafos (quebras de linha)
            if '\n\n' in mensagem or mensagem.count('\n') >= 2:
                # Dividir por parágrafos
                paragrafos = []
                
                # Primeiro tenta dividir por \n\n (parágrafos reais)
                if '\n\n' in mensagem:
                    paragrafos = [p.strip() for p in mensagem.split('\n\n') if p.strip()]
                    self.log(f"📝 Mensagem dividida em {len(paragrafos)} parágrafos (por \\n\\n)", "info")
                
                # Se não tiver \n\n mas tiver várias quebras simples, divide por \n
                elif mensagem.count('\n') >= 2:
                    linhas = [l.strip() for l in mensagem.split('\n') if l.strip()]
                    # Agrupa linhas em parágrafos menores (máximo 3 linhas por parágrafo)
                    paragrafos = []
                    for i in range(0, len(linhas), 3):
                        paragrafo = '\n'.join(linhas[i:i+3])
                        paragrafos.append(paragrafo)
                    self.log(f"📝 Mensagem dividida em {len(paragrafos)} blocos (por quebras de linha)", "info")
                
                # Enviar cada parágrafo separadamente
                for i, paragrafo in enumerate(paragrafos, 1):
                    if paragrafo.strip():
                        self.log(f"📤 Enviando parte {i}/{len(paragrafos)}: {paragrafo[:50]}{'...' if len(paragrafo) > 50 else ''}", "info")
                        
                        # Limpar e focar na caixa de texto
                        caixa_texto.clear()
                        caixa_texto.click()
                        caixa_texto.send_keys(paragrafo.strip())
                        
                        time.sleep(1)
                        
                        # Enviar parte
                        caixa_texto.send_keys(Keys.ENTER)
                        
                        # Pausa entre partes (para não parecer spam)
                        if i < len(paragrafos):
                            time.sleep(2)
                            self.log(f"⏸️ Pausa entre partes ({i}/{len(paragrafos)})...", "info")
                
                self.log(f"✅ Mensagem completa enviada em {len(paragrafos)} partes!", "success")
                
            else:
                # Mensagem sem parágrafos - enviar tudo junto
                self.log("📤 Mensagem única (sem parágrafos) - enviando tudo junto", "info")
                
                # Limpar e focar na caixa de texto
                caixa_texto.clear()
                caixa_texto.click()
                caixa_texto.send_keys(mensagem)
                
                time.sleep(2)
                
                # Enviar mensagem
                self.log("Enviando mensagem...", "info")
                caixa_texto.send_keys(Keys.ENTER)
                
                self.log("✅ Mensagem enviada com sucesso!", "success")
            
            time.sleep(3)
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao enviar mensagem: {str(e)}", "error")
            return False

    def iniciar_automacao(self):
        """Inicia automação completa baseada no código original"""
        # Verifica se tem arquivo
        if not self.lista_numeros:
            messagebox.showerror("Erro", "Selecione um arquivo com a lista de contatos!")
            return
            
        # Verifica mensagem
        mensagem = self.texto_mensagem.get("1.0", tk.END).strip()
        if not mensagem:
            messagebox.showerror("Erro", "Digite uma mensagem para enviar!")
            return
            
        # Validar pausa
        try:
            pausa = int(self.pausa_var.get())
            self.PAUSA_ENTRE_ENVIOS = pausa
        except:
            messagebox.showerror("Erro", "Pausa entre envios deve ser um número!")
            return
            
        # Confirmação
        resposta = messagebox.askyesno(
            "Confirmar Automação",
            f"Iniciar envio para {len(self.lista_numeros)} contatos?\n\n"
            f"Mensagem: {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n"
            f"⚠️ ATENÇÃO: Este processo pode levar muito tempo!\n\n"
            f"🔑 Será necessário escanear o QR Code do WhatsApp Web"
        )
        
        if not resposta:
            return
            
        # Configurar interface
        self.rodando = True
        self.btn_iniciar.config(state='disabled')
        self.btn_teste.config(state='disabled') 
        self.btn_parar.config(state='normal')
        
        # Iniciar thread
        threading.Thread(target=self.executar_automacao, args=(mensagem,), daemon=True).start()
        
    def teste_um_contato(self):
        """Teste com um contato baseado no código original"""
        if not self.lista_numeros:
            messagebox.showerror("Erro", "Selecione um arquivo com a lista de contatos!")
            return
            
        mensagem = self.texto_mensagem.get("1.0", tk.END).strip()
        if not mensagem:
            messagebox.showerror("Erro", "Digite uma mensagem para enviar!")
            return
            
        primeiro_numero = self.lista_numeros[0]
        resposta = messagebox.askyesno(
            "Confirmar Teste",
            f"Enviar mensagem de TESTE para:\n{primeiro_numero}\n\n"
            f"Mensagem: {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n"
            f"Este é apenas um teste com 1 contato."
        )
        
        if not resposta:
            return
            
        # Configurar interface
        self.rodando = True
        self.btn_iniciar.config(state='disabled')
        self.btn_teste.config(state='disabled')
        self.btn_parar.config(state='normal')
        
        # Iniciar thread
        threading.Thread(target=self.executar_teste, args=(mensagem, primeiro_numero), daemon=True).start()
        
    def executar_teste(self, mensagem, numero):
        """Executa teste com um contato"""
        try:
            # Configurar driver
            self.status_var.set("Configurando navegador para teste...")
            self.driver = self.configurar_driver()
            
            if not self.driver:
                self.log("Erro ao configurar navegador", "error")
                return
                
            # Navegar para WhatsApp
            self.status_var.set("Navegando para WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            # Aguardar login
            self.status_var.set("Aguardando login no WhatsApp...")
            if not self.aguardar_login_whatsapp(self.driver):
                self.log("Falha no login do WhatsApp", "error")
                return
                
            # Enviar mensagem de teste
            self.status_var.set(f"TESTE: Enviando para {numero}...")
            self.progress['maximum'] = 1
            self.progress['value'] = 0
            
            if self.enviar_mensagem_selenium(self.driver, numero, mensagem):
                self.log("✅ TESTE CONCLUÍDO COM SUCESSO!", "success")
                self.status_var.set("Teste concluído com sucesso!")
                messagebox.showinfo("Teste Concluído", f"✅ Mensagem enviada com sucesso para:\n{numero}")
            else:
                self.log("❌ TESTE FALHOU", "error")
                self.status_var.set("Teste falhou!")
                messagebox.showerror("Teste Falhou", f"❌ Não foi possível enviar para:\n{numero}")
                
            self.progress['value'] = 1
            
        except Exception as e:
            self.log(f"Erro no teste: {str(e)}", "error")
            messagebox.showerror("Erro", f"Erro durante o teste: {str(e)}")
        finally:
            self.finalizar_automacao()
            
    def executar_automacao(self, mensagem):
        """Executa automação completa baseada no código original"""
        try:
            # Limpar cache de logs únicos para nova automação
            self.limpar_logs_unicos()
            
            # Configurar driver
            self.status_var.set("Configurando navegador...")
            self.driver = self.configurar_driver()
            
            if not self.driver:
                self.log("Erro ao configurar navegador", "error")
                return
                
            # Navegar para WhatsApp
            self.status_var.set("Navegando para WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            # Aguardar login
            self.status_var.set("Aguardando login no WhatsApp...")
            if not self.aguardar_login_whatsapp(self.driver):
                self.log("Falha no login do WhatsApp", "error")
                return
                
            # Processar contatos
            total = len(self.lista_numeros)
            sucessos = 0
            falhas = 0
            
            self.progress['maximum'] = total
            
            for i, numero in enumerate(self.lista_numeros):
                if not self.rodando:
                    self.log("Automação interrompida pelo usuário", "warning")
                    break
                    
                self.status_var.set(f"Enviando para {numero} ({i+1}/{total})...")
                self.progress['value'] = i + 1
                
                if self.enviar_mensagem_selenium(self.driver, numero, mensagem):
                    sucessos += 1
                else:
                    falhas += 1
                    
                # Pausa entre envios (exceto no último)
                if i < total - 1 and self.rodando:
                    self.status_var.set(f"Aguardando {self.PAUSA_ENTRE_ENVIOS}s...")
                    for segundo in range(self.PAUSA_ENTRE_ENVIOS):
                        if not self.rodando:
                            break
                        time.sleep(1)
                        self.root.update_idletasks()
                        
            # Relatório final
            self.log("AUTOMAÇÃO CONCLUÍDA!", "success")
            self.log(f"Sucessos: {sucessos}", "success")
            self.log(f"Falhas: {falhas}", "error" if falhas > 0 else "info")
            self.log(f"Total processado: {sucessos + falhas}", "info")
            
            self.status_var.set(f"Concluído: {sucessos} sucessos, {falhas} falhas")
            
            messagebox.showinfo(
                "Automação Concluída",
                f"Envios finalizados!\n\n✅ Sucessos: {sucessos}\n❌ Falhas: {falhas}\n📊 Total: {sucessos + falhas}"
            )
            
        except Exception as e:
            self.log(f"Erro na automação: {str(e)}", "error")
            messagebox.showerror("Erro", f"Erro durante a automação: {str(e)}")
        finally:
            self.finalizar_automacao()
            
    def parar_automacao(self):
        """Para automação em execução"""
        self.rodando = False
        self.log("Parando automação...", "warning")
        self.status_var.set("Parando...")
        
    def finalizar_automacao(self):
        """Finaliza automação e limpa recursos"""
        self.rodando = False
        
        # Fechar driver
        if self.driver:
            try:
                self.driver.quit()
                self.log("Navegador fechado", "info")
            except:
                pass
            self.driver = None
            
        # Restaurar interface
        self.btn_iniciar.config(state='normal')
        self.btn_teste.config(state='normal') 
        self.btn_parar.config(state='disabled')
        self.progress['value'] = 0
        
        # Atualizar status se necessário
        if self.status_var.get() in ("Parando...", "Configurando navegador para teste...", "Configurando navegador..."):
            self.status_var.set("Pronto para iniciar")
            
    def executar(self):
        """Executa aplicação"""
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)
        self.root.mainloop()
        
    def ao_fechar(self):
        """Manipula fechamento da aplicação"""
        if self.rodando:
            resposta = messagebox.askyesno(
                "Confirmação",
                "A automação está em execução. Deseja realmente sair?"
            )
            if not resposta:
                return
                
            self.parar_automacao()
            
        # Fechar driver
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
                
        self.root.destroy()


def main():
    """Função principal"""
    try:
        app = AutomatizadorWhatsApp()
        app.executar()
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar aplicação: {str(e)}")


if __name__ == "__main__":
    main()