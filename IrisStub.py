import os, sys
import utils
import traceback

sys.path.append('/home/user/fvp/Base_RevC_AEMvA_pkg/Iris/Python')
import iris.debug
port = int(os.environ["iris_port"])
print(f"fvp port: {port}")
model = iris.debug.NetworkModel("localhost",port)
cpu = None
def read_int(cpu, addr, bsize):
    if bsize == 0:
        return 0
    mem = cpu.read_memory(addr, size = bsize, count = 1)
    ans = int(0)
    for i in range(bsize):
        ans = ans | mem[-(i+1)] << (8*i)
    return ans
def read_int32(cpu, addr):
    return read_int(cpu,addr,4)


def set_brk(cpu, addr):
    bptinfos = []
    for space in cpu._memory_spaces_by_name.keys():
        try:
            bptinfos.append(cpu.add_bpt_prog(addr, memory_space=space))
        except:
            pass
    return bptinfos
def clear_brks(cpu):
    for space in cpu._memory_spaces_by_name.keys():
        try:
            cpu.clear_bpts()
        except:
            pass
brk_dir = {}

def add_brk( addr):
    assert addr not in brk_dir
    brk_dir[addr] = [info for cc in model.get_cpus() for info in set_brk(cc, addr)]

def del_brk(addr):
    assert addr in brk_dir
    for bpt in brk_dir[addr]:
        bpt.delete()
    brk_dir.pop(addr)
def run_util_hit():
    model.run()
    bpts = [bpt  for cc in model.get_cpus() for bpt in cc.get_hit_breakpoints()]

    global cpu 
    cpu = bpts[0].target

def IrisInit():
    start_addr = int(os.environ["exec_address"], 16) + 0x2000
    add_brk(start_addr)
    run_util_hit()
    
    del_brk(start_addr)
    


def HandleStopReply(args):
    '''?'''
    return "S05"

def HandleIfAttached(args):
    '''q,Attached'''
    return "1"

def HandleQOffset(args):
    '''q,Offsets'''
    return ""
def HandleQSymbol(args):
    '''q,Symbol'''
    return ""

def HandleReadAll(args):
    '''g'''
    return "".join([getRegByID(x) for x in range(32)])

def HandleReadMem(args):
    '''m'''
    addr, bsize = [int(x, 16) for x in args.split(',')]
    # print(f"try read memory at {addr:#x} {bsize}")
    ret = ""
    try:
        if bsize >= 8:
            ret +="".join(["{:02x}".format(b) for b in cpu.read_memory(addr, size = 8, count = bsize // 8)])
            addr += bsize // 8 * 8
            bsize = bsize % 8
        return ret + utils.int2str(read_int(cpu,addr,bsize), bsize)
    except ValueError as e:
        return "N"
def getRegByID(regnum):
    name = ""
    if regnum <= 30:
        name = f"X{regnum}"
    elif regnum == 31:
        name = "SP"
    elif regnum == 32:
        name = "PC"
    elif regnum == 33:
        name = "AArch64 Core.CPSR"
    elif regnum == 0x42:
        name = "FPSR"
    elif regnum == 0x43:
        name = "FPCR"
    else:
        raise Exception(f"reg num {regnum} not right")

    try:
        return utils.int2str(cpu.read_register(name), 8)
    except ValueError as e:
        print(f"can not acces reg {name}")
        traceback.print_exc()
        return "f"*16


def HandleReadReg(args):
    '''p'''
    regnum = int(args, 16)
    return getRegByID(regnum)
def HandlevCont(args):
    '''v,Cont'''
    return ""
def HandleHc0(args):
    '''H,c'''
    if args == "0":
        return "OK"

def HandleRun(args):
    '''c'''
    run_util_hit()
    return "S05"

def HandleInsertBpt(args):
    '''Z'''
    type0, addr, type1 = [int(x,16) for x in args.split(",")]
    if type0 == 0 and type1 == 4:
        add_brk(addr)
        return "OK"
    return None
def HandleRemoveBpt(args):
    '''z'''
    type0, addr, type1 = [int(x,16) for x in args.split(",")]
    if type0 == 0 and type1 == 4:
        del_brk(addr)
        return "OK"
    return None

def HandleStepi(args):
    '''s'''
    model.step(count = 1)
    return "S05"