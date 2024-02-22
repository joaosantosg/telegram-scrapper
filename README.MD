## Projeto de scraping telegram

### Objetivo
O objetivo deste projeto é criar um bot que coleta informações de um site e envia para um grupo no telegram, utilizando a biblioteca telethon.

Para gerar as chaves de acesso, é necessário criar um aplicativo no site do telegram e obter as chaves de acesso.


### Tecnologias
- Python

### Bibliotecas
- telethon
- python-dotenv

### Como rodar
1. Clone o repositório
```bash
git clone
```
2. Crie um virtualenv
```bash
python3 -m venv venv
```

3. Ative o virtualenv
```bash
source venv/bin/activate
```

4. Instale as dependências
```bash
pip install -r requirements.txt
```

5. Crie um arquivo .env e adicione as variáveis de ambiente
```bash
TelegramUsername=    
TelegramPhone=
TelegramApiId=
TelegramApiHash=
```

6. Rode o projeto
```bash
python main.py
```

### Como rodar os testes
1. Clone o repositório
```bash
git clone
```
2. Crie um virtualenv
```bash
python3 -m venv venv
```

3. Ative o virtualenv
```bash
source venv/bin/activate
```

4. Instale as dependências
```bash
pip install -r requirements.txt
```

5. Rode os testes
```bash
pytest
```



