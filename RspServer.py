import socket
import traceback
import sys
import RspDeafultHandlers
import re


def calcChecksum(data):
    return "{:02x}".format(sum(ord(c) for c in data) & 0xff)
def encode(data):
    ret = str(data)
    ret = str.encode("+$" + ret + "#" + str(calcChecksum(ret)))
    print(f"sending:{ret}")
    return ret

def decode(bytes):
    if not bytes:
        raise "not recv data"
    print(f"raw data:{bytes}")
    data = bytes.decode('utf-8')
    m = re.compile("^\+?\$([a-zA-Z?])([a-zA-Z]*)([^#]*)#([0-9a-zA-Z]{2})$").match(data)
    
    if not m:
        raise("fail to run re.")

    firestType = m[1]
    secondType = m[2]
    args = m[3]
    print(f"fi type: {firestType}, se type: {secondType} args: {args}")
    
    checksum = m[4]
   
    calchecksum =  calcChecksum(firestType + secondType + args)
    if checksum != calchecksum:
        print(data)
        print(checksum, calchecksum)
        raise Exception("fail to check checksum")
    
    return firestType, secondType, args

class RspServer:
    def __init__(self, port) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = ('localhost', int(port))
        self.queryHandlers = {}
        self.importHandlers(RspDeafultHandlers)
        self.sock.bind(server_address)
        pass
    def importHandlers(self, module):
        for v in dir(module):
            if v.startswith("Handle"):
                func = getattr(module, v)
                if callable(func) and func.__doc__:
                    m = re.compile("^([^#,]+)(,([^#,]*))?$").match(func.__doc__)
                    self.updHandler(m[1], m[3], func)
    def updHandler(self, fi, se, func):
        print(fi,se,func.__doc__)
        if fi not in self.queryHandlers:
            self.queryHandlers[fi] = {}
        if se:
            self.queryHandlers[fi][se] = func
        else:
            self.queryHandlers[fi]["AnySeType"] = func
    def handle(data):
        pass
    def run_once(self):
        try:
            data = self.conn.recv(1024)
            if data == b'+':
               return True
            fi,se,args = decode(data)
            resp = None
            if fi in self.queryHandlers:
                if se in self.queryHandlers[fi]:
                    resp = self.queryHandlers[fi][se](args)
                elif "AnySeType" in self.queryHandlers[fi]:
                    resp = self.queryHandlers[fi]["AnySeType"](se + args)
            # print(f"recv data:{data}")
            if resp is None:
                resp = RspDeafultHandlers.Handle_AnyCase(fi + se + args)
            self.conn.sendall(encode(resp))
        except Exception as e:
            traceback.print_exc()
            print(e)
            return False
        return True

    def rsp_init(self):
        self.sock.listen()
        self.conn, addr = self.sock.accept()
        if self.conn:
            print(f"connected: {addr}")
        else:
            raise Exception("rsp connect failed")   
        if not self.run_once():
            raise Exception("init failed")


    def run(self):
        while self.run_once():
            pass
