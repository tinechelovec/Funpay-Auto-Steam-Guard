# FunPay Auto Steam Guard

🔐 Бот для автоматической генерации кодов Steam Guard на FunPay  
📌 Готов к использованию

## Что из себя представляет бот?

Это Python-скрипт, который:      
✔ Автоматически генерирует коды Steam Guard по запросу  
✔ Интегрируется с FunPay для обработки команд  
✔ Использует защищённое хранение данных аутентификации  
✔ Работает с SDA (Steam Desktop Authenticator)  

## Что нужно для работы бота?
1. Установка Python и библиотек
```pip install -r requirements.txt```
2. Привязанный SDA к аккаунту Steam и `shared_secret` из вашего `mafile`.
3. Настройка .env
```
FUNPAY_AUTH_TOKEN=ваш_golden_key
STEAM_SHARED_SECRET=ваш_shared_secret
```
4. Если сделали все праильно, то по команде ```!код```, код от Steam Guard будет приходить.

По всем багам, вопросам и предложеням пишите в [Issues](https://github.com/tinechelovec/Funpay-Auto-Steam-Guard/issues) или в [Telegram](https://t.me/tinechelovec)

Другие боты [Channel](https://t.me/by_thc)
