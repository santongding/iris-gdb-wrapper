def EncodeArgs(k, v):
    if v == True:
        return k + "+"
    if v == False:
        return k + "-"
    if v is not None:
        return k + "=" + str(v)
    return k

def DecodeArgs(str:str):
    if str.endswith("+"):
        return {str[0:-1]:True}
    if str.endswith("-"):
        return {str[0:-1]:False}
    if "=" in str:
        v = str.split("=")
        return {v[0]:v[1]}
    raise Exception(f"unkown args format:{str}")
def int2str(v:int, bits:int):
    ret = ""
    # print("convert {:016x}".format(v))
    for i in range(0, bits):
        ret += "{:02x}".format(255 & v)
        v = v >> 8
    return ret