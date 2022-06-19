'''
交叉编译 open ssh
    1: 编译 zlib
    2: 编译 openssl
    3: 编译 openssh
'''

#%% import all
import threading
import urllib.request as urllib2
from config import *
import os

rootDir =os.path.abspath(os.curdir)

#%% 定义函数
class DownloadThread(threading.Thread):
    __downloadUrl : str
    __fileName : str

    def __init__(self,saveFolder,downloadUrl : str):
        threading.Thread.__init__(self)
        self.__downloadUrl = downloadUrl
        self.__fileName = os.path.join(saveFolder,downloadUrl.split('/')[-1])

    def run(self):
        if(os.path.isfile(self.__fileName)):
            return
        remoteF = urllib2.urlopen(self.__downloadUrl) 
        with open(self.__fileName, "wb") as saveFile:
            saveFile.write(remoteF.read())

def MakeSureFolderExist(folderUrl):
    if os.path.exists(folderUrl):
        if os.path.isdir(folderUrl):
            return
        else:
            print("路径已存在,但并不是文件夹")

    else:
        try:
            os.makedirs(folderUrl)
        except Exception:
            print("创建文件夹失败.")
        else:
            pass

        

#%% 下载文件
MakeSureFolderExist(download_folder)

dZlib = DownloadThread(download_folder,zlib_url)
dSSL = DownloadThread(download_folder,ssl_url)
dSSH = DownloadThread(download_folder,ssh_url)

dZlib.start()
dSSL.start()
dSSH.start()

dZlib.join()
dSSL.join()
dSSH.join()

# %% 解压 编译 zlib
zlibFileName = os.path.join(download_folder,zlib_url.split('/')[-1])
zlibFilePath = os.path.abspath(zlibFileName)

MakeSureFolderExist(source_folder)
os.chdir(source_folder)

# 解压
if not os.path.exists("zlib"):
    oldFolders = os.listdir()
    os.system("tar -xvf "+ zlibFilePath)
    newFolders = os.listdir()

    for folderName in newFolders:
        if folderName not in oldFolders:
            os.rename(folderName,"zlib")
            break

# 编译
zlibOptFolder = os.path.join(rootDir,install_folder,"zlib")
if not os.path.exists(zlibOptFolder):
    os.chdir("zlib")
    os.system("prefix={0} CC={1}gcc CFLAGS=\"-fPIC\" ./configure".format(zlibOptFolder,cc_prefix))
    os.system("make -j4 && make install")

# 返回root
os.chdir(rootDir)

# %% 解压编译 openssl
sslFileName = os.path.join(download_folder,ssl_url.split('/')[-1])
sslFilePath = os.path.abspath(sslFileName)

# 移动到编译目录
MakeSureFolderExist(source_folder)
os.chdir(source_folder)

# 解压ssl
if not os.path.exists("openssl"):
    oldFolders = os.listdir()
    os.system("tar -xvf "+ sslFilePath)
    newFolders = os.listdir()

    for folderName in newFolders:
        if folderName not in oldFolders:
            os.rename(folderName,"openssl")
            break

sslOptFolder = os.path.join(rootDir,install_folder,"openssl")
if not os.path.exists(sslOptFolder):
    os.chdir("openssl")

    # cur
    os.system("./Configure --prefix={0} --cross-compile-prefix={1} no-asm shared linux-armv4".format(sslOptFolder,cc_prefix))

    os.system("make -j4 && make install")

os.chdir(rootDir)

# %%
sshFileName = os.path.join(download_folder,ssh_url.split('/')[-1])
sshFilePath = os.path.abspath(sshFileName)

# 移动到编译目录
MakeSureFolderExist(source_folder)
os.chdir(source_folder)

# 解压ssl
if not os.path.exists("openssh"):
    oldFolders = os.listdir()
    os.system("tar -xvf "+ sshFilePath)
    newFolders = os.listdir()

    for folderName in newFolders:
        if folderName not in oldFolders:
            os.rename(folderName,"openssh")
            break

#%% next 编译
sshOptFolder = os.path.join(rootDir,install_folder,"openssh")
if not os.path.exists(sshOptFolder):
    os.chdir("openssh")

    os.system("./configure \
        --host={0} \
        --with-zlib={1} \
        --with-ssl-dir={2} \
        --disable-etc-default-login \
        LDFLAGS=\"-pthread\"".format(cc_prefix[:-1],zlibOptFolder,sslOptFolder,))

    os.system("make -j4")

    tarSshOpt = os.path.join(sshOptFolder,"bin")
    os.makedirs(tarSshOpt)
    os.system("cp scp sftp ssh ssh-add ssh-agent ssh-keygen ssh-keyscan " + tarSshOpt)
    
    tarSshOpt = os.path.join(sshOptFolder,"etc")
    os.makedirs(tarSshOpt)
    os.system("cp moduli ssh_config sshd_config " + tarSshOpt)

    tarSshOpt = os.path.join(sshOptFolder,"libexec")
    os.makedirs(tarSshOpt)
    os.system("cp sftp-server ssh-keysign " + tarSshOpt)

    tarSshOpt = os.path.join(sshOptFolder,"sbin")
    os.makedirs(tarSshOpt)
    os.system("cp sshd " + tarSshOpt)

    
os.chdir(rootDir)
# %%
