import paramiko
import os
import sys
import yaml
from time import gmtime, strftime

'''

Snakeflash adalah sebuah script auto export dan import database
dari database local ke database server yang dikoneksikan melalui
jalur SSH

@author: Yusril Rapsanjani
@version: 1.0

'''

def parsingArg():
    with open("config.yml") as stream:
        config = yaml.safe_load(stream)

        host = config['config']['server_config']['host']
        username = config['config']['server_config']['user']
        password = config['config']['server_config']['password']

        srcuser = config['config']['src_db_config']['user']
        srcpw = config['config']['src_db_config']['password']
        srcdb = config['config']['src_db_config']['database']

        dstuser = config['config']['dst_db_config']['user']
        dstpw = config['config']['dst_db_config']['password']
        dstdb = config['config']['dst_db_config']['database']

        filename = config['config']['filename']

    return username, password, srcuser, srcpw, srcdb, dstuser, dstpw, dstdb, filename, host

def getTime():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def dumpingDatabase(user, password, database, filename):
    os.system('mysqldump --user="{}" --password="{}" {} > files/{}'.format(user, password, database, filename))
    print("[{}]  Successfully dump database".format(getTime()))

def connectSSH(host, user, password):
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(host,22,username=user,password=password,timeout=4)

    return s

def importDatabase(s, Mysqluser, Mysqlpassword, database, filename):
    stdin, stdout, stderr = s.exec_command('mysql --user="{}" --password="{}" {} < /home/{}'
        .format(Mysqluser, Mysqlpassword, database, filename))

username, password, srcuser, srcpw, srcdb, dstuser, dstpw, dstdb, filename, host = parsingArg()

print(" ")

print("[{}]  Trying to dump database".format(getTime()))
dumpingDatabase(srcuser, srcpw, srcdb, filename)

print("[{}]  Connecting to server SSH".format(getTime()))
s = connectSSH(host, username, password)
print("[{}]  Successfully connected!".format(getTime()))

print("[{}]  Trying to find backup files".format(getTime()))
#Base dir
files_dir = os.getcwd() + "/files"
sftp = s.open_sftp()
sftp.put(files_dir + "/" + filename, '/home/' + filename)
print("[{}]  Files {} successfully sended".format(getTime(),filename))

print("[{}]  Trying to import backup database".format(getTime()))
importDatabase(s, dstuser, dstpw, dstdb, filename)
print("[{}]  Import database successfully".format(getTime()))
