# 🏨 Sistema de Reservas de Hotel

Um sistema web moderno e responsivo para gerenciamento de reservas de hotel, desenvolvido com Flask e SQLAlchemy.

## ✨ Funcionalidades

### 👥 Área do Cliente
- Visualização de quartos disponíveis com fotos e descrições
- Sistema de reservas online
- Gerenciamento de reservas pessoais
- Histórico de estadias
- Perfil do usuário personalizável

### 👨‍💼 Área do Administrador
- Gerenciamento completo de quartos
  - Adicionar/Editar/Remover quartos
  - Upload de múltiplas fotos
  - Definição de preços e tipos
- Controle de reservas
  - Visualização de todas as reservas
  - Confirmação/Cancelamento de reservas
  - Histórico detalhado
- Dashboard administrativo
  - Estatísticas de ocupação
  - Relatórios de reservas
  - Gestão de usuários

## 🛠 Tecnologias Utilizadas

- **Backend**
  - Python 3.8+
  - Flask (Framework Web)
  - SQLAlchemy (ORM)
  - Flask-Login (Autenticação)
  - Werkzeug (Utilitários)

- **Frontend**
  - HTML5
  - CSS3 (Design Responsivo)
  - JavaScript
  - Bootstrap 5
  - Font Awesome (Ícones)

- **Banco de Dados**
  - SQLite (Desenvolvimento)
  - PostgreSQL (Produção)

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (Gerenciador de pacotes Python)
- Virtualenv (recomendado)

## 🚀 Instalação

1. Clone o repositório
```bash
git clone https://github.com/biaphra/Python_HotelSystem.git
cd sistema-reservas-hotel
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Inicialize o banco de dados
```bash
python reset_db.py
```

6. Execute o servidor de desenvolvimento
```bash
python app.py
```

## 📝 Configuração

O sistema pode ser configurado através das seguintes variáveis de ambiente:

- `FLASK_ENV`: Ambiente de execução (development/production)
- `SECRET_KEY`: Chave secreta para sessões
- `DATABASE_URL`: URL de conexão com o banco de dados
- `UPLOAD_FOLDER`: Diretório para upload de imagens

## 🔒 Segurança

- Senhas criptografadas com Werkzeug
- Proteção contra CSRF
- Validação de entrada de dados
- Controle de acesso baseado em funções
- Sanitização de uploads de arquivos

## 📱 Responsividade

O sistema é totalmente responsivo, adaptando-se a diferentes tamanhos de tela:
- Desktop
- Tablet
- Smartphone

## 🎨 Personalização

O sistema utiliza variáveis CSS para fácil personalização:
- Cores principais
- Tipografia
- Espaçamentos
- Elementos visuais

## 📊 Estrutura do Projeto

```
sistema-reservas-hotel/
├── app.py              # Aplicação principal
├── config.py           # Configurações
├── models/             # Modelos do banco de dados
├── static/             # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/          # Templates HTML
│   ├── admin/
│   └── client/
└── utils/             # Utilitários
```

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- **Biaphra Araujo** - *Trabalho inicial* - [@biaphra](https://github.com/biaphra/Python_HotelSystem)

## 🙏 Agradecimentos

- Bootstrap Team
- Flask Team
- Todos os contribuidores que participaram deste projeto

---
⌨️ By: [@biaphra](https://github.com/biaphra/Python_HotelSystem)
