#! /usr/bin/env python3

import bincli, sys, os

def load_key():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(this_dir, 'key.txt'), 'r') as f:
        return [x.strip() for x in f][0]
      
def load_sec():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(this_dir, 'sec.txt'), 'r') as f:
        return [x.strip() for x in f][0]

def save_key(data):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(this_dir, 'key.txt'), 'w') as f:
        f.write(f'{data}\n')
        
def save_sec(data):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(this_dir, 'sec.txt'), 'w') as f:
        f.write(f'{data}\n')

if __name__ == '__main__':
    if sys.argv[1] == 'api':
        save_key(sys.argv[2])
        save_sec(sys.argv[3])    
    elif sys.argv[1] == 'run':
        key = load_key()
        sec = load_sec()
        sym = sys.argv[2]
        lev = sys.argv[3] 
        mar = sys.argv[4] 
        pos = sys.argv[5] 
        binbot = bincli.BinanceClient(key, sec)
        binbot.run(sym, lev, str(mar), pos)
    else:
      else:
        print('set api: bincli.py [api] [key] [secret]')
        print('run client: bincli.py [run] [symbol] [leverage] [margin] [side]')
    sys.exit()
