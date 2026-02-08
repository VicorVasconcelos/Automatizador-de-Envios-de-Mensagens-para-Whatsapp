# 🚀 WhatsApp Automatizador

<div align="center">

![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Status](https://img.shields.io/badge/Status-Ativo-brightgreen?style=for-the-badge)

**Ferramenta pra automatizar envio de mensagens em massa no WhatsApp**

[Características](#-características) •
[Instalação](#-instalação) •
[Como Usar](#-como-usar) •
[Configuração](#-configuração) •
[Melhorias Recentes](#-melhorias-recentes-fevereiro2026) •
[Suporte](#-suporte)

</div>

---

## 📋 Índice

- [Características](#-características)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Configuração](#-configuração)
- [Formatos de Números](#-formatos-de-números)
- [Funcionalidades](#-funcionalidades)
- [Melhorias Recentes](#-melhorias-recentes-fevereiro2026)
- [Importante](#-importante)
- [Suporte](#-suporte)

---

## 🎯 Características

- Envio automático pra múltiplos contatos
- Envia mensagem inteira ou dividida por parágrafos (você escolhe)
- Importação de Excel (.xlsx) com lista de contatos
- Pausa entre envios (configurável)
- Logs em tempo real
- Interface fácil de usar
- Modo segundo plano (Chrome invisível após login)

---

## 🛠️ Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Google Chrome instalado
- Conexão com internet

### Dependências
```bash
pip install -r requirements.txt
```

Ou instale manualmente:
```bash
pip install selenium pandas openpyxl webdriver-manager
```

### Executar
```bash
python WhatsApp_Automatizador_CODIGO_COMPLETO.py
```

---

## 🚀 Como Usar

### 1. Preparar o arquivo de contatos
Crie um Excel (.xlsx) com uma coluna chamada **"Numero"**:

```
| Numero        |
|---------------|
| 5561984385187 |
| 5561999171175 |
| 5561993707017 |
```

### 2. Abrir o programa
```bash
python WhatsApp_Automatizador_CODIGO_COMPLETO.py
```

### 3. Configurar
1. Seleciona o arquivo Excel
2. Digita a mensagem
3. Define a pausa entre envios
4. Escolhe o modo (visual ou segundo plano)

### 4. Fazer login
1. QR Code aparece na tela do Chrome
2. Escaneia no celular
3. Pronto! A automação começa sozinha

### 5. Acompanhar
Os logs mostram tudo que tá acontecendo em tempo real.

---

## ⚙️ Configuração

### Modos
- **Visual**: Chrome fica aberto pra você ver tudo
- **Segundo Plano**: Chrome fica invisível depois do login

### Pausa entre envios
- Poucos contatos: 15-20 segundos
- Médio volume: 25-30 segundos
- Muitos contatos: 35-45 segundos

---

## 📱 Formatos de Números

Aceita:
- `5561984385187` (com código do país)
- `61984385187` (só com DDD)
- `+5561984385187` (formato internacional)

Não aceita:
- `(61) 98438-5187` (com caracteres especiais)
- `984385187` (sem código de área)

---

## 🔧 Funcionalidades

### Envio Inteligente
- **Mensagem única**: envia tudo de uma vez
- **Dividido por parágrafos**: envia cada parágrafo como uma mensagem separada

Exemplo:
```
Olá!

Tudo bem?

Como posso ajudar?
```

Se dividir: envia 3 mensagens separadas com pausa entre cada uma.

### Validação de Contatos
- Remove duplicatas automaticamente
- Valida números antes de enviar
- Mostra quantos foram removidos

### Exportar Modelo
Cria um arquivo `MODELO_CONTATOS.xlsx` pra você preencher e enviar

---

## 🆕 Melhorias Recentes (Fevereiro/2026)

### 📁 Salvamento Inteligente do Modelo
- Agora o modelo de contatos é salvo direto na pasta **Documentos** do usuário
- O explorador de arquivos abre automaticamente mostrando onde o arquivo foi salvo
- Você não precisa mais procurar onde ficou o arquivo!

### 📨 Correção no Envio de Mensagem Única
- **Problema resolvido**: Quando marcava "enviar em mensagem única", o WhatsApp enviava múltiplas mensagens se tivesse quebras de linha
- **Solução**: Agora usa SHIFT+ENTER pra manter todas as quebras de linha dentro de uma única mensagem
- Resultado: Mensagem é enviada completa, preservando toda a formatação, sem dividir

---

## ⚠️ Importante

- Use só com seus próprios contatos
- Não faça spam
- Use pausas adequadas pra não tomar ban do WhatsApp
- Teste sempre com poucos contatos primeiro
- Mantém WhatsApp atualizado no celular

---

## 🆘 Suporte

### Contato
- **WhatsApp**: +55 (61) 98438-5187
- **Email**: victorvasconcellos28@gmail.com

---

<div align="center">

### Se ajudou, deixa uma ⭐!

**Feito com ❤️ por [Victor Vasconcelos](https://github.com/VicorVasconcelos)**

</div>