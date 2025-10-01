# 🚀 WhatsApp Automatizador

<div align="center">

![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Status](https://img.shields.io/badge/Status-Ativo-brightgreen?style=for-the-badge)

**Automatizador profissional para envio de mensagens em massa no WhatsApp Web**

[Características](#-características) •
[Instalação](#-instalação) •
[Uso](#-como-usar) •
[Configuração](#-configuração) •
[Suporte](#-suporte)

</div>

---

## 📋 Índice

- [🎯 Características](#-características)
- [🛠️ Instalação](#️-instalação)
- [🚀 Como Usar](#-como-usar)
- [⚙️ Configuração](#️-configuração)
- [📊 Formatos Suportados](#-formatos-suportados)
- [🔧 Funcionalidades Avançadas](#-funcionalidades-avançadas)
- [🎨 Interface](#-interface)
- [⚠️ Importante](#️-importante)
- [🆘 Suporte](#-suporte)
- [📝 Changelog](#-changelog)

---

## 🎯 Características

### ✨ **Principais Funcionalidades**
- 📱 **Envio automático** de mensagens para múltiplos contatos
- 🤖 **Divisão inteligente** de mensagens por parágrafos
- 🥷 **Modo segundo plano** - automação invisível após login
- 📊 **Importação Excel** (.xlsx) com lista de contatos
- ⏱️ **Controle de pausas** personalizável entre envios
- 🔍 **Logs detalhados** com sistema anti-repetição
- 🎨 **Interface gráfica** intuitiva e moderna

### 🔥 **Diferenciais Únicos**
- **Detecção automática de parágrafos** - envia mensagens organizadas
- **Chrome invisível** - funciona em segundo plano após login
- **Logs inteligentes** - evita spam de mensagens repetitivas
- **Login QR Code** - autenticação segura do WhatsApp
- **Seletor otimizado** - usa elementos que realmente funcionam

---

## 🛠️ Instalação

### 📋 **Pré-requisitos**
- Python 3.7 ou superior
- Google Chrome instalado
- Conexão com internet
- WhatsApp configurado no celular

### 💾 **Dependências**
```bash
pip install selenium
pip install pandas
pip install openpyxl
pip install webdriver-manager
pip install tkinter  # (normalmente já incluído no Python)
```

### 📦 **Instalação Rápida**
```bash
# Clone ou baixe os arquivos
cd Pendrive_Automatizador_WhatsApp

# Instale as dependências
pip install -r requirements.txt

# Execute o programa
python WhatsApp_Automatizador_CODIGO_COMPLETO.py
```

---

## 🚀 Como Usar

### 1️⃣ **Preparar Lista de Contatos**
Crie um arquivo Excel (.xlsx) com uma coluna chamada **"Numero"**:

```
| Numero        |
|---------------|
| 5561984385187 |
| 5561999171175 |
| 5561993707017 |
```

### 2️⃣ **Executar o Programa**
```bash
python WhatsApp_Automatizador_CODIGO_COMPLETO.py
```

### 3️⃣ **Configurar Automação**
1. 📁 **Selecionar arquivo** Excel com contatos
2. 📝 **Digitar mensagem** na caixa de texto
3. ⏱️ **Definir pausa** entre envios (recomendado: 20 segundos)
4. 🎛️ **Escolher modo**: Visual ou Segundo Plano

### 4️⃣ **Fazer Login**
1. 🔍 **Escanear QR Code** que aparecerá no Chrome
2. ✅ **Aguardar confirmação** do login
3. 🚀 **Automação iniciará** automaticamente

### 5️⃣ **Acompanhar Progresso**
- 📊 Logs em tempo real
- 📈 Contadores de sucesso/falha
- ⏹️ Botão de parada a qualquer momento

---

## ⚙️ Configuração

### 🎛️ **Modos de Operação**

#### 💻 **Modo Visual**
- Chrome visível durante toda automação
- Ideal para acompanhar o processo
- Recomendado para primeiros usos

#### 🥷 **Modo Segundo Plano**
- Chrome visível apenas para login QR Code
- Após login, fica completamente invisível
- Ideal para automações longas e discretas

### ⏰ **Pausas Recomendadas**
- **Poucos contatos (< 10)**: 15-20 segundos
- **Médio volume (10-50)**: 25-30 segundos  
- **Alto volume (> 50)**: 35-45 segundos

---

## 📊 Formatos Suportados

### 📱 **Números de Telefone**
```
✅ Aceitos:
- 5561984385187 (com código do país)
- 61984385187 (com DDD)
- +5561984385187 (formato internacional)

❌ Não aceitos:
- (61) 98438-5187 (com caracteres especiais)
- 984385187 (sem código de área)
```

### 📝 **Mensagens Inteligentes**

#### **Mensagem Simples** (enviada como 1 mensagem):
```
Olá! Como você está? Gostaria de saber sobre nossos produtos.
```

#### **Mensagem com Parágrafos** (enviada como múltiplas mensagens):
```
Olá! Como você está?

Gostaria de saber sobre nossos produtos.

*Oferecemos:*
- Qualidade garantida
- Preços competitivos
- Entrega rápida

Podemos conversar hoje?
```

---

## 🔧 Funcionalidades Avançadas

### 🤖 **Divisão Inteligente de Mensagens**
- **Detecção automática** de parágrafos (`\n\n`)
- **Envio sequencial** com pausas entre partes
- **Formatação preservada** (negrito, itálico, etc.)
- **Evita detecção de spam** com timing natural

### 📋 **Sistema de Logs**
- **Logs únicos** - evita repetições desnecessárias
- **Códigos de cor** para diferentes tipos de mensagem
- **Timestamp preciso** em cada ação
- **Cache inteligente** resetado a cada automação

### 🔒 **Segurança e Estabilidade**
- **Detecção de elementos** otimizada para WhatsApp Web
- **Tratamento de erros** robusto
- **Perfis temporários** do Chrome
- **Limpeza automática** de recursos

---

## 🎨 Interface

### 🖥️ **Tela Principal**
```
┌─────────────────────────────────────────┐
│  📁 Selecionar Arquivo  [Arquivo.xlsx]  │
├─────────────────────────────────────────┤
│  📝 Mensagem:                           │
│  ┌─────────────────────────────────────┐ │
│  │ Digite sua mensagem aqui...         │ │
│  │                                     │ │
│  └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  ⏱️ Pausa: [20] segundos                │
│  🎛️ □ Modo Segundo Plano                │
├─────────────────────────────────────────┤
│  🚀 Iniciar  🧪 Teste  ⏹️ Parar        │
├─────────────────────────────────────────┤
│  📊 Logs:                               │
│  ┌─────────────────────────────────────┐ │
│  │ [16:00:51] Arquivo carregado...     │ │
│  │ [16:00:59] Configurando Chrome...   │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 📊 **Contadores em Tempo Real**
- ✅ **Sucessos**: Mensagens enviadas com sucesso
- ❌ **Falhas**: Erros durante envio
- 📊 **Total**: Contatos processados
- ⏱️ **Tempo**: Duração da automação

---

## ⚠️ Importante

### 🚨 **Avisos Legais**
- ✅ Use apenas com **seus próprios contatos**
- ✅ Respeite as **políticas do WhatsApp**
- ✅ Evite **spam** ou mensagens não solicitadas
- ✅ **Teste sempre** com poucos contatos primeiro

### 🛡️ **Boas Práticas**
- 📱 **Mantenha WhatsApp** atualizado no celular
- 🔒 **Não compartilhe** suas credenciais
- ⏰ **Use pausas adequadas** para evitar bloqueios
- 🧪 **Teste mensagens** antes de envios em massa

### 🔧 **Resolução de Problemas**
- **QR Code não aparece**: Aguarde alguns segundos
- **Chrome não abre**: Verifique se está instalado
- **Erro de elementos**: WhatsApp pode ter mudado, aguarde atualização
- **Mensagens não enviam**: Verifique formato dos números

---

## 🆘 Suporte

### 📞 **Contato**
- 💬 **WhatsApp**: +55 (61) 98438-5187
- 📧 **Email**: victorvasconcellos28@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/usuario/repo/issues)


### 🤝 **Contribuições**
Contribuições são bem-vindas! Por favor:
1. 🍴 Fork o projeto
2. 🌿 Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push para a branch (`git push origin feature/AmazingFeature`)
5. 🔄 Abra um Pull Request

---

## 📝 Changelog

### 🔄 **Versão Atual - v2.0.0**
- ✨ **Novo**: Divisão inteligente de mensagens por parágrafos
- ✨ **Novo**: Modo segundo plano com Chrome invisível após login
- ✨ **Novo**: Sistema de logs únicos (anti-repetição)
- 🔧 **Melhorado**: Seletor otimizado para caixa de texto
- 🔧 **Melhorado**: Interface mais limpa e profissional
- 🐛 **Corrigido**: Problemas com caracteres especiais
- 🐛 **Corrigido**: Detecção de login mais estável

### 📜 **Versões Anteriores**
- **v1.5.0**: Implementação do modo headless
- **v1.4.0**: Adição de controle de pausas
- **v1.3.0**: Interface gráfica aprimorada
- **v1.2.0**: Suporte a arquivos Excel
- **v1.1.0**: Sistema de logs coloridos
- **v1.0.0**: Versão inicial básica

---

<div align="center">

### 🌟 **Se este projeto te ajudou, deixe uma ⭐!**

**Desenvolvido com ❤️ por [Victor Vasconcelos](https://github.com/VicorVasconcelos)**

---

*️⃣ **Automatização inteligente • Interface moderna • Resultados profissionais***

![Footer](https://img.shields.io/badge/Made%20with-Python%20%F0%9F%90%8D-blue?style=for-the-badge)
![Love](https://img.shields.io/badge/Built%20with-%E2%9D%A4%EF%B8%8F-red?style=for-the-badge)

</div>