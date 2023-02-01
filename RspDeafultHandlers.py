def Handle_AnyCase(t ,**kwargs):
    dic = {"vMustReplyEmpty", "Hg0", "qTStatus", "qfThreadInfo", "qL", "Hc-1", "qC"} 
    for v in dic:
        if t.startswith(v):
            return {}
    raise Exception(f"{t} not in {dic}")
def Handle_support(**kwargs):
    """qSupported"""
    return {"PacketSize":1024, "hwbreak": True, "QStartNoAckMode": True}

def Handle_noack(**kwargs):
    """QStartNoAckMode"""
    return {"OK":None}
