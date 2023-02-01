import socket
import traceback
import sys
import RspDeafultHandlers
def decodeArgs(str:str):
    if str.endswith("+"):
        return {str[0:-1]:True}
    if str.endswith("-"):
        return {str[0:-1]:False}
    if "=" in str:
        v = str.split("=")
        return {v[0]:v[1]}
    raise Exception(f"unkown args format:{str}")
def encodeArgs(k, v):
    if v == True:
        return k + "+"
    if v == False:
        return k + "-"
    if v is not None:
        return k + "=" + str(v)
    return k
def calcChecksum(data):
    return "{:02x}".format(sum(ord(c) for c in data) & 0xff)
def encode(dic):
    if type(dic) != dict:
        ret = str(dic)
    else:
        ret =  ";".join([encodeArgs(k,v) for k,v in dic.items()])
    ret = str.encode("+$" + ret + "#" + str(calcChecksum(ret)))
    print(f"sending:{ret}")
    return ret
    pass
def decode(bytes):
    if not bytes:
        return None
    print(f"raw data:{bytes}")
    data = bytes.decode('utf-8')
    data = data.split("$")[1]
    checksum = data.split("#")[-1]
    data = data.split("#")[0]
    

    calchecksum =  calcChecksum(data)
    if checksum != calchecksum:
        print(data)
        print(checksum, calchecksum)
        raise Exception("fail to check checksum")
    
    t = data.split(":")[0]
    data = "".join(data.split(":")[1:])
    args = {}
    if len(data) > 0:
        data = data.split(";")
        for x in data:
            args.update(decodeArgs(x))

    return [t, args]
    # data = data.split("")

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
                    self.updHandler(func.__doc__, func)
    def updHandler(self, key:str, func):
        self.queryHandlers[key] = func
    def handle(data):
        pass
    def run_once(self):
        try:
            data = self.conn.recv(1024)
            if data == b'+':
                return True
            data = decode(data)
            if not data:
                raise Exception("rsp init data not recv")
            # print(f"recv data:{data}")
            resp = None
            if data[0] not in self.queryHandlers:
                resp = RspDeafultHandlers.Handle_AnyCase(data[0], **data[1])
            else:
                resp = self.queryHandlers[data[0]](**data[1])
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
