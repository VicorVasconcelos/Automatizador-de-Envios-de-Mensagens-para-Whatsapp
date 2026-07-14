# 🚀 WhatsApp Automatizador

<div align="center">

![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Status](https://img.shields.io/badge/Status-Ativo-brightgreen?style=for-the-badge)

**Sistema pra mandar mensagem em massa no WhatsApp Web**

**Criado porque mandar mensagem uma por uma é muito trabalho!**

[O que faz](#-o-que-faz) •
[Como instalar](#-como-instalar) •
[Como usar](#-como-usar) •
[Configurações](#-configurações) •
[Novidades](#-novidades-fevereiro2026) •
[Contato](#-contato)

</div>

---

## 📋 O que tem aqui

- [O que faz](#-o-que-faz)
- [Como instalar](#-como-instalar)
- [Como usar](#-como-usar)
- [Configurações](#-configurações)
- [Jeito certo de colocar os números](#-jeito-certo-de-colocar-os-números)
- [Recursos](#-recursos)
- [Novidades](#-novidades-fevereiro2026)
- [Cuidados importantes](#-cuidados-importantes)
- [Contato](#-contato)

---

## 🎯 O que faz

- Manda mensagem pra vários contatos de uma vez (automático)
- Você escolhe: manda tudo junto ou divide por parágrafo
- Carrega lista de contatos do Excel (.xlsx)
- Espera um tempo entre cada envio (pra não tomar ban)
- Mostra na tela o que tá fazendo
- Interface simples de usar
- Pode deixar o Chrome invisível depois de fazer login

---

## 🛠️ Como instalar

### O que você precisa ter instalado antes
- Python 3.7 ou mais novo (se não tem, baixa no python.org)
- Google Chrome (o navegador mesmo)
- Internet funcionando

### Instalar as bibliotecas
Abre o terminal (CMD ou PowerShell) na pasta do projeto e roda:
```bash
pip install -r requirements.txt
```

Se der problema, instala uma por uma:
```bash
pip install selenium pandas openpyxl webdriver-manager
```

### Pra rodar o programa
```bash
python WhatsApp_Automatizador_CODIGO_COMPLETO.py
```

---

## 🚀 Como usar

### 1. Fazer a planilha de contatos
Cria um arquivo Excel (.xlsx) com uma coluna chamada **"Numero"** (tem que ser esse nome):

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

### 3. Configurar tudo
1. Clica no botão pra escolher o arquivo Excel
2. Escreve a mensagem que quer mandar
3. Escolhe quanto tempo vai esperar entre cada envio
4. Decide se quer ver o Chrome ou deixar ele invisível

### 4. Fazer login no WhatsApp
1. Vai abrir o Chrome com um QR Code
2. Abre o WhatsApp no celular e escaneia o QR Code
3. Pronto! Agora é só clicar em "Iniciar" e deixar rodar

### 5. Acompanhar os envios
Na tela você vê tudo que tá acontecendo: quantos foram enviados, se deu erro, etc.

---

## ⚙️ Configurações

### Modos do Chrome
- **Visual**: Chrome fica aberto e você vê tudo acontecendo
- **Segundo Plano**: Chrome fica invisível depois de fazer login (mais rápido)

### Quanto tempo esperar entre cada envio
**IMPORTANTE:** Se mandar muito rápido, o WhatsApp bloqueia!

- Poucos contatos (até 50): 15-20 segundos
- Quantidade média (50-200): 25-30 segundos
- Muitos contatos (200+): 35-45 segundos

💡 **Dica:** Sempre comece com tempo maior. Melhor demorar mais do que tomar ban!

---

## 📱 Jeito certo de colocar os números

### ✅ Formatos que funcionam:
- `5561984385187` (com código do país 55)
- `61984385187` (só com DDD)
- `+5561984385187` (com o +)

### ❌ Formatos que NÃO funcionam:
- `(61) 98438-5187` (com parênteses e traço)
- `984385187` (sem DDD)
- `61 98438-5187` (com espaços)

💡 **Dica:** O programa arruma automaticamente se tá faltando o 55, mas é melhor já colocar certinho!

---

## 🔧 Recursos

### Como a mensagem é enviada
- **Mensagem única**: Manda tudo de uma vez só (recomendado)
- **Dividido por parágrafo**: Manda cada parágrafo separado (útil pra mensagens longas)

**Exemplo:**
```
Olá!

Tudo bem?

Como posso ajudar?
```

Se escolher "dividido": vai mandar 3 mensagens separadas.

### Limpeza automática da lista
- Tira os números repetidos sozinho
- Verifica se os números tão no formato certo
- Mostra quantos tinha problema

### Baixar modelo de planilha
Tem um botão que cria o arquivo `MODELO_CONTATOS.xlsx` já pronto pra você só preencher

---

## 🆕 Novidades (Fevereiro/2026)

### 📁 Agora salva o modelo direitinho
- O arquivo modelo vai direto pra pasta **Documentos**
- Abre a pasta automaticamente pra você ver onde ficou
- Não precisa mais ficar procurando!

### 📨 Consertamos o envio de mensagem única
- **O problema:** Antes, mesmo marcando "mensagem única", se tivesse Enter no texto, mandava várias mensagens
- **Como resolvemos:** Agora usa SHIFT+ENTER internamente pra manter tudo numa mensagem só
- **Resultado:** A mensagem vai completa, com todas as quebras de linha, tudo junto

---

## ⚠️ Cuidados importantes

**LEIA ISSO ANTES DE USAR:**

- ⚠️ Só manda mensagem pra quem você conhece e autorizou
- ⚠️ Não faz spam! WhatsApp bloqueia e é chato
- ⚠️ Usa um tempo de espera bom entre os envios (pelo menos 20 segundos)
- ⚠️ **SEMPRE** testa primeiro com 2-3 contatos antes de mandar pra lista toda
- ⚠️ Mantém o WhatsApp do celular atualizado
- ⚠️ Não fecha o Chrome enquanto tiver enviando

**Se tomar ban, a culpa não é nossa! Use com responsabilidade.**

---

## 🆘 Contato

**Tá com dúvida ou deu problema?**

- 💬 **WhatsApp**: +55 (61) 98438-5187
- 📧 **Email**: victorvasconcellos28@gmail.com
- 🐛 **Bug/Sugestão**: Abre uma issue aqui no GitHub

---

<div align="center">

### 👍 Se o programa te ajudou, deixa uma estrela ⭐!

**Feito com ☕ e muito ctrl+c ctrl+v por [Victor Vasconcelos](https://github.com/VicorVasconcelos)**

*"Preguiça é a mãe da automação" - Algum programador aí*

</div>