#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatizador de Envio de Mensagens WhatsApp
Feito pra facilitar o envio em massa pelo WhatsApp Web
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# ==================== FUNÇÕES AUXILIARES ====================

def arrumar_numero_telefone(telefone):
    """
    Arruma o número de telefone pro formato que o WhatsApp entende
    Aceita: (11) 99999-9999, 11999999999, 5511999999999
    Retorna sempre: 5511999999999 (com código do Brasil)
    """
    if not telefone:
        return None
    
    telefone_limpo = str(telefone).strip()
    # Tira tudo que não é número
    so_numeros = re.sub(r'[^\d]', '', telefone_limpo)
    
    # Já tem o 55 na frente
    if len(so_numeros) == 13 and so_numeros.startswith('55'):
        return so_numeros
    # Falta o 55, então adiciona
    elif len(so_numeros) in (10, 11):
        return '55' + so_numeros
    
    return None

def limpar_lista_telefones(lista_telefones):
    """
    Limpa a lista de telefones: remove duplicados e separa os válidos dos inválidos
    Retorna: (telefones_validos, telefones_invalidos, quantos_eram_duplicados)
    """
    telefones_ok = []
    telefones_ruins = []
    ja_vimos = set()
    quantos_duplicados = 0
    
    for telefone in lista_telefones:
        telefone_arrumado = arrumar_numero_telefone(telefone)
        
        if telefone_arrumado:
            if telefone_arrumado not in ja_vimos:
                telefones_ok.append(telefone_arrumado)
                ja_vimos.add(telefone_arrumado)
            else:
                quantos_duplicados += 1
        else:
            telefones_ruins.append(str(telefone))
    
    return telefones_ok, telefones_ruins, quantos_duplicados

def salvar_no_historico(telefone, deu_certo, mensagem="", observacao=""):
    """
    Salva o resultado do envio num arquivo CSV pra poder ver depois o que aconteceu
    Útil pra saber quantos deram certo e quantos falharam
    """
    arquivo_csv = "historico_envios.csv"
    
    # Se o arquivo não existe ainda, precisa criar ele com o cabeçalho
    arquivo_novo = not os.path.exists(arquivo_csv)
    
    try:
        with open(arquivo_csv, 'a', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            
            if arquivo_novo:
                escritor.writerow(['Data', 'Hora', 'Telefone', 'Status', 'Observacao', 'Tamanho_Msg'])
            
            agora = datetime.now()
            data = agora.strftime('%d/%m/%Y')
            hora = agora.strftime('%H:%M:%S')
            
            escritor.writerow([data, hora, telefone, deu_certo, observacao, len(mensagem)])
    except Exception as erro:
        print(f"[ERRO] Não consegui salvar no arquivo CSV: {str(erro)}")

def criar_planilha_modelo():
    """
    Cria uma planilha de exemplo pro usuário baixar e preencher
    Facilita pra quem não sabe como montar a planilha
    """
    try:
        # Exemplo com 3 telefones pra pessoa ver como é
        exemplos = pd.DataFrame({
            'Numero': ['5511999999999', '5521998888888', '5585987777777']
        })
        
        # Salva na pasta Documentos do Windows
        pasta_docs = os.path.join(os.path.expanduser('~'), 'Documents')
        arquivo_modelo = os.path.join(pasta_docs, "MODELO_CONTATOS.xlsx")
        exemplos.to_excel(arquivo_modelo, index=False, sheet_name='Contatos')
        
        # Abre a pasta onde salvou
        os.startfile(pasta_docs)
        
        return arquivo_modelo, True
    except Exception as erro:
        print(f"[ERRO] Problema ao criar planilha modelo: {str(erro)}")
        return str(erro), False

class AutomatizadorWhatsApp:
    """
    Sistema que automatiza envio de mensagens em massa pelo WhatsApp Web
    Usa Selenium pra controlar o navegador Chrome e enviar as mensagens
    """
    def __init__(self):
        self.ta_rodando = False
        self.navegador = None
        self.lista_telefones = []
        # Guarda quais logs já mostramos pra não ficar repetindo no console
        self.logs_ja_mostrados = set()
        
        # Tempo de espera entre cada envio (em segundos)
        # Coloquei 20 segundos pra não tomar ban do WhatsApp
        self.tempo_espera_entre_envios = 20
        
        self.janela = tk.Tk()
        self.janela.title("🚀 Automatizador WhatsApp - Envio em Massa")
        self.janela.geometry("1200x900")
        self.janela.resizable(True, True)
        try:
            self.janela.state('zoomed')  # Maximiza a janela no Windows
        except:
            pass  # Se não funcionar (Linux/Mac), deixa pra lá
        
        # Variáveis que controlam os campos da interface
        self.texto_status = tk.StringVar(value="Pronto pra começar")
        self.tempo_fixo = tk.StringVar(value="20")
        self.tempo_minimo = tk.StringVar(value="15")
        self.tempo_maximo = tk.StringVar(value="25")
        self.usar_tempo_aleatorio = tk.BooleanVar(value=False)
        self.enviar_tudo_junto = tk.BooleanVar(value=True)  # Se True: mensagem única, se False: divide por parágrafo
        self.contador_caracteres = tk.StringVar(value="Caracteres: 0")
        self.contador_telefones = tk.StringVar(value="Total: 0 telefones")
        self.log_expandido = False
        self.rodar_chrome_escondido = tk.BooleanVar(value=False)
        
        self.montar_tela()
        
    def montar_tela(self):
        """Monta a tela principal do programa"""
        # Estilo dos botões
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       background='#007ACC',
                       foreground='white')
        estilo.map('Accent.TButton',
                 background=[('active', '#005A9E')])
        
        # Canvas com scroll pra poder rolar a tela
        canvas = tk.Canvas(self.janela, bg="white", highlightthickness=0)
        barra_scroll = ttk.Scrollbar(self.janela, orient="vertical", command=canvas.yview)
        self.frame_scroll = ttk.Frame(canvas)
        
        id_canvas = canvas.create_window((0, 0), window=self.frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=barra_scroll.set)
        
        # Funções pra ajustar o scroll quando a janela muda de tamanho
        def ajustar_largura(event):
            canvas.itemconfig(id_canvas, width=event.width)
            
        def ajustar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.frame_scroll.bind("<Configure>", ajustar_scroll)
        canvas.bind("<Configure>", ajustar_largura)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        barra_scroll.grid(row=0, column=1, sticky="ns")
        
        self.janela.columnconfigure(0, weight=1)
        self.janela.rowconfigure(0, weight=1)
        
        # Scroll com a rodinha do mouse
        def rolar_mouse(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", rolar_mouse)
        
        frame_principal = ttk.Frame(self.frame_scroll, padding="10")
        frame_principal.pack(fill="both", expand=True)
        
        frame_principal.columnconfigure(0, weight=1)
        for i in range(7):
            frame_principal.rowconfigure(i, weight=0)
        frame_principal.rowconfigure(6, weight=1)
        
        titulo_label = ttk.Label(frame_principal, 
                               text="🚀 Motor de Campanha WhatsApp",
                               font=('Arial', 18, 'bold'))
        titulo_label.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky="ew")
        
        # Avisos operacionais críticos
        frame_avisos = ttk.LabelFrame(frame_principal, text="⚠️ AVISOS OPERACIONAIS", padding="15")
        frame_avisos.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 25))
        frame_avisos.columnconfigure(0, weight=1)
        
        texto_avisos = ttk.Label(frame_avisos, 
                                text="⚠️ Perfil Chrome temporário será criado\n"
                                     "⚠️ QR Code scan obrigatório a cada execução\n"
                                     "⚠️ Taxa de envio limitada para evitar detecção de bot",
                                foreground="red")
        texto_avisos.grid(row=0, column=0, sticky="ew")
        
        frame_corpo_mensagem = ttk.LabelFrame(frame_principal, text="💬 Payload da Campanha", padding="15")
        frame_corpo_mensagem.grid(row=2, column=0, columnspan=2, sticky="ewns", pady=(0, 15))
        frame_corpo_mensagem.columnconfigure(0, weight=1)
        
        self.corpo_campanha = tk.Text(frame_corpo_mensagem, height=6, wrap=tk.WORD, font=('Arial', 10))
        self.corpo_campanha.grid(row=0, column=0, sticky="ewns", pady=(0, 10))
        
        payload_exemplo = ("Ola! Esta e uma mensagem de teste automatizada.\n\n"
                       "*Funcionalidades suportadas:*\n"
                       "- Links: https://www.google.com\n"
                       "- *Negrito*, _italico_, ~riscado~\n"
                       "- Quebras de linha\n\n"
                       "Por favor, ignore se ja recebeu. Estou testando um novo sistema.\n\n"
                       "Obrigado!")
        self.corpo_campanha.insert("1.0", payload_exemplo)
        
        frame_info_payload = ttk.Frame(frame_corpo_mensagem)
        frame_info_payload.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        frame_info_payload.columnconfigure(1, weight=1)
        
        ttk.Label(frame_info_payload, textvariable=self.contador_caracteres, font=('Arial', 9)).grid(row=0, column=0, sticky="ew")
        
        ttk.Label(frame_info_payload, 
                 text="💡 Formatação WhatsApp: *negrito* _itálico_ ~riscado~ + URLs autolink",
                 font=('Arial', 8, 'italic'),
                 foreground="blue").grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        self.corpo_campanha.bind('<KeyRelease>', self.atualizar_contador_caracteres)
        
        frame_destinatarios = ttk.LabelFrame(frame_principal, text="📋 Fila de Destinatários", padding="15")
        frame_destinatarios.grid(row=3, column=0, columnspan=2, sticky="ewns", pady=(0, 15))
        frame_destinatarios.columnconfigure(1, weight=1)
        frame_destinatarios.rowconfigure(1, weight=1)
        
        self.btn_upload_planilha = ttk.Button(frame_destinatarios,
                                     text="📁 Carregar Planilha",
                                     command=self.carregar_planilha_destinatarios,
                                     width=25)
        self.btn_upload_planilha.grid(row=0, column=0, padx=(0, 10), pady=(0, 10))
        
        self.btn_gerar_template = ttk.Button(frame_destinatarios, 
                                      text="📥 Baixar Modelo Excel",
                                      command=self.baixar_modelo_excel,
                                      width=25)
        self.btn_gerar_template.grid(row=0, column=1, padx=(0, 10), pady=(0, 10))
        
        self.label_arquivo_carregado = ttk.Label(frame_destinatarios, 
                                      text="Nenhuma campanha carregada",
                                      foreground="gray",
                                      font=('Arial', 10))
        self.label_arquivo_carregado.grid(row=0, column=2, sticky="ew", pady=(0, 10))
        
        self.grid_destinatarios = ttk.Treeview(frame_destinatarios, columns=("msisdn",), show="headings", height=8)
        self.grid_destinatarios.heading("msisdn", text="Telefones Normalizados")
        self.grid_destinatarios.column("msisdn", width=400, anchor="w")
        self.grid_destinatarios.grid(row=1, column=0, columnspan=3, sticky="ewns", pady=(0, 10))
        
        scrollbar_grid = ttk.Scrollbar(frame_destinatarios, orient="vertical", command=self.grid_destinatarios.yview)
        scrollbar_grid.grid(row=1, column=3, sticky="ns", pady=(0, 10))
        self.grid_destinatarios.configure(yscrollcommand=scrollbar_grid.set)
        
        ttk.Label(frame_destinatarios, 
                 textvariable=self.contador_telefones,
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        # Configurações de throttling - calibrado contra detecção de bot do WhatsApp
        frame_configuracoes = ttk.LabelFrame(frame_principal, text="⚙️ Anti-Ban", padding="10")
        frame_configuracoes.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        frame_configuracoes.columnconfigure(1, weight=1)
        
        ttk.Label(frame_configuracoes, text="Estratégia de envio:").grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        frame_modo_envio = ttk.Frame(frame_configuracoes)
        frame_modo_envio.grid(row=0, column=1, padx=(10, 0), sticky="w", pady=(0, 10))
        
        ttk.Checkbutton(frame_modo_envio,
                       text="📨 Mensagem Única",
                       variable=self.enviar_tudo_junto).pack(anchor="w")
        
        self.label_modo_envio_hint = ttk.Label(frame_modo_envio,
                                         text="Desmarcado: split automático por parágrafos (quebras \\n\\n)",
                                         font=('Arial', 8, 'italic'),
                                         foreground="blue")
        self.label_modo_envio_hint.pack(anchor="w", pady=(3, 0))
        
        # Throttling configura delay entre mensagens - valores < 15s aumentam risco de ban
        ttk.Label(frame_configuracoes, text="Delay entre envios (segundos):").grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        frame_throttle = ttk.Frame(frame_configuracoes)
        frame_throttle.grid(row=1, column=1, padx=(10, 0), sticky="ew", pady=(0, 10))
        frame_throttle.columnconfigure(2, weight=1)
        
        ttk.Checkbutton(frame_throttle, 
                       text="🎲 Randomizar",
                       variable=self.usar_tempo_aleatorio,
                       command=self.atualizar_modo_throttle).pack(side="left", padx=(0, 10))
        
        entry_throttle_fixo = ttk.Entry(frame_throttle, textvariable=self.tempo_fixo, width=8)
        entry_throttle_fixo.pack(side="left", padx=(0, 5))
        
        self.label_throttle_min = ttk.Label(frame_throttle, text="Mín:", foreground="gray")
        self.label_throttle_min.pack(side="left", padx=(10, 5))
        
        self.entry_throttle_min = ttk.Entry(frame_throttle, textvariable=self.tempo_minimo, width=8, state='disabled')
        self.entry_throttle_min.pack(side="left", padx=(0, 10))
        
        self.label_throttle_max = ttk.Label(frame_throttle, text="Máx:", foreground="gray")
        self.label_throttle_max.pack(side="left", padx=(0, 5))
        
        self.entry_throttle_max = ttk.Entry(frame_throttle, textvariable=self.tempo_maximo, width=8, state='disabled')
        self.entry_throttle_max.pack(side="left")
        
        ttk.Label(frame_configuracoes, text="Modo de execução:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        frame_modo_browser = ttk.Frame(frame_configuracoes)
        frame_modo_browser.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        
        ttk.Checkbutton(frame_modo_browser, 
                       text="🔇 Chrome em segundo plano (performance > visibilidade)",
                       variable=self.rodar_chrome_escondido,
                       command=self.atualizar_label_modo_browser).pack(anchor="w")
        
        self.label_modo_browser_hint = ttk.Label(frame_modo_browser, 
                                   text="💻 Modo atual: Chrome visível (útil para debug)",
                                   font=('Arial', 8, 'italic'),
                                   foreground="blue")
        self.label_modo_browser_hint.pack(anchor="w", pady=(5, 0))
        
        # === CONTROLES ===
        controls_frame = ttk.LabelFrame(frame_principal, text="🎛️ Controles de Automação", padding="15")
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
        self.status_label = ttk.Label(controls_frame, textvariable=self.texto_status)
        self.status_label.grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        frame_log_auditoria = ttk.LabelFrame(frame_principal, text="📝 Log de Execução", padding="10")
        frame_log_auditoria.grid(row=6, column=0, columnspan=2, sticky="ewns", pady=(0, 10))
        frame_log_auditoria.columnconfigure(0, weight=1)
        frame_log_auditoria.rowconfigure(1, weight=1)
        
        frame_controles_log = ttk.Frame(frame_log_auditoria)
        frame_controles_log.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        frame_controles_log.columnconfigure(1, weight=1)
        
        self.btn_toggle_log = ttk.Button(frame_controles_log,
                                        text="🔽 Expandir Log",
                                        command=self.toggle_area_log)
        self.btn_toggle_log.grid(row=0, column=0, sticky="ew")
        
        ttk.Button(frame_controles_log,
                  text="🗑️ Limpar",
                  command=self.limpar_console_log).grid(row=0, column=2, sticky="ew", padx=(10, 0))
        
        self.console_auditoria = scrolledtext.ScrolledText(frame_log_auditoria, height=10, width=60)
        self.console_auditoria.grid(row=1, column=0, sticky="ewns")
        
        # Tags para colorização semântica dos logs
        self.console_auditoria.tag_configure("success", foreground="green")
        self.console_auditoria.tag_configure("error", foreground="red")
        self.console_auditoria.tag_configure("warning", foreground="orange")
        self.console_auditoria.tag_configure("info", foreground="blue")
        
        self.console_auditoria.configure(height=7)
        
        separador_rodape = ttk.Separator(frame_principal, orient='horizontal')
        separador_rodape.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        label_rodape = ttk.Label(frame_principal,
                                text="Desenvolvido por Victor Vasconcelos - 61984385187",
                                font=('Arial', 9, 'italic'),
                                foreground="gray")
        label_rodape.grid(row=8, column=0, columnspan=2)
        
        self.atualizar_contador_caracteres()
        
    def atualizar_label_modo_browser(self):
        """Atualiza hint visual do modo de execução do browser"""
        if self.rodar_chrome_escondido.get():
            self.label_modo_browser_hint.configure(
                text="🚀 Browser em background: execução otimizada sem UI",
                foreground="green"
            )
        else:
            self.label_modo_browser_hint.configure(
                text="💻 Modo atual: Chrome visível (útil para debug)",
                foreground="blue"
            )
    
    def atualizar_modo_throttle(self):
        """Toggle controles de throttling randomizado"""
        if self.usar_tempo_aleatorio.get():
            self.entry_throttle_min.config(state='normal')
            self.entry_throttle_max.config(state='normal')
            self.label_throttle_min.config(foreground="black")
            self.label_throttle_max.config(foreground="black")
        else:
            self.entry_throttle_min.config(state='disabled')
            self.entry_throttle_max.config(state='disabled')
            self.label_throttle_min.config(foreground="gray")
            self.label_throttle_max.config(foreground="gray")
    
    def atualizar_contador_caracteres(self, event=None):
        """Recalcula tamanho do payload em tempo real"""
        payload_atual = self.corpo_campanha.get("1.0", tk.END).strip()
        self.contador_caracteres.set(f"Caracteres: {len(payload_atual)}")
        
    def toggle_area_log(self):
        """Expande/colapsa console de auditoria"""
        if not self.log_area_expandida:
            self.console_auditoria.configure(height=12)
            self.btn_toggle_log.configure(text="🔼 Recolher Log")
            self.log_area_expandida = True
        else:
            self.console_auditoria.configure(height=4)
            self.btn_toggle_log.configure(text="🔽 Expandir Log")
            self.log_area_expandida = False
            
    def limpar_console_log(self):
        """Flush completo do buffer de logs"""
        self.console_auditoria.delete("1.0", tk.END)
        self.escrever_log("Console de auditoria reiniciado", "info")
        
    def escrever_log(self, mensagem, tipo="info", nao_repetir=False):
        # nao_repetir serve pra evitar spammar a mesma mensagem 500x
        # tipo bem útil quando o WhatsApp começa a buggar
        if nao_repetir:
            if mensagem in self.logs_ja_mostrados:
                return
            else:
                self.logs_ja_mostrados.add(mensagem)
        
        hora_agora = time.strftime("%H:%M:%S")
        linha_formatada = f"[{hora_agora}] {mensagem}\n"
        
        self.console_auditoria.insert(tk.END, linha_formatada, tipo)
        self.console_auditoria.see(tk.END)
        self.janela.update_idletasks()
    
    def limpar_cache_logs(self):
        # Limpa o cache dos logs repetidos pra começar tudo novo
        self.logs_ja_mostrados.clear()
    
    def baixar_modelo_excel(self):
        # Cria aquele modelo de Excel já bonitinho pro usuário não ter que ficar adivinhando
        try:
            caminho_exportado, deu_certo = criar_planilha_modelo()
            
            if deu_certo:
                self.escrever_log(f"✅ Modelo criado: {caminho_exportado}", "success")
                messagebox.showinfo("Modelo Criado", 
                    f"✅ Pronto! Modelo do Excel criado com sucesso!\n\nLocal: {caminho_exportado}\n\nPreenche a coluna 'Numero' e depois carrega aqui.")
            else:
                self.escrever_log(f"❌ Erro ao criar modelo: {caminho_exportado}", "error")
                messagebox.showerror("Erro", f"Não consegui gerar o modelo:\n{caminho_exportado}")
        except IOError as erro:
            self.escrever_log(f"❌ Erro grave: {str(erro)}", "error")
            messagebox.showerror("Erro", f"Deu ruim ao exportar:\n{str(erro)}")
        
    def carregar_planilha_destinatarios(self):
        """
        Carrega fila de destinatários de Excel, normaliza MSISDNs e dedup licada
        Rejeita planilhas sem coluna 'Numero' - padrão estabelecido em docs
        """
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecionar planilha de campanha",
            filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos", "*.*")]
        )
        
        if not caminho_arquivo:
            return
            
        try:
            dataframe_campanha = pd.read_excel(caminho_arquivo)
            
            # Guard clause: valida schema obrigatório
            if 'Numero' not in dataframe_campanha.columns:
                messagebox.showerror("Schema Inválido", 
                    "Planilha rejeitada: coluna 'Numero' ausente.\n\nFaça download do template para ver estrutura esperada.")
                return
            
            msisdns_brutos = dataframe_campanha['Numero'].astype(str).tolist()
            fila_valida, fila_rejeitada, qtd_duplicatas = limpar_lista_telefones(msisdns_brutos)
            
            self.lista_telefones = fila_valida
            
            # Limpa grid e popula com MSISDNs normalizados
            for item_antigo in self.grid_destinatarios.get_children():
                self.grid_destinatarios.delete(item_antigo)
            
            for msisdn in self.lista_telefones:
                self.grid_destinatarios.insert("", "end", values=(msisdn,))
            
            # UI feedback detalhado
            resumo_validacao = f"✅ {len(fila_valida)} válidos | ⚠️ {len(fila_rejeitada)} rejeitados | 🔄 {qtd_duplicatas} duplicatas"
            self.label_arquivo_carregado.configure(text=resumo_validacao, foreground="green")
            self.contador_telefones.set(f"Total: {len(fila_valida)} destinatários únicos")
            
            # Auditoria estruturada
            self.escrever_log(f"[CAMPANHA-CARREGADA] Arquivo: {caminho_arquivo}", "success")
            self.escrever_log(f"[VALIDACAO] {len(fila_valida)} MSISDNs normalizados", "success")
            
            if qtd_duplicatas > 0:
                self.escrever_log(f"[DEDUP] {qtd_duplicatas} duplicatas removidas automaticamente", "warning")
            
            if len(fila_rejeitada) > 0:
                amostra_rejeitados = ', '.join(fila_rejeitada[:5])
                sufixo = '...' if len(fila_rejeitada) > 5 else ''
                self.escrever_log(f"[VALIDACAO-FALHA] {len(fila_rejeitada)} rejeitados: {amostra_rejeitados}{sufixo}", "warning")
            
        except FileNotFoundError:
            messagebox.showerror("Arquivo Não Encontrado", f"Não foi possível abrir:\n{caminho_arquivo}")
            self.escrever_log(f"[IO-ERRO] Arquivo inacessível: {caminho_arquivo}", "error")
        except Exception as err_geral:
            messagebox.showerror("Erro ao Processar", f"Falha ao carregar planilha:\n{str(err_geral)}")
            self.escrever_log(f"[PARSE-ERRO] {str(err_geral)}", "error")
                
    def configurar_chrome(self):
        """
        Prepara o Chrome pra funcionar com WhatsApp Web
        Usa uma pasta temporária porque senão o WhatsApp detecta e bloqueia
        """
        try:
            modo = "escondido" if self.rodar_chrome_escondido.get() else "visível"
            print(f"--> Configurando Chrome ({modo})...")
            
            # Cria uma pasta temporária pro perfil do Chrome
            # Tem que ser temporária senão WhatsApp detecta que é automação e bane em 2 dias
            pasta_temp = tempfile.mkdtemp(prefix="whatsapp_auto_")
            print(f"    Pasta temporária criada: {pasta_temp}")
            
            config = Options()
            config.add_argument(f"--user-data-dir={pasta_temp}")
            config.add_argument("--profile-directory=AutoProfile")
            
            # Essas configs escondem que é automação
            # Se não colocar isso aqui, o WhatsApp detecta pela API do Selenium
            config.add_argument("--disable-blink-features=AutomationControlled")
            config.add_experimental_option("excludeSwitches", ["enable-automation"])
            config.add_experimental_option('useAutomationExtension', False)
            config.add_argument("--disable-extensions")
            config.add_argument("--no-sandbox")
            config.add_argument("--disable-dev-shm-usage")
            
            # Finge ser um Chrome normal (não automação)
            config.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            if self.rodar_chrome_escondido.get():
                # Deixa pequeno e posiciona fora da tela
                # Não pode usar headless puro porque o WhatsApp detecta pelo JavaScript
                config.add_argument("--window-size=800,600")
                config.add_argument("--window-position=200,200")
                print("    Modo: Vai aparecer no início (pro QR Code) e depois esconde")
            else:
                config.add_argument("--window-size=1200,800")
                config.add_argument("--window-position=100,100")
                print("    Modo: Chrome vai ficar visível o tempo todo")
            
            # Desliga um monte de coisa pra deixar mais rápido
            config.add_argument("--disable-background-networking")
            config.add_argument("--disable-background-timer-throttling")
            config.add_argument("--disable-client-side-phishing-detection")
            config.add_argument("--disable-default-apps")
            config.add_argument("--disable-hang-monitor")
            config.add_argument("--disable-popup-blocking")
            config.add_argument("--disable-prompt-on-repost")
            config.add_argument("--disable-sync")
            config.add_argument("--metrics-recording-only")
            config.add_argument("--no-first-run")
            config.add_argument("--safebrowsing-disable-auto-update")
            config.add_argument("--password-store=basic")
            config.add_argument("--disable-gpu")
            config.add_argument("--disable-web-security")
            config.add_argument("--allow-running-insecure-content")
            
            servico = Service(ChromeDriverManager().install())
            navegador = webdriver.Chrome(service=servico, options=config)
            
            # Remove a propriedade que mostra que é automação
            navegador.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✓ Chrome configurado e pronto!")
            
            if not self.rodar_chrome_escondido.get():
                self.escrever_log("[QR-REQUIRED] Scan de QR Code necessário para autenticação", "info")
            else:
                self.escrever_log("[QR-REQUIRED] QR Code carregará automaticamente - aguarde instruções", "info")
            
            return navegador
                
        except Exception as err_driver:
            self.escrever_log(f"[BROWSER-CRITICAL] Falha fatal ao iniciar Chrome: {str(err_driver)}", "error")
            return None
    def verificar_se_ta_logado(self, navegador):
        # Checa se o WhatsApp Web tá logado olhando se tem os elementos da tela principal
        # O WhatsApp muda o HTML direto então testa vários seletores diferentes
        try:
            # Primeiro checa se TEM o QR Code - se tiver, não tá logado
            seletores_qr = [
                "//div[@data-testid='qrcode']",
                "//canvas[contains(@aria-label, 'Scan')]",
                "//div[contains(@class, 'qr-code')]"
            ]
            
            for seletor in seletores_qr:
                try:
                    elementos_qr = navegador.find_elements(By.XPATH, seletor)
                    for elemento in elementos_qr:
                        if elemento.is_displayed():
                            self.escrever_log("🔍 QR Code ainda tá na tela - não logou ainda", "info")
                            return False
                except:
                    continue
            
            # Se não tem QR Code, procura pelos elementos da tela logada
            # Testa vários porque o WhatsApp fica mudando isso sem avisar
            seletores_tela_logada = [
                "//div[@data-testid='chat-list']",          # Lista de conversas
                "//div[contains(@class, 'chat-list')]",
                "//div[@data-testid='chatlist-header']",    # Header de cima
                "//header[contains(@class, 'app-header')]",
                "//div[@data-testid='search-input']",       # Busca de contatos
                "//div[contains(@title, 'Pesquisar')]",
                "//div[@data-testid='menu']",               # Menu de config
                "//span[contains(@title, 'Menu')]",
                "//div[contains(@class, 'chat') and @data-testid]",
                "//div[contains(@class, 'app-wrapper-web')]//div[contains(@class, 'two')]"
            ]
            
            contador_elementos = 0
            for seletor in seletores_tela_logada:
                try:
                    elementos = navegador.find_elements(By.XPATH, seletor)
                    for elem in elementos:
                        if elem.is_displayed():
                            contador_elementos += 1
                            break
                except:
                    continue
            
            # Se achou pelo menos 1 elemento válido, consideramos como logado
            # Melhor ser flexível do que travar porque o WhatsApp mudou 1 div
            if contador_elementos >= 1:
                return True
            else:
                return False
                
        except Exception as erro:
            self.escrever_log(f"❌ Erro ao verificar login: {str(erro)}", "error")
            return False
            
    def fazer_login_whatsapp(self, navegador, tempo_max_segundos=300):
        """
        Aguarda autenticação via QR Code no WhatsApp Web
        Timeout de 5min é trade-off entre UX e pragmatismo operacional
        """
        try:
            self.escrever_log("[SESSAO-WA] Aguardando hidratação inicial do DOM...", "info")
            
            # WhatsApp Web tem SPA React pesado - aguarda readyState complete
            wait = WebDriverWait(navegador, 45)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(3)  # Buffer extra - DOM completo != React totalmente montado
            
            self.escrever_log("[SESSAO-WA] Aguardando componentes React materializarem...", "info")
            try:
                # Espera qualquer um dos componentes principais renderizar
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='qrcode']")),
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='chat-list']")),
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'app-wrapper-web')]")),
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='chatlist-header']"))
                ))
                self.escrever_log("[SESSAO-WA-OK] Interface React carregada", "success")
            except TimeoutException:
                self.escrever_log("[SESSAO-WA-SLOW] Interface demorou, mas prosseguindo...", "warning")
            
            time.sleep(5)
            
            # Fast-path: verifica se sessão já existe (cookies persistentes)
            self.escrever_log("[AUTH-CHECK] Verificando sessão pré-existente...", "info")
            if self.verificar_se_ta_logado(navegador):
                self.escrever_log("[AUTH-CACHED] Sessão já ativa - QR Code desnecessário", "success")
                time.sleep(5)
                return True
            
            # Main path: aguarda autenticação via QR Code
            self.escrever_log("[QR-SCAN-REQUIRED] Sessão não encontrada - QR Code scan necessário", "warning")
            self.escrever_log(f"[TIMEOUT-CONFIG] Aguardando até {tempo_max_segundos//60}min para scan", "info")
            
            if self.rodar_chrome_escondido.get():
                self.escrever_log("[STEALTH-MODE] Browser visível para QR, depois vai para background", "info")
                self.escrever_log("[ACTION-REQUIRED] Escaneie QR Code - browser será ocultado após auth", "warning")
            
            timestamp_inicio = time.time()
            timestamp_ultima_checagem = 0
            flag_qr_detectado = False
            flag_log_qr_emitido = False
            tentativas_checagem = 0
            flag_log_aguardo_emitido = False
            
            while time.time() - timestamp_inicio < tempo_max_segundos:
                # Guard clause: campanha abortada por usuário
                if not self.ta_rodando:
                    self.escrever_log("[AUTH-ABORTED] Processo cancelado manualmente", "warning")
                    return False
                
                # Detecta QR Code visível e notifica usuário (log consolidado)
                if not flag_qr_detectado and not flag_log_qr_emitido:
                    try:
                        elementos_qr = navegador.find_elements(By.XPATH, 
                            "//div[@data-testid='qrcode'] | //canvas[contains(@aria-label, 'Scan')]")
                        for elem_qr in elementos_qr:
                            if elem_qr.is_displayed():
                                self.escrever_log("[QR-CODE-VISIBLE] QR Code renderizado - pronto para scan", "info", nao_repetir=True)
                                flag_qr_detectado = True
                                flag_log_qr_emitido = True
                                break
                    except:
                        pass
                
                # Polling de auth a cada 3s - balanceamento entre responsividade e overhead
                if time.time() - timestamp_ultima_checagem > 3:
                    tentativas_checagem += 1
                    
                    if self.verificar_se_ta_logado(navegador):
                        # Conta elementos UI visíveis para métrica de confiabilidade
                        seletores_metricas = [
                            "//div[@data-testid='chat-list']",
                            "//div[@data-testid='chatlist-header']", 
                            "//div[contains(@class, 'app-wrapper-web')]//div[contains(@class, 'two')]"
                        ]
                        qtd_elementos_ui = len([el for sel in seletores_metricas 
                                               for el in navegador.find_elements(By.XPATH, sel) if el.is_displayed()])
                        
                        self.escrever_log(f"[AUTH-SUCCESS] Login detectado! ({qtd_elementos_ui} elementos UI validados)", "success")
                        self.escrever_log("[STABILIZATION] Aguardando interface estabilizar...", "success")
                        
                        # Período de estabilização - WhatsApp carrega chats assincronamente
                        for i in range(15):
                            if not self.ta_rodando:
                                return False
                            time.sleep(1)
                            self.escrever_log(f"[STABILIZATION] Progresso: {i+1}/15s", "info")
                            self.janela.update_idletasks()
                        
                        # Verificação final de persistência de sessão
                        if self.verificar_se_ta_logado(navegador):
                            self.escrever_log("[AUTH-STABLE] Sessão confirmada e estável", "success")
                            
                            # Modo stealth: oculta browser após autenticação bem-sucedida
                            if self.rodar_chrome_escondido.get():
                                try:
                                    self.escrever_log("[STEALTH-ACTIVATE] Ocultando browser...", "info")
                                    
                                    navegador.minimize_window()
                                    time.sleep(1)
                                    
                                    # Posicionamento off-screen como fallback
                                    navegador.set_window_position(-2000, -2000)
                                    navegador.set_window_size(100, 100)
                                    time.sleep(1)
                                    
                                    self.escrever_log("[STEALTH-OK] Browser em background - execução invisível", "success")
                                except Exception as err_stealth:
                                    self.escrever_log(f"[STEALTH-PARTIAL] Ocultação parcial: {str(err_stealth)}", "warning")
                            
                            time.sleep(3)
                            return True
                        else:
                            self.escrever_log("[AUTH-UNSTABLE] Interface ainda instável, aguardando...", "warning")
                    else:
                        # Log consolidado de espera (evita flood)
                        if not flag_log_aguardo_emitido:
                            self.escrever_log("[AUTH-PENDING] Aguardando scan de QR Code...", "info", nao_repetir=True)
                            flag_log_aguardo_emitido = True
                    
                    timestamp_ultima_checagem = time.time()
                
                # Status periódico a cada 30s para feedback ao usuário
                tempo_decorrido = int(time.time() - timestamp_inicio)
                if tempo_decorrido % 30 == 0 and tempo_decorrido > 0:
                    minutos_restantes = int((tempo_max_segundos - tempo_decorrido) / 60)
                    segundos_restantes = (tempo_max_segundos - tempo_decorrido) % 60
                    self.escrever_log(f"[TIMEOUT-STATUS] Tempo restante: {minutos_restantes}m {segundos_restantes}s", "info")
                
                time.sleep(1)
                self.janela.update_idletasks()
            
            # Timeout atingido - falha de autenticação
            self.escrever_log("[AUTH-TIMEOUT] Tempo limite excedido - sessão não estabelecida", "error")
            return False
            
        except Exception as err_auth:
            self.escrever_log(f"[AUTH-EXCEPTION] Erro crítico em autenticação: {str(err_auth)}", "error")
            return False
    def mandar_mensagem(self, navegador, numero_destino, texto_mensagem):
        # Manda mensagem pro número usando aquela URL do WhatsApp Web
        # Demora ~8s porque o React precisa carregar tudo
        try:
            self.escrever_log(f"📤 Mandando mensagem pro {numero_destino}...", "info")
            
            url_conversa = f"https://web.whatsapp.com/send?phone={numero_destino}"
            self.escrever_log(f"🌐 Abrindo conversa: {url_conversa}", "info")
            
            navegador.get(url_conversa)
            
            # Precisa esperar 8 segundos senão o WhatsApp nem terminou de carregar
            self.escrever_log("⏳ Esperando WhatsApp carregar (~8s)...", "info", nao_repetir=True)
            time.sleep(8)
            
            # As vezes aparece aquele popup chato "Usar WhatsApp Web"
            try:
                self.escrever_log("🔍 Procurando popups irritantes...", "info", nao_repetir=True)
                botao_popup = WebDriverWait(navegador, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Usar o WhatsApp Web') or contains(text(), 'Use WhatsApp Web')]"))
                )
                botao_popup.click()
                time.sleep(3)
                self.escrever_log("✅ Fechei o popup", "success", nao_repetir=True)
            except TimeoutException:
                self.escrever_log("👍 Sem popup pra fechar", "info", nao_repetir=True)
            
            # Procura onde digitar a mensagem
            self.escrever_log("🔍 Procurando onde digitar...", "info", nao_repetir=True)
            
            wait_curto = WebDriverWait(navegador, 20)
            campo_texto = None
            
            try:
                # Esse data-tab='10' é o campo de texto do WhatsApp (por enquanto...)
                campo_texto = wait_curto.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
                )
                self.escrever_log("✅ Achei onde digitar!", "success")
            except TimeoutException as erro:
                self.escrever_log(f"❌ Não achei onde digitar depois de 20s: {str(erro)}", "error")
                return False
            
            # Verifica se o usuário quer mandar tudo de uma vez ou quebrar em partes
            self.escrever_log("📝 Preparando texto...", "info", nao_repetir=True)
            
            if self.enviar_tudo_junto.get():
                # Manda tudo de uma vez só (mais rápido)
                self.escrever_log("💬 Mandando mensagem completa", "info")
                
                campo_texto.clear()
                campo_texto.click()
                
                # Usa SHIFT+ENTER pra quebrar linha sem mandar
                linhas = texto_mensagem.split('\n')
                for i, linha in enumerate(linhas):
                    campo_texto.send_keys(linha)
                    if i < len(linhas) - 1:
                        campo_texto.send_keys(Keys.SHIFT, Keys.ENTER)
                
                time.sleep(2)  
                self.escrever_log("📨 Enviando...", "info")
                campo_texto.send_keys(Keys.ENTER)
                self.escrever_log("✅ Mensagem enviada!", "success")
            
            else:
                # Quebra por parágrafos e manda separado
                self.escrever_log("📃 Modo de envio em partes", "info")
                
                if '\n\n' in texto_mensagem:
                    partes = [p.strip() for p in texto_mensagem.split('\n\n') if p.strip()]
                    self.escrever_log(f"📊 {len(partes)} partes detectadas", "info")
                    
                    for num_parte, parte in enumerate(partes, 1):
                        preview = parte[:40] + ('...' if len(parte) > 40 else '')
                        self.escrever_log(f"📨 Enviando {num_parte}/{len(partes)}: {preview}", "info")
                        
                        campo_texto.clear()
                        campo_texto.click()
                        campo_texto.send_keys(parte.strip())
                        
                        time.sleep(1)
                        campo_texto.send_keys(Keys.ENTER)
                        
                        if num_parte < len(partes):
                            time.sleep(2)
                    
                    self.escrever_log(f"✅ {len(partes)} partes enviadas!", "success")
                else:
                    # Não tem parágrafo duplo, manda tudo junto mesmo
                    self.escrever_log("📝 Sem parágrafos encontrados - mandando tudo junto", "info")
                    
                    campo_texto.clear()
                    campo_texto.click()
                    
                    linhas = texto_mensagem.split('\n')
                    for i, linha in enumerate(linhas):
                        campo_texto.send_keys(linha)
                        if i < len(linhas) - 1:
                            campo_texto.send_keys(Keys.SHIFT, Keys.ENTER)
                    
                    time.sleep(2)
                    self.escrever_log("📨 Enviando...", "info")
                    campo_texto.send_keys(Keys.ENTER)
                    self.escrever_log("✅ Mensagem enviada!", "success")
            
            # Espera um pouco pra não parecer bot
            time.sleep(3)
            return True
            
        except NoSuchElementException as erro:
            self.escrever_log(f"❌ Elemento não encontrado: {str(erro)}", "error")
            return False
        except StaleElementReferenceException as erro:
            self.escrever_log(f"❌ Elemento sumiu do nada: {str(erro)}", "error")
            return False
        except Exception as erro:
            self.escrever_log(f"❌ Erro crítico: {str(erro)}", "error")
            return False

    def iniciar_automacao(self):
        """Inicia automação completa com validações melhoradas"""
        # Verifica se tem arquivo
        if not self.lista_telefones:
            messagebox.showerror("Erro", "Selecione um arquivo com a lista de contatos!")
            return
            
        # Verifica mensagem
        mensagem = self.corpo_campanha.get("1.0", tk.END).strip()
        if not mensagem:
            messagebox.showerror("Erro", "Digite uma mensagem para enviar!")
            return
            
        # Validar pausa
        try:
            if self.usar_tempo_aleatorio.get():
                pausa_min = int(self.tempo_minimo.get())
                pausa_max = int(self.tempo_maximo.get())
                if pausa_min >= pausa_max:
                    messagebox.showerror("Erro", "Pausa mínima deve ser menor que a máxima!")
                    return
            else:
                pausa = int(self.tempo_fixo.get())
        except:
            messagebox.showerror("Erro", "Valores de pausa devem ser números!")
            return
            
        # Confirmação
        modo_pausa = f"Aleatória ({self.tempo_minimo.get()}s a {self.tempo_maximo.get()}s)" if self.usar_tempo_aleatorio.get() else f"Fixa ({self.tempo_fixo.get()}s)"
        resposta = messagebox.askyesno(
            "Confirmar Automação",
            f"Iniciar envio para {len(self.lista_telefones)} contatos?\n\n"
            f"Mensagem: {mensagem[:40]}{'...' if len(mensagem) > 40 else ''}\n"
            f"Pausa: {modo_pausa}\n\n"
            f"⚠️ ATENÇÃO: Este processo pode levar muito tempo!\n\n"
            f"🔑 Será necessário escanear o QR Code do WhatsApp Web"
        )
        
        if not resposta:
            return
            
        # Configurar interface
        self.ta_rodando = True
        self.btn_iniciar.config(state='disabled')
        self.btn_teste.config(state='disabled') 
        self.btn_parar.config(state='normal')
        
        # Iniciar thread
        threading.Thread(target=self.executar_automacao, args=(mensagem,), daemon=True).start()
        
    def teste_um_contato(self):
        """Teste com um contato baseado no código original"""
        if not self.lista_telefones:
            messagebox.showerror("Erro", "Selecione um arquivo com a lista de contatos!")
            return
            
        mensagem = self.corpo_campanha.get("1.0", tk.END).strip()
        if not mensagem:
            messagebox.showerror("Erro", "Digite uma mensagem para enviar!")
            return
            
        primeiro_numero = self.lista_telefones[0]
        resposta = messagebox.askyesno(
            "Confirmar Teste",
            f"Enviar mensagem de TESTE para:\n{primeiro_numero}\n\n"
            f"Mensagem: {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n"
            f"Este é apenas um teste com 1 contato."
        )
        
        if not resposta:
            return
            
        # Configurar interface
        self.ta_rodando = True
        self.btn_iniciar.config(state='disabled')
        self.btn_teste.config(state='disabled')
        self.btn_parar.config(state='normal')
        
        # Iniciar thread
        threading.Thread(target=self.executar_teste, args=(mensagem, primeiro_numero), daemon=True).start()
        
    def executar_teste(self, mensagem, numero):
        """Executa teste com um contato e salva histórico"""
        try:
            # Configurar driver
            self.texto_status.set("Configurando navegador para teste...")
            self.navegador = self.configurar_chrome()
            
            if not self.navegador:
                self.escrever_log("Erro ao configurar navegador", "error")
                return
                
            # Navegar para WhatsApp
            self.texto_status.set("Navegando para WhatsApp Web...")
            self.navegador.get("https://web.whatsapp.com")
            
            # Aguardar login
            self.texto_status.set("Aguardando login no WhatsApp...")
            if not self.fazer_login_whatsapp(self.navegador):
                self.escrever_log("Falha no login do WhatsApp", "error")
                return
                
            # Enviar mensagem de teste
            self.texto_status.set(f"TESTE: Enviando para {numero}...")
            self.progress['maximum'] = 1
            self.progress['value'] = 0
            
            if self.mandar_mensagem(self.navegador, numero, mensagem):
                self.escrever_log("✅ TESTE CONCLUÍDO COM SUCESSO!", "success")
                self.escrever_log(f"📊 Teste salvo em: historico_envios.csv", "info")
                salvar_no_historico(numero, "✅ Teste Sucesso", mensagem, "Teste executado com sucesso")
                self.texto_status.set("Teste concluído com sucesso!")
                messagebox.showinfo("Teste Concluído", f"✅ Mensagem enviada com sucesso para:\n{numero}\n\n📊 Histórico salvo!")
            else:
                self.escrever_log("❌ TESTE FALHOU", "error")
                salvar_no_historico(numero, "❌ Teste Falha", mensagem, "Erro ao enviar teste")
                self.texto_status.set("Teste falhou!")
                messagebox.showerror("Teste Falhou", f"❌ Não foi possível enviar para:\n{numero}")
                
            self.progress['value'] = 1
            
        except Exception as e:
            self.escrever_log(f"Erro no teste: {str(e)}", "error")
            messagebox.showerror("Erro", f"Erro durante o teste: {str(e)}")
        finally:
            self.finalizar_automacao()
            
    def executar_automacao(self, mensagem):
        """Executa automação completa baseada no código original"""
        try:
            # Limpar cache de logs únicos para nova automação
            self.limpar_cache_logs()
            
            # Configurar driver
            self.texto_status.set("Configurando navegador...")
            self.navegador = self.configurar_chrome()
            
            if not self.navegador:
                self.escrever_log("Erro ao configurar navegador", "error")
                return
                
            # Navegar para WhatsApp
            self.texto_status.set("Navegando para WhatsApp Web...")
            self.navegador.get("https://web.whatsapp.com")
            
            # Aguardar login
            self.texto_status.set("Aguardando login no WhatsApp...")
            if not self.fazer_login_whatsapp(self.navegador):
                self.escrever_log("Falha no login do WhatsApp", "error")
                return
                
            # Processar contatos
            total = len(self.lista_telefones)
            sucessos = 0
            falhas = 0
            
            self.progress['maximum'] = total
            
            for i, numero in enumerate(self.lista_telefones):
                if not self.ta_rodando:
                    self.escrever_log("Automação interrompida pelo usuário", "warning")
                    break
                    
                self.texto_status.set(f"Enviando para {numero} ({i+1}/{total})...")
                self.progress['value'] = i + 1
                
                if self.mandar_mensagem(self.navegador, numero, mensagem):
                    sucessos += 1
                    salvar_no_historico(numero, "✅ Sucesso", mensagem, "Mensagem enviada com sucesso")
                    self.escrever_log(f"✅ Sucesso: {numero}", "success")
                else:
                    falhas += 1
                    salvar_no_historico(numero, "❌ Falha", mensagem, "Erro ao enviar mensagem")
                    self.escrever_log(f"❌ Falha: {numero}", "error")
                    
                # Pausa entre envios (exceto no último)
                if i < total - 1 and self.ta_rodando:
                    if self.usar_tempo_aleatorio.get():
                        pausa = random.randint(int(self.tempo_minimo.get()), int(self.tempo_maximo.get()))
                        self.escrever_log(f"⏰ Pausa aleatória: {pausa}s", "info")
                    else:
                        pausa = int(self.tempo_fixo.get())
                        self.escrever_log(f"⏰ Pausa: {pausa}s", "info")
                    
                    self.texto_status.set(f"Pausa: {pausa}s...")
                    for segundo in range(pausa):
                        if not self.ta_rodando:
                            break
                        time.sleep(1)
                        self.janela.update_idletasks()
                        
            # Relatório final
            taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
            self.escrever_log("=" * 50, "info")
            self.escrever_log("🎉 AUTOMAÇÃO CONCLUÍDA!", "success")
            self.escrever_log(f"✅ Sucessos: {sucessos}/{total} ({taxa_sucesso:.1f}%)", "success")
            self.escrever_log(f"❌ Falhas: {falhas}/{total}", "error" if falhas > 0 else "info")
            self.escrever_log(f"📊 Histórico salvo em: historico_envios.csv", "info")
            self.escrever_log("=" * 50, "info")
            
            self.texto_status.set(f"Concluído: {sucessos} sucessos, {falhas} falhas")
            
            messagebox.showinfo(
                "Automação Concluída",
                f"✅ Envios finalizados!\n\n"
                f"✅ Sucessos: {sucessos}/{total} ({taxa_sucesso:.1f}%)\n"
                f"❌ Falhas: {falhas}\n\n"
                f"📊 Histórico salvo em: historico_envios.csv"
            )
            
        except Exception as e:
            self.escrever_log(f"Erro na automação: {str(e)}", "error")
            messagebox.showerror("Erro", f"Erro durante a automação: {str(e)}")
        finally:
            self.finalizar_automacao()
            
    def parar_automacao(self):
        """Para automação em execução"""
        self.ta_rodando = False
        self.escrever_log("Parando automação...", "warning")
        self.texto_status.set("Parando...")
        
    def finalizar_automacao(self):
        """Finaliza automação e limpa recursos"""
        self.ta_rodando = False
        
        # Fechar driver
        if self.navegador:
            try:
                self.navegador.quit()
                self.escrever_log("Navegador fechado", "info")
            except:
                pass
            self.navegador = None
            
        # Restaurar interface
        self.btn_iniciar.config(state='normal')
        self.btn_teste.config(state='normal') 
        self.btn_parar.config(state='disabled')
        self.progress['value'] = 0
        
        # Atualizar status se necessário
        if self.texto_status.get() in ("Parando...", "Configurando navegador para teste...", "Configurando navegador..."):
            self.texto_status.set("Pronto para iniciar")
            
    def executar(self):
        """Executa aplicação"""
        self.janela.protocol("WM_DELETE_WINDOW", self.ao_fechar)
        self.janela.mainloop()
        
    def ao_fechar(self):
        """Manipula fechamento da aplicação"""
        if self.ta_rodando:
            resposta = messagebox.askyesno(
                "Confirmação",
                "A automação está em execução. Deseja realmente sair?"
            )
            if not resposta:
                return
                
            self.parar_automacao()
            
        # Fechar driver
        if self.navegador:
            try:
                self.navegador.quit()
            except:
                pass
                
        self.janela.destroy()


def main():
    """Função principal"""
    try:
        app = AutomatizadorWhatsApp()
        app.executar()
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar aplicação: {str(e)}")


if __name__ == "__main__":
    main()
















