# FunPay Auto Steam Guard

🔐 Бот для автоматической генерации кодов Steam Guard на FunPay  
📌 Готов к использованию

## Что из себя представляет бот?

Это Python-скрипт, который:      
✔ Автоматически генерирует коды Steam Guard по запросу  
✔ Можно добавить более одного аккаунта   
✔ Использует защищённое хранение данных аутентификации  
✔ Работает с SDA (Steam Desktop Authenticator)  

## Что нужно для работы бота?
1. Установка Python и библиотек
```pip install -r requirements.txt```
2. Привязанный SDA к аккаунту Steam и `shared_secret` из вашего `mafile`.
3. Настройка .env
```
FUNPAY_AUTH_TOKEN=ваш_golden_key
SHARED_SECRET_0=SHARED_SECRET_0
COMMAND_SECRET_0=!0
LIMIT_SECRET_0=любое
PERIOD_SECRET_0=любое
```

По всем багам, вопросам и предложеням пишите в [Issues](https://github.com/tinechelovec/Funpay-Auto-Steam-Guard/issues) или в [Telegram](https://t.me/tinechelovec)

Другие боты и плагины [Channel](https://t.me/by_thc)
