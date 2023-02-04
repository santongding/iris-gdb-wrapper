import utils
def Handle_AnyCase(t):
    dic = {"vMustReplyEmpty", "Hg0", "qTStatus", "qfThreadInfo", "qL1200000000000000000", "Hc-1", "qC"} 
    if t in dic:
        return ""
    raise Exception(f"{t} not in {dic}")
def Handle_support(args):
    """q,Supported"""
    return ";".join([utils.EncodeArgs(k,v) for k, v in {"PacketSize":1024, "hwbreak": True, "QStartNoAckMode": True}.items()])

def Handle_noack(args):
    """Q,StartNoAckMode"""
    return "OK"

