import logging
import re

import psycopg2
import paramiko
from dotenv import load_dotenv
import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def find_phone_number_Command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров или введите "БД", чтобы получить все номера телефонов из базы данных:')

    return 'find_phone_number'

def add_phone_number_to_db_Command(update: Update, context):

    return 'add_phone_number_to_db'

def add_email_to_db_Command(update: Update, context):

    return 'add_email_to_db'

def find_email_Command(update: Update, context):
    update.message.reply_text('Введите текст для поиска адресов электронной почты или введите "БД", чтобы получить все адреса электронной почты из базы данных:')

    return 'find_email'

def verify_password_Command(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его надёжности:')

    return 'verify_password'

def get_release_Command(update: Update, context):
    return 'get_release'

def get_uname_Command(update: Update, context):
    return 'get_uname'

def get_uptime_Command(update: Update, context):
    return 'get_uptime'

def get_df_Command(update: Update, context):
    return 'get_df'

def get_free_Command(update: Update, context):
    return 'get_free'

def get_mpstat_Command(update: Update, context):
    return 'get_mpstat'

def get_w_Command(update: Update, context):
    return 'get_w'

def get_auths_Command(update: Update, context):
    return 'get_auths'

def get_critical_Command(update: Update, context):
    return 'get_critical'

def get_ps_Command(update: Update, context):
    return 'get_ps'

def get_ss_Command(update: Update, context):
    return 'get_ss'

def get_services_Command(update: Update, context):
    return 'get_services'

def get_apt_list_Command(update: Update, context):
    update.message.reply_text('Введите название пакета для поиска или введите all, чтобы получить список всех пакетов:')
    return 'get_apt_list'

def get_repl_logs_Command(update: Update, context):
    return 'get_repl_logs'

def find_phone_number(update: Update, context):
    user_input = update.message.text
    if user_input == 'БД':
        try:
            conn = psycopg2.connect(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}")
            cursor = conn.cursor()
            cursor.execute("SELECT phone_number FROM phone_numbers;") 
            phone_numbers = cursor.fetchall()
            conn.close()

            phone_numbers_list = "\n".join([phone_number[0] for phone_number in phone_numbers]) or update.message.reply_text("Номера телефонов не были найдены в бд") and logging.info('find_phone_number numbers weren`t found in db')
            update.message.reply_text(phone_numbers_list)
        except Exception as e:
            print(f"Error: {e}")
            logging.error("find_phone_number exit 1")
            update.message.reply_text("Произошла ошибка при подключении к БД")
        return ConversationHandler.END


    else:
        phone_patterns = [
            r"[+78]\s?\(\d{3}\)\s?\d{3}-\d{2}-\d{2}",  # +7/8 (XXX) XXX-XX-XX
            r"[+78]\s?\(\d{3}\)\s?\d{7}",            # +7/8 (XXX) XXXXXXX
            r"[+78]\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}",    # +7/8 XXX XXX XX XX
            r"[+78]-\d{3}-\d{3}-\d{2}-\d{2}",           # +7/8-XXX-XXX-XX-XX
            r"[+78]\d{10}"                             # +7/8XXXXXXXXXX
        ]

        phone_numbers_list = []
        for pattern in phone_patterns:
            phoneNumRegex = re.compile(pattern)
            found_numbers = phoneNumRegex.findall(user_input)
            phone_numbers_list.extend(found_numbers) #  Используем extend для добавления элементов списка

        # Удаляем дубликаты, сохраняя порядок
        seen = set()
        phone_numbers_list = [x for x in phone_numbers_list if not (x in seen or seen.add(x))]

        if not phone_numbers_list:
            update.message.reply_text('Телефонные номера не найдены')
            logging.info("find_phone_number no numbers was found")
            logging.info("find_phone_number exit 0")
            return ConversationHandler.END
        
        context.user_data['found_numbers'] = phone_numbers_list
        for i in phone_numbers_list:
            update.message.reply_text(i)
        logging.info("find_phone_number found numbers")

        update.message.reply_text("Хотите ли вы добавить найденные номера телефонов в базу данных [Да/Нет]?")
        logging.info("find_phone_numbers exit 0")
        return 'add_phone_number_to_db'
    
def add_phone_number_to_db(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == "да":
        try:
            conn = psycopg2.connect(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}")
            cursor = conn.cursor()
            for i in context.user_data['found_numbers']:
                cursor.execute(f"INSERT INTO phone_numbers(phone_number) VALUES ('{i}');") 
            conn.commit()
            conn.close()
            update.message.reply_text("Данные были добавлены в базу данных")
            logging.info("find_phone_number has added data to db")
            return ConversationHandler.END
        except Exception as e:
            print(f"Error: {e}")
            logging.error("find_phone_number exit 1")
            update.message.reply_text("Произошла ошибка при подключении к БД")
            return ConversationHandler.END
    else:
        update.message.reply_text("Данные не были добавлены в БД")
        logging.info("find_phone_number user refused to insert data into db")
        logging.info("find_phone_number exit 0")
        return ConversationHandler.END

def find_email(update: Update, context):
    user_input = update.message.text
    if user_input == "БД":
        try:
            conn = psycopg2.connect(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}")
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM emails;") 
            emails = cursor.fetchall()
            conn.close()

            emails_list = "\n".join([email[0] for email in emails]) or update.message.reply_text("Адреса электронных почт не были найдены в бд") and logging.info('find_email emails weren`t found in db')
            update.message.reply_text(emails_list)
        except Exception as e:
            print(f"Error: {e}")
            logging.error("find_email exit 1")
            update.message.reply_text("Произошла ошибка при подключении к БД")
        return ConversationHandler.END
    else:
        emailRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

        emailList = emailRegex.findall(user_input)

        if not emailList:
            update.message.reply_text('Адреса электронной почты не найдены')
            logging.info("find_email email was found")
            logging.info("find_email exit 0")
            return ConversationHandler.END
        
        emails = ''
        for i in range(len(emailList)):
            emails += f'{i+1}. {emailList[i]}\n'

        context.user_data['found_emails'] = emailList
        update.message.reply_text(emails)
        logging.info("find_email email was found")
        update.message.reply_text("Хотите ли вы добавить найденные адреса электронной почты в базу данных [Да/Нет]?")
        logging.info("find_email exit 0")
        return 'add_email_to_db'
    
def add_email_to_db(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == "да":
        try:
            conn = psycopg2.connect(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}")
            cursor = conn.cursor()
            for i in context.user_data['found_emails']:
                cursor.execute(f"INSERT INTO emails(email) VALUES ('{i}');") 
            conn.commit()
            conn.close()
            update.message.reply_text("Данные были добавлены в базу данных")
            logging.info("find_email has added data to db")
            return ConversationHandler.END
        except Exception as e:
            print(f"Error: {e}")
            logging.error("find_email exit 1")
            update.message.reply_text("Произошла ошибка при подключении к БД")
            return ConversationHandler.END
    else:
        update.message.reply_text("Данные не были добавлены в БД")
        logging.info("find_email no data was inserted into db")
        logging.info("find_email exit 0")
        return ConversationHandler.END

def verify_password(update: Update, context):
    user_input = update.message.text
    
    if len(user_input) == 0:
        update.message.reply_text("Вы ничего не ввели")
        logging.info("verify_password no input")
        logging.info("verify_password exit 0")

    elif len(user_input) < 8 or not re.search(r'[A-Z]', user_input) or not re.search(r'[a-z]', user_input) or \
          not re.search(r'[0-9]', user_input) or not re.search(r'[!@#$%^&*().]', user_input):
        update.message.reply_text("Пароль простой")
    else:
        update.message.reply_text("Пароль сложный")
    
    logging.info("verify_password exit 0")
    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def get_release(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_release exit 1")
    stdin, stdout, stderr = client.exec_command('lsb_release -a')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)
    logging.info("get_release exit 0")

    return ConversationHandler.END

def get_uname(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_uname exit 1") 
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)
    logging.info("get_uname exit 0")

    return ConversationHandler.END

def get_uptime(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_uptime exit 1") 
    stdin, stdout, stderr = client.exec_command('uptime')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)
    logging.info("get_uptime exit 0")

    return ConversationHandler.END

def get_df(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_df exit 1") 
    stdin, stdout, stderr = client.exec_command('df -h')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

    logging.info("get_df exit 0")
    return ConversationHandler.END

def get_free(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_df exit 1") 
    stdin, stdout, stderr = client.exec_command('free')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

    logging.info('get_df exit 0')
    return ConversationHandler.END

def get_mpstat(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_mpstat exit 1") 
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

    logging.info("get_mpstat exit 0")
    return ConversationHandler.END

def get_w(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_w exit 1")
    stdin, stdout, stderr = client.exec_command('w')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

    logging.info("get_w exit 0")
    return ConversationHandler.END

def get_auths(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_auths exit 1") 
    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

    logging.info("get_auths exit 0")
    return ConversationHandler.END

def get_critical(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_critical exit 1") 
    stdin, stdout, stderr = client.exec_command('journalctl -p crit -n 10')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

    logging.info("get_critical exit 0")
    return ConversationHandler.END

def get_ps(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_ps exit 1") 
    stdin, stdout, stderr = client.exec_command('ps')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

    logging.info("get_ps exit 0")
    return ConversationHandler.END

def get_ss(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_ss exit 1") 
    stdin, stdout, stderr = client.exec_command('ss')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    
    lines = [line for line in data.split('\n') if line.strip()]
    if not lines:
        update.message.reply_text("Ничего не найдено.")
        return ConversationHandler.END

    for i in range(0, len(lines), 20):
        chunk = '\n'.join(lines[i:i + 20])
        update.message.reply_text(chunk)

    logging.info("get_ss exit 0")
    return ConversationHandler.END

def get_apt_list(update: Update, context):
    user_input = update.message.text
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_apt_list exit 1")

    if user_input == 'all':
        stdin, stdout, stderr = client.exec_command('dpkg -l')
    else:
        stdin, stdout, stderr = client.exec_command(f'dpkg -l | grep {user_input}')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()

    lines = [line for line in data.split('\n') if line.strip()]
    if not lines:
        update.message.reply_text("Ничего не найдено.")
        return ConversationHandler.END

    for i in range(0, len(lines), 20):
        chunk = '\n'.join(lines[i:i + 20])
        update.message.reply_text(chunk)

    logging.info("get_apt_list exit 0")
    return ConversationHandler.END

def get_services(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_services exit 1") 
    stdin, stdout, stderr = client.exec_command('service --status-all')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()

    lines = [line for line in data.split('\n') if line.strip()]
    if not lines:
        update.message.reply_text("Ничего не найдено.")
        return ConversationHandler.END

    for i in range(0, len(lines), 20):
        chunk = '\n'.join(lines[i:i + 20])
        update.message.reply_text(chunk)

    logging.info("get_services exit 0")
    return ConversationHandler.END

def get_repl_logs(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=os.getenv("DB_HOST"), username=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), port=os.getenv("RM_PORT"))
    except Exception as e:
        update.message.reply_text("Не удалось подключиться к хосту")
        logging.error("get_repl_logs exit 1") 
        client.close()
        return ConversationHandler.END
    stdin, stdout, stderr = client.exec_command('cat /var/log/postgresql/postgresql-16-main.log | grep "repl_user"')
    data = str(stdout.read() + stderr.read()).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()

    lines = [line for line in data.split('\n') if line.strip()]
    if not lines:
        update.message.reply_text("Ничего не найдено.")
        return ConversationHandler.END

    for i in range(0, len(lines), 20):
        chunk = '\n'.join(lines[i:i + 20])
        update.message.reply_text(chunk)

    logging.info("get_repl_logs exit 0")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик телефонов
    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_number_Command), CommandHandler('add_phone_number_to_db', add_phone_number_to_db_Command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'add_phone_number_to_db': [MessageHandler(Filters.text & ~Filters.command, add_phone_number_to_db)],
        },
        fallbacks=[]
    )
	
    convHandler_find_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_Command), CommandHandler('add_email_to_db', add_email_to_db_Command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'add_email_to_db': [MessageHandler(Filters.text & ~Filters.command, add_email_to_db)]
        },
        fallbacks=[]
    )

    convHandler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_Command)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandler_get_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_Command)],
        states={
            "get_apt_list": [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerfind_phone_number)
    dp.add_handler(convHandler_find_email)
    dp.add_handler(convHandler_verify_password)
    dp.add_handler(convHandler_get_apt_list)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    # dp.add_handler(convHandler_ssh_connect)

	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()