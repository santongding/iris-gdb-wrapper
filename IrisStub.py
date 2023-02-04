import os, sys
import utils
import traceback

sys.path.append('/home/user/fvp/Base_RevC_AEMvA_pkg/Iris/Python')
import iris.debug
port = int(os.environ["iris_port"])
print(f"fvp port: {port}")
model = iris.debug.NetworkModel("localhost",port)
cpu = None
def read_int(cpu, addr, bits):
    mem = cpu.read_memory(addr, size = bits, count = 1)
    ans = int(0)
    for i in range(bits):
        ans = ans | mem[-(i+1)] << (8*i)
    return ans
def read_int32(cpu, addr):
    return read_int(cpu,addr,4)


def set_brk(cpu, addr):
    for space in cpu._memory_spaces_by_name.keys():
        try:
            cpu.add_bpt_prog(addr, memory_space=space)
        except:
            pass
def clear_brks(cpu):
    for space in cpu._memory_spaces_by_name.keys():
        try:
            cpu.clear_bpts()
        except:
            pass 
def IrisInit():
    start_addr = int(os.environ["exec_address"], 16) + 0x2000
    for cc in model.get_cpus():
        set_brk(cc, start_addr)
    model.run()
    for cc in model.get_cpus():
        pc = int(cc.read_register("PC"))
        if pc == start_addr:
            global cpu
            cpu = cc
            print(f"success run to start address: 0x{start_addr:#x}")
    
    for cc in model.get_cpus():
        clear_brks(cc)
    


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
    addr, bits = [int(x, 16) for x in args.split(',')]
    print(f"try read memory at {addr:#x} {bits}")

    return ""
    return formats.format(read_int(cpu,addr,bits))
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

