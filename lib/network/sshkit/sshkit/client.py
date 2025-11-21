import sys
import paramiko
import threading
from paramiko.channel import ChannelStdinFile, ChannelStderrFile, ChannelFile

# exit codes
# 0     = success
# 127   = command not found
# 1-255 = failure 
# 2     = bad ussage

EXEC_RESP = tuple[ChannelStdinFile, ChannelFile, ChannelStderrFile]

class Client(paramiko.SSHClient):
    def __init__(self, host, **kwargs):
        self.host = host
        self.user = kwargs.get("user", "admin")
        self.pswd = kwargs.get("pswd", "password")
        self.id_rsa = kwargs.get("id_rsa", None)
        self.__hostname = ''
        self.connected = False
        self._lock = threading.Lock()
        super().__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __parse_exec(self, res: EXEC_RESP):
        _, stdout, stderr = res
        channel = stdout.channel
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        code = channel.recv_exit_status()
        return code, out, err

    def connect(self):
        with self._lock:
            try:
                if self.id_rsa: super().connect(self.host, username=self.user, key_filename=self.id_rsa, timeout=0.5)
                else: super().connect(self.host, username=self.user, password=self.pswd, timeout=0.5)
                self.connected = True
            except:
                raise Exception(f"connect to {self.host} failed due to timeout")

    def close(self):
        with self._lock:
            try: super().close()
            except: pass
            self.connected = False

    def exec_command(self, command) -> EXEC_RESP:
        with self._lock:
            try:
                return super().exec_command(command)
            except Exception as e:
                print(f"[exec_command] Error running command '{command}': {e}", file=sys.stderr)
                # return None, None, None
                return ChannelStdinFile(), ChannelStderrFile(), ChannelFile()

    def safe_exec_command(self, command: str) -> EXEC_RESP:
        """ Ensures connect/disconnect, runs command, returns (stdin, stdout, stderr). """
        isConnected = bool(self.connected)
        if (not isConnected): self.connect()
        res = self.exec_command(command)
        if (not isConnected):
            res[1].channel.recv_exit_status()
            self.close()
        return res
    
    def exec_parse(self, command: str) -> tuple[int,str,str]:
        res = self.safe_exec_command(command)
        return self.__parse_exec(res)

    def get_hostname(self) -> str:
        if self.__hostname:  return self.__hostname
        code, out, err = self.exec_parse("hostname")
        if code==0: self.__hostname = out
        return self.__hostname
    hostname = property(get_hostname)

        

if __name__ == "__main__":
    client = Client("192.168.5.22", user="admin", pswd="handsome")
    client.connect()
    res = client.exec_parse("echo hello")
    print(res)
    print(client.hostname)
    client.close()
