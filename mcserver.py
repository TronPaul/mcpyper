import os
import shutil
from time import sleep
from functools import update_wrapper
from subprocess import Popen, PIPE, STDOUT
from urllib import urlretrieve

def clean_dir(path, exempt=[]):
    files = (f for f in os.listdir(path) if f not in
        exempt)
    for x in files:
        fullpath = os.path.join(path, x)
        if os.path.isfile(fullpath):
            os.remove(fullpath)
        elif os.path.isdir(fullpath):
            shutil.rmtree(fullpath)

def with_killing(f):
    def wrapper_func(self, *args, **kwargs):
        if self.is_running:
            self.kill()
        return f(self, *args, **kwargs)
    return update_wrapper(wrapper_func, f)

def with_restarting(f):
    def wrapper_func(self, *args, **kwargs):
        restart = self.is_running
        if restart:
            self.stop()
        ret = f(self, *args, **kwargs)
        if restart:
            self.start()
        return ret
    return update_wrapper(wrapper_func, f)

def with_saving_paused(f):
    def wrapper_func(self, *args, **kwargs):
        self.save_off()
        self.save_all()
        ret = f(self, *args, **kwargs)
        self.save_on()
        return ret
    return update_wrapper(wrapper_func, f)

class MinecraftServer(object):
    jar_url = ('https://s3.amazonaws.com/MinecraftDownload'
            '/launcher/minecraft_server.jar')
    def __init__(self, proc_dir='/home/tron/minecraft', max_memory=1024,
            min_memory=1024, java_args=None, jar_args=None):
        self.args = self.build_args(min_memory, max_memory, java_args,
                jar_args)
        self.proc_dir = proc_dir
        self.backup_dir = str(proc_dir)
        self.proc = None

    def build_args(self, min_memory, max_memory, java_args, jar_args):
        args = ['java']
        if java_args is not None:
            java_args = [arg for arg in java_args if not arg.startswith('-Xmx')
                and not arg.startswith('-Xms')]
        else:
            java_args = []
        java_args.append('-Xms%dM' % min_memory)
        java_args.append('-Xmx%dM' % max_memory)
        args.extend(java_args)
        args.append('-jar')
        args.append('minecraft_server.jar')
        args.append('-nogui')
        if jar_args is not None:
            args.extend(jar_args)
        return args

    @property
    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    @property
    def world_path(self):
        return os.path.join(self.proc_dir, self.world_name)

    @property
    def world_name(self):
        return 'world'

    def download_jar(self, filename):
        jar_path = os.path.join(self.proc_dir, filename)
        urlretrieve(self.jar_url, jar_path)

    @with_killing
    def install(self):
        clean_dir(self.proc_dir)
        self.download_jar('minecraft_server.jar')

    @with_killing
    def uninstall(self):
        clean_dir(self.proc_dir)

    @with_killing
    def clean(self):
        clean_dir(self.proc_dir, ['minecraft_server.jar'])

    @with_restarting
    def update(self):
        self.download_jar('minecraft_server.jar')

    def start(self):
        if self.is_running:
            raise Exception
        self.proc = Popen(self.args, bufsize=1, cwd=self.proc_dir,
            stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

    def stop(self):
        if not self.is_running:
            raise Exception
        self.save_off()
        self.save_all()
        self.rcon('stop')
        self.proc.wait()

    def restart(self):
        self.stop()
        self.start()

    def kill(self):
        if not self.is_running:
            raise Exception
        self.proc.kill()
        self.proc.wait()

    def rcon(self, command):
        self.proc.stdin.write('%s\n' % command)

    def save_off(self):
        self.rcon('save-off')

    def save_on(self):
        self.rcon('save-on')

    def save_all(self):
        self.rcon('save-all')
        sleep(10)

    @with_restarting
    def delete_world(self):
        shutil.rmtree(self.world_path)

    @with_saving_paused
    def compress_world(self, filename):
        backup_path = os.join(self.backup_dir, filename)
        compress_proc = Popen(['tar', '-czvf', backup_path, self.world_path])
        compress_proc.wait()
        return backup_path
