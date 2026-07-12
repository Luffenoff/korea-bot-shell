# Korea Car Bot

Telegram бот для поиска и заказа автомобилей из Кореи.

## Установка на хостинг

### Railway (Рекомендуется)

1. Зарегистрируйтесь на [Railway](https://railway.app/)
2. Подключите ваш GitHub репозиторий
3. Railway автоматически определит Python проект и запустит его

### Heroku

1. Установите Heroku CLI
2. Выполните команды:
```bash
heroku create your-bot-name
git add .
git commit -m "Initial commit"
git push heroku main
```

### VPS (Ubuntu/Debian)

1. Подключитесь к серверу
2. Установите Python и зависимости:
```bash
sudo apt update
sudo apt install python3 python3-pip git
git clone <your-repo-url>
cd Korea_bot
pip3 install -r requirements.txt
```

3. Создайте systemd сервис:
```bash
sudo nano /etc/systemd/system/korea-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Korea Car Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Korea_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. Запустите сервис:
```bash
sudo systemctl enable korea-bot
sudo systemctl start korea-bot
```

## Переменные окружения

Создайте файл `.env` или установите переменные окружения:

```env
API_TOKEN=your_bot_token
GROUP_CHAT_ID=your_group_chat_id
```

## Структура проекта

- `bot.py` - основной файл бота
- `cars.json` - база данных автомобилей
- `requirements.txt` - зависимости Python
- `Procfile` - конфигурация для Heroku/Railway
