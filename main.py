import os
import sys
import shutil
import zipfile
import time
import schedule
from get_config import GetConfig
from cryptography.fernet import Fernet
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")

TIME = time.strftime("%Y%m%d-%H%M%S")
path_file_ini = "config.ini"
CONFIG = GetConfig.get_config(path_file_ini)
SETTINGS = CONFIG["settings"]
MYSQL_SETTINGS = CONFIG["mysql"]
KEY_NAME = SETTINGS["crypto_key"]
TEMP_FOLDER = f'{SETTINGS["temp_folder"]}{TIME}/'
OUTPUT_FOLDER = SETTINGS["output_folder"]


DB_HOST = MYSQL_SETTINGS["host"]
DB_USER = MYSQL_SETTINGS["user"]
DB_USER_PASSWORD = MYSQL_SETTINGS["password"]
DB_NAMES = MYSQL_SETTINGS["db_names"]
PATH_MYSQLDUMP = MYSQL_SETTINGS["path_mysqldump"]


def create_crypto_key():
    key = Fernet.generate_key()
    with open(f"keys/{KEY_NAME}", "wb") as file:
        file.write(key)
    return key


def load_key():
    return open(f"keys/{KEY_NAME}", "rb").read()


def encrypt_file(filename, key):
    time_start = time.time()
    f = Fernet(key)
    with open(filename, "rb") as file:
        data = file.read()
    encrypted_data = f.encrypt(data)
    with open(filename, "wb") as file:
        file.write(encrypted_data)
    logger.info(f'{round(time.time() - time_start, 2)} second encrypted')


def decrypt_file(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    with open(filename, "wb") as file:
        file.write(decrypted_data)


def backup_mysql(path):
    try:
        if not DB_HOST or not DB_USER or not DB_USER_PASSWORD or not DB_NAMES:
            raise ValueError("Missing values")
        dumpcmd = (
            PATH_MYSQLDUMP
            + " -h"
            + DB_HOST
            + " -u"
            + DB_USER
            + " -p"
            + DB_USER_PASSWORD
            + " "
            + DB_NAMES
            + " > "
            + path
        )
        os.system(dumpcmd)
    except Exception as e:
        logger.error(f"Error {e}")


def list_type(input_value):
    if isinstance(input_value, str):
        return [input_value]
    return input_value


def remove_file(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        logger.error("The file does not exist")


def backup():
    TIME = time.strftime("%Y%m%d-%H%M%S")
    TEMP_FOLDER = f'{SETTINGS["temp_folder"]}{TIME}/'
    time_start = time.time()
    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)
    FILE_SQL = TIME + ".sql"
    PATH_SQL_FILE = TEMP_FOLDER + FILE_SQL
    if not os.path.exists(OUTPUT_FOLDER + TIME):
        os.mkdir(OUTPUT_FOLDER + TIME)

    try:
        zip_file = f"{TEMP_FOLDER}{TIME}.zip"
        zip = zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED)
        for folder in INPUT_FOLDERS:
            for root, dirs, files in os.walk(folder):
                if os.path.basename(root) in LIST_IGNORE_FOLDERS:
                    logger.info(f"IGNORE FOLDER {os.path.basename(root)}")
                    zip.write(os.path.join(root))
                    continue
                for file in files:
                    if file.split(".")[-1] in LIST_IGNORE_TYPE_FILE:
                        continue
                    zip.write(os.path.join(root, file))
        if SETTINGS["backup_mysql_bd"]:
            logger.info('Clone MYSQL DB')
            backup_mysql(PATH_SQL_FILE)
            if os.path.isfile(PATH_SQL_FILE):
                logger.info("Add sql file")
                zip.write(PATH_SQL_FILE, arcname="sql\\" + FILE_SQL)
                remove_file(PATH_SQL_FILE)
        zip.close()
        encrypt_file(zip_file, key)
        shutil.move(zip_file, OUTPUT_FOLDER + TIME)
    except Exception as e:
        logger.error(f'Error on crate_archive: {e}')
    finally:
        logger.info(f'{round(time.time() - time_start, 2)} second work with {OUTPUT_FOLDER}{TIME}/{TIME}.zip')
        shutil.rmtree(TEMP_FOLDER, ignore_errors=True)


if __name__ == "__main__":
    if not os.path.exists("keys/"):
        logger.info("Create keys folder")
        os.mkdir("keys/")
    if not os.path.isfile(f"keys/{KEY_NAME}"):
        logger.info("Create crypto.key")
        key = create_crypto_key()
        logger.warning(
            "Attention! The generated crypto.key must be stored in a safe place. If it is lost, it will be impossible to decrypt the data that was encrypted with this key."
        )
    else:
        key = load_key()

    INPUT_FOLDERS = list_type(SETTINGS["input_folders"])
    LIST_IGNORE_FOLDERS = list_type(SETTINGS["list_ignore_folders"])
    LIST_IGNORE_TYPE_FILE = list_type(SETTINGS["list_ignore_type_file"])

    schedule.every().hour.at("1:30").do(backup)
    while True:
        schedule.run_pending()
        time.sleep(1)


