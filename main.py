from RspServer import RspServer
import IrisStub

if __name__ == "__main__":
    server = RspServer(2333)
    server.rsp_init()
    server.importHandlers(IrisStub)
    server.run()
