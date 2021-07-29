# BACKUPER
Backup folder  and mysql database in .zip archive with AES encripted.


# Requirements
 * Fill in the file config.ini
 * Create .venv with python 3.8
 * Install Poetry and execute command
    > poetry install
   
 * Start script

# IMPORTANT 

After start script create keys in keys/crypto.key You must keep this key in a safe place, it is required to decode your archives. In case of loss, you will not be able to restore your backups.

# Information
After running the script, backups will be created every night at 1.30, but you can always change the time and interval. 
[Read more](https://schedule.readthedocs.io/en/stable/) 

More info about [AES](https://wikipedia.org/wiki/AES)

