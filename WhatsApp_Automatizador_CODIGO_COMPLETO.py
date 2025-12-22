#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatizador de Mensagens WhatsApp
"""

import time
import threading
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import random
import re
import os
from datetime import datetime
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ==================== FUNÇÕES UTILITÁRIAS ====================

def validar_numero_telefone(numero):
    """Valida e limpa número de telefone"""
    if not numero:
        return None
    
    numero_str = str(numero).strip()
    numero_limpo = re.sub(r'[^\d]', '', numero_str)
    
    if len(numero_limpo) == 13 and numero_limpo.startswith('55'):
        return numero_limpo
    elif len(numero_limpo) == 11:
        return '55' + numero_limpo
    elif len(numero_limpo) == 10:
        return '55' + numero_limpo
    
    return None

def remover_duplicatas_e_validar(numeros):
    """Remove duplicatas e retorna (válidos, inválidos, duplicatas)"""
    validos = []
    invalidos = []
    vistos = set()
    duplicatas = 0
    
    for num in numeros:
        num_validado = validar_numero_telefone(num)
        
        if num_validado:
            if num_validado not in vistos:
                validos.append(num_validado)
                vistos.add(num_validado)
            else:
                duplicatas += 1
        else:
            invalidos.append(str(num))
    
    return validos, invalidos, duplicatas

def salvar_historico_envio(numero, status, mensagem="", resultado=""):
    """Salva histórico de envio em CSV"""
    arquivo_historico = "historico_envios.csv"
    
    criar_arquivo = not os.path.exists(arquivo_historico)
    
    try:
        with open(arquivo_historico, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if criar_arquivo:
                writer.writerow(['Data', 'Hora', 'Número', 'Status', 'Resultado', 'Mensagem Chars'])
            
            timestamp = datetime.now()
            data = timestamp.strftime('%d/%m/%Y')
            hora = timestamp.strftime('%H:%M:%S')
            
            writer.writerow([data, hora, numero, status, resultado, len(mensagem)])
    except Exception as e:
        print(f"Erro ao salvar histórico: {str(e)}")

def exportar_modelo_excel():
    """Exporta modelo de planilha Excel"""
    try:
        df = pd.DataFrame({
            'Numero': ['5511999999999', '5521998888888', '5585987777777']
        })
        
        arquivo_modelo = "MODELO_CONTATOS.xlsx"
        df.to_excel(arquivo_modelo, index=False, sheet_name='Contatos')
        
        return arquivo_modelo, True
    except Exception as e:
        return str(e), False

class AutomatizadorWhatsApp:
    def __init__(self):
        self.rodando = False
        self.driver = None
        self.lista_numeros = []
        self.logs_mostrados = set()
        
        self.PAUSA_ENTRE_ENVIOS = 20
        
        self.root = tk.Tk()
        self.root.title("🚀 Automatizador WhatsApp - Selenium")
        self.root.geometry("1200x900")
        self.root.resizable(True, True)
        try:
            self.root.state('zoomed')  # Maximizar no Windows
        except:
            pass  # Fallback para outros SOs
        
        # Variáveis da interface
        self.status_var = tk.StringVar(value="Pronto para iniciar")
        self.pausa_var = tk.StringVar(value="20")
        self.pausa_min_var = tk.StringVar(value="15")  # Pausa mínima (aleatória)
        self.pausa_max_var = tk.StringVar(value="25")  # Pausa máxima (aleatória)
        self.usar_pausa_aleatoria = tk.BooleanVar(value=False)  # Ativar pausa aleatória
        self.envio_unico = tk.BooleanVar(value=True)  # Enviar em uma única mensagem
        self.contador_chars = tk.StringVar(value="Caracteres: 0")
        self.contador_contatos = tk.StringVar(value="Total: 0 contatos")
        self.log_expandido = False
        self.modo_headless = tk.BooleanVar(value=False)
        
        self.criar_interface()
        
    def criar_interface(self):
        """Cria a interface gráfica completa"""
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       background='#007ACC',
                       foreground='white')
        style.map('Accent.TButton',
                 background=[('active', '#005A9E')])
        
        # Canvas com scroll para interface completa
        canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # ID do canvas window para reconfigurar largura
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Função para expandir frame com o canvas
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
            
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.scrollable_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Configurar scroll do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Frame principal com padding
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # Título
        main_frame.rowconfigure(1, weight=0)  # Avisos
        main_frame.rowconfigure(2, weight=0)  # Mensagem
        main_frame.rowconfigure(3, weight=0)  # Contatos
        main_frame.rowconfigure(4, weight=0)  # Config
        main_frame.rowconfigure(5, weight=0)  # Controles
        main_frame.rowconfigure(6, weight=1)  # Log (expande)
        
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
                                text="⚠️ Chrome será aberto com perfil limpo\n"
                                     "⚠️ É necessário escanear o QR Code do WhatsApp Web\n"
                                     "⚠️ Use com moderação pra não tomar ban",
                                foreground="red")
        warning_text.grid(row=0, column=0, sticky="ew")
        
        msg_frame = ttk.LabelFrame(main_frame, text="💬 Mensagem", padding="15")
        msg_frame.grid(row=2, column=0, columnspan=2, sticky="ewns", pady=(0, 15))
        msg_frame.columnconfigure(0, weight=1)
        
        self.texto_mensagem = tk.Text(msg_frame, height=6, wrap=tk.WORD, font=('Arial', 10))
        self.texto_mensagem.grid(row=0, column=0, sticky="ewns", pady=(0, 10))
        
        texto_padrao = ("Ola! Esta e uma mensagem de teste automatizada.\n\n"
                       "*Funcionalidades suportadas:*\n"
                       "- Links: https://www.google.com\n"
                       "- *Negrito*, _italico_, ~riscado~\n"
                       "- Quebras de linha\n\n"
                       "Por favor, ignore se ja recebeu. Estou testando um novo sistema.\n\n"
                       "Obrigado!")
        self.texto_mensagem.insert("1.0", texto_padrao)
        
        chars_frame = ttk.Frame(msg_frame)
        chars_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        chars_frame.columnconfigure(1, weight=1)
        
        ttk.Label(chars_frame, textvariable=self.contador_chars, font=('Arial', 9)).grid(row=0, column=0, sticky="ew")
        
        ttk.Label(chars_frame, 
                 text="💡 Dicas: *negrito* _itálico_ ~riscado~ + links funcionam!",
                 font=('Arial', 8, 'italic'),
                 foreground="blue").grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        self.texto_mensagem.bind('<KeyRelease>', self.atualizar_contador)
        
        contatos_frame = ttk.LabelFrame(main_frame, text="📋 Contatos", padding="15")
        contatos_frame.grid(row=3, column=0, columnspan=2, sticky="ewns", pady=(0, 15))
        contatos_frame.columnconfigure(1, weight=1)
        contatos_frame.rowconfigure(1, weight=1)
        
        self.btn_arquivo = ttk.Button(contatos_frame,
                                     text="📁 Selecionar Arquivo Excel",
                                     command=self.selecionar_arquivo,
                                     width=25)
        self.btn_arquivo.grid(row=0, column=0, padx=(0, 10), pady=(0, 10))
        
        # Botão para exportar modelo
        self.btn_exportar = ttk.Button(contatos_frame, 
                                      text="📥 Exportar Modelo Excel",
                                      command=self.exportar_modelo,
                                      width=25)
        self.btn_exportar.grid(row=0, column=1, padx=(0, 10), pady=(0, 10))
        
        # Label do arquivo selecionado
        self.label_arquivo = ttk.Label(contatos_frame, 
                                      text="Nenhum arquivo selecionado",
                                      foreground="gray",
                                      font=('Arial', 10))
        self.label_arquivo.grid(row=0, column=2, sticky="ew", pady=(0, 10))
        
        # Treeview para mostrar contatos
        self.tree_contatos = ttk.Treeview(contatos_frame, columns=("numero",), show="headings", height=8)
        self.tree_contatos.heading("numero", text="Números de Telefone")
        self.tree_contatos.column("numero", width=400, anchor="w")
        self.tree_contatos.grid(row=1, column=0, columnspan=3, sticky="ewns", pady=(0, 10))
        
        # Scrollbar para treeview
        tree_scroll = ttk.Scrollbar(contatos_frame, orient="vertical", command=self.tree_contatos.yview)
        tree_scroll.grid(row=1, column=3, sticky="ns", pady=(0, 10))
        self.tree_contatos.configure(yscrollcommand=tree_scroll.set)
        
        # Contador de contatos
        ttk.Label(contatos_frame, 
                 textvariable=self.contador_contatos,
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        # === CONFIGURAÇÕES ===
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configurações", padding="10")
        config_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Modo de envio
        ttk.Label(config_frame, text="Modo de envio:").grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        modo_envio_frame = ttk.Frame(config_frame)
        modo_envio_frame.grid(row=0, column=1, padx=(10, 0), sticky="w", pady=(0, 10))
        
        ttk.Checkbutton(modo_envio_frame,
                       text="📨 Enviar em uma única mensagem",
                       variable=self.envio_unico).pack(anchor="w")
        
        self.label_modo_envio = ttk.Label(modo_envio_frame,
                                         text="Se desmarcado: enviará dividido por parágrafos (quebras duplas \\n\\n)",
                                         font=('Arial', 8, 'italic'),
                                         foreground="blue")
        self.label_modo_envio.pack(anchor="w", pady=(3, 0))
        
        # Pausa entre envios
        ttk.Label(config_frame, text="Pausa entre envios (segundos):").grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        pause_frame = ttk.Frame(config_frame)
        pause_frame.grid(row=1, column=1, padx=(10, 0), sticky="ew", pady=(0, 10))
        pause_frame.columnconfigure(2, weight=1)
        
        ttk.Checkbutton(pause_frame, 
                       text="🎲 Aleatória",
                       variable=self.usar_pausa_aleatoria,
                       command=self.atualizar_modo_pausa).pack(side="left", padx=(0, 10))
        
        pausa_entry = ttk.Entry(pause_frame, textvariable=self.pausa_var, width=8)
        pausa_entry.pack(side="left", padx=(0, 5))
        
        self.pausa_min_label = ttk.Label(pause_frame, text="Mín:", foreground="gray")
        self.pausa_min_label.pack(side="left", padx=(10, 5))
        
        self.pausa_min_entry = ttk.Entry(pause_frame, textvariable=self.pausa_min_var, width=8, state='disabled')
        self.pausa_min_entry.pack(side="left", padx=(0, 10))
        
        self.pausa_max_label = ttk.Label(pause_frame, text="Máx:", foreground="gray")
        self.pausa_max_label.pack(side="left", padx=(0, 5))
        
        self.pausa_max_entry = ttk.Entry(pause_frame, textvariable=self.pausa_max_var, width=8, state='disabled')
        self.pausa_max_entry.pack(side="left")
        
        # Modo de execução do Chrome
        ttk.Label(config_frame, text="Modo de execução:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        chrome_mode_frame = ttk.Frame(config_frame)
        chrome_mode_frame.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        
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
        
        # LabelFrame para log
        log_frame = ttk.LabelFrame(main_frame, text="📝 Log de Atividades", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky="ewns", pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
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
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=60)
        self.log_text.grid(row=1, column=0, sticky="ewns")
        
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
    
    def atualizar_modo_pausa(self):
        """Ativa/desativa campos de pausa aleatória"""
        if self.usar_pausa_aleatoria.get():
            self.pausa_min_entry.config(state='normal')
            self.pausa_max_entry.config(state='normal')
            self.pausa_min_label.config(foreground="black")
            self.pausa_max_label.config(foreground="black")
        else:
            self.pausa_min_entry.config(state='disabled')
            self.pausa_max_entry.config(state='disabled')
            self.pausa_min_label.config(foreground="gray")
            self.pausa_max_label.config(foreground="gray")
    
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
    
    def exportar_modelo(self):
        """Exporta modelo de planilha Excel para preenchimento"""
        try:
            arquivo_modelo, sucesso = exportar_modelo_excel()
            
            if sucesso:
                self.log(f"✅ Modelo exportado com sucesso: {arquivo_modelo}", "success")
                messagebox.showinfo("Sucesso", f"✅ Modelo exportado com sucesso!\n\nArquivo: {arquivo_modelo}\n\nPreencha a coluna 'Numero' com os telefones e carregue o arquivo.")
            else:
                self.log(f"❌ Erro ao exportar modelo: {arquivo_modelo}", "error")
                messagebox.showerror("Erro", f"Erro ao exportar modelo:\n{arquivo_modelo}")
        except Exception as e:
            self.log(f"❌ Erro: {str(e)}", "error")
            messagebox.showerror("Erro", f"Erro ao exportar modelo:\n{str(e)}")
        
    def selecionar_arquivo(self):
        """Seleciona arquivo Excel com lista de contatos e valida números"""
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
                
                # Extrai números e valida
                numeros_brutos = df['Numero'].astype(str).tolist()
                numeros_validos, numeros_invalidos, duplicatas = remover_duplicatas_e_validar(numeros_brutos)
                
                self.lista_numeros = numeros_validos
                
                # Limpa treeview e adiciona novos números
                for item in self.tree_contatos.get_children():
                    self.tree_contatos.delete(item)
                
                for numero in self.lista_numeros:
                    self.tree_contatos.insert("", "end", values=(numero,))
                
                # Atualiza labels
                self.label_arquivo.configure(text=f"✅ {len(self.lista_numeros)} válidos | ⚠️ {len(numeros_invalidos)} inválidos | 🔄 {duplicatas} duplicatas",
                                            foreground="green")
                self.contador_contatos.set(f"Total: {len(self.lista_numeros)} contatos válidos")
                
                # Log detalhado
                self.log(f"📁 Arquivo carregado: {arquivo}", "success")
                self.log(f"✅ Números válidos: {len(self.lista_numeros)}", "success")
                if duplicatas > 0:
                    self.log(f"🔄 Duplicatas removidas: {duplicatas}", "warning")
                if len(numeros_invalidos) > 0:
                    self.log(f"⚠️ Números inválidos: {len(numeros_invalidos)} - {', '.join(numeros_invalidos[:5])}{'...' if len(numeros_invalidos) > 5 else ''}", "warning")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
                self.log(f"Erro ao carregar arquivo: {str(e)}", "error")
                
    def configurar_driver(self):
        """Configura driver Chrome com perfil temporário"""
        try:
            modo_desc = "segundo plano (headless)" if self.modo_headless.get() else "visual"
            self.log(f"Configurando Chrome WebDriver em modo {modo_desc}...", "info")
            
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
                options.add_argument("--window-size=800,600")
                options.add_argument("--window-position=200,200")
                self.log("🚀 Modo segundo plano: Chrome visível para login, depois ficará invisível", "info")
            else:
                options.add_argument("--window-size=1200,800")
                options.add_argument("--window-position=100,100")
                self.log("💻 Modo visual ativado - Chrome será visível", "info")
            
            # Otimizações gerais
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
            
            # Verificar modo de envio do usuário
            if self.envio_unico.get():
                # Enviar TUDO em uma única mensagem
                self.log("📨 Modo: MENSAGEM ÚNICA - enviando tudo junto", "info")
                
                caixa_texto.clear()
                caixa_texto.click()
                caixa_texto.send_keys(mensagem)
                
                time.sleep(2)
                self.log("Enviando mensagem...", "info")
                caixa_texto.send_keys(Keys.ENTER)
                self.log("✅ Mensagem única enviada com sucesso!", "success")
            
            else:
                # Enviar DIVIDIDO por parágrafos (quebras duplas \n\n)
                self.log("📨 Modo: PARÁGRAFOS - enviando em partes separadas", "info")
                
                if '\n\n' in mensagem:
                    # Dividir por parágrafos (quebras duplas)
                    paragrafos = [p.strip() for p in mensagem.split('\n\n') if p.strip()]
                    self.log(f"📝 Mensagem dividida em {len(paragrafos)} parágrafos", "info")
                    
                    # Enviar cada parágrafo separadamente
                    for i, paragrafo in enumerate(paragrafos, 1):
                        self.log(f"📤 Enviando parágrafo {i}/{len(paragrafos)}: {paragrafo[:40]}{'...' if len(paragrafo) > 40 else ''}", "info")
                        
                        caixa_texto.clear()
                        caixa_texto.click()
                        caixa_texto.send_keys(paragrafo.strip())
                        
                        time.sleep(1)
                        caixa_texto.send_keys(Keys.ENTER)
                        
                        # Pausa entre partes
                        if i < len(paragrafos):
                            time.sleep(2)
                    
                    self.log(f"✅ Mensagem completa enviada em {len(paragrafos)} parágrafos!", "success")
                else:
                    # Se não houver parágrafos, enviar tudo junto mesmo assim
                    self.log("📨 Sem parágrafos detectados - enviando como mensagem única", "info")
                    
                    caixa_texto.clear()
                    caixa_texto.click()
                    caixa_texto.send_keys(mensagem)
                    
                    time.sleep(2)
                    self.log("Enviando mensagem...", "info")
                    caixa_texto.send_keys(Keys.ENTER)
                    self.log("✅ Mensagem enviada com sucesso!", "success")
            
            time.sleep(3)
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao enviar mensagem: {str(e)}", "error")
            return False

    def iniciar_automacao(self):
        """Inicia automação completa com validações melhoradas"""
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
            if self.usar_pausa_aleatoria.get():
                pausa_min = int(self.pausa_min_var.get())
                pausa_max = int(self.pausa_max_var.get())
                if pausa_min >= pausa_max:
                    messagebox.showerror("Erro", "Pausa mínima deve ser menor que a máxima!")
                    return
                self.pausa_min = pausa_min
                self.pausa_max = pausa_max
            else:
                pausa = int(self.pausa_var.get())
                self.PAUSA_ENTRE_ENVIOS = pausa
        except:
            messagebox.showerror("Erro", "Valores de pausa devem ser números!")
            return
            
        # Confirmação
        modo_pausa = f"Aleatória ({self.pausa_min_var.get()}s a {self.pausa_max_var.get()}s)" if self.usar_pausa_aleatoria.get() else f"Fixa ({self.pausa_var.get()}s)"
        resposta = messagebox.askyesno(
            "Confirmar Automação",
            f"Iniciar envio para {len(self.lista_numeros)} contatos?\n\n"
            f"Mensagem: {mensagem[:40]}{'...' if len(mensagem) > 40 else ''}\n"
            f"Pausa: {modo_pausa}\n\n"
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
        """Executa teste com um contato e salva histórico"""
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
                self.log(f"📊 Teste salvo em: historico_envios.csv", "info")
                salvar_historico_envio(numero, "✅ Teste Sucesso", mensagem, "Teste executado com sucesso")
                self.status_var.set("Teste concluído com sucesso!")
                messagebox.showinfo("Teste Concluído", f"✅ Mensagem enviada com sucesso para:\n{numero}\n\n📊 Histórico salvo!")
            else:
                self.log("❌ TESTE FALHOU", "error")
                salvar_historico_envio(numero, "❌ Teste Falha", mensagem, "Erro ao enviar teste")
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
                    salvar_historico_envio(numero, "✅ Sucesso", mensagem, "Mensagem enviada com sucesso")
                    self.log(f"✅ Sucesso: {numero}", "success")
                else:
                    falhas += 1
                    salvar_historico_envio(numero, "❌ Falha", mensagem, "Erro ao enviar mensagem")
                    self.log(f"❌ Falha: {numero}", "error")
                    
                # Pausa entre envios (exceto no último)
                if i < total - 1 and self.rodando:
                    if self.usar_pausa_aleatoria.get():
                        pausa = random.randint(self.pausa_min, self.pausa_max)
                        self.log(f"⏰ Pausa aleatória: {pausa}s", "info")
                    else:
                        pausa = self.PAUSA_ENTRE_ENVIOS
                        self.log(f"⏰ Pausa: {pausa}s", "info")
                    
                    self.status_var.set(f"Pausa: {pausa}s...")
                    for segundo in range(pausa):
                        if not self.rodando:
                            break
                        time.sleep(1)
                        self.root.update_idletasks()
                        
            # Relatório final
            taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
            self.log("=" * 50, "info")
            self.log("🎉 AUTOMAÇÃO CONCLUÍDA!", "success")
            self.log(f"✅ Sucessos: {sucessos}/{total} ({taxa_sucesso:.1f}%)", "success")
            self.log(f"❌ Falhas: {falhas}/{total}", "error" if falhas > 0 else "info")
            self.log(f"📊 Histórico salvo em: historico_envios.csv", "info")
            self.log("=" * 50, "info")
            
            self.status_var.set(f"Concluído: {sucessos} sucessos, {falhas} falhas")
            
            messagebox.showinfo(
                "Automação Concluída",
                f"✅ Envios finalizados!\n\n"
                f"✅ Sucessos: {sucessos}/{total} ({taxa_sucesso:.1f}%)\n"
                f"❌ Falhas: {falhas}\n\n"
                f"📊 Histórico salvo em: historico_envios.csv"
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