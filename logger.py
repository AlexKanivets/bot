import logging
import sys

# Настройка базового логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

# Создаем основной логгер
logger = logging.getLogger('bot')

# Устанавливаем уровень логирования
logger.setLevel(logging.INFO)

# Создаем форматтер для логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Добавляем обработчики
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)