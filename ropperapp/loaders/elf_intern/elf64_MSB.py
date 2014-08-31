from ctypes import *
from elf_gen import *
from ropperapp.disasm.arch import x86_64


Elf64_Addr = c_ulonglong
Elf64_Off = c_ulonglong
Elf64_Half = c_ushort
Elf64_Word = c_uint
Elf64_Sword = c_int
Elf64_Xword = c_ulonglong
Elf64_Sxword = c_longlong
uchar = c_ubyte


R_SYM = lambda i: i >> 32
R_TYPE = lambda i: i & 0xffffffff


class Ehdr(BigEndianStructure):
    _fields_ = [('e_ident', uchar * 16),
                ('e_type', Elf64_Half),
                ('e_machine', Elf64_Half),
                ('e_version', Elf64_Word),
                ('e_entry', Elf64_Addr),
                ('e_phoff', Elf64_Off),
                ('e_shoff', Elf64_Off),
                ('e_flags', Elf64_Word),
                ('e_ehsize', Elf64_Half),
                ('e_phentsize', Elf64_Half),
                ('e_phnum', Elf64_Half),
                ('e_shentsize', Elf64_Half),
                ('e_shnum', Elf64_Half),
                ('e_shstrndx', Elf64_Half)
                ]


class Shdr(BigEndianStructure):
    _fields_ = [('sh_name', Elf64_Word),
                ('sh_type', Elf64_Word),
                ('sh_flags', Elf64_Xword),
                ('sh_addr', Elf64_Addr),
                ('sh_offset', Elf64_Off),
                ('sh_size', Elf64_Xword),
                ('sh_link', Elf64_Word),
                ('sh_info', Elf64_Word),
                ('sh_addralign', Elf64_Xword),
                ('sh_entsize', Elf64_Xword)
                ]


class Sym(BigEndianStructure):
    _fields_ = [('st_name', Elf64_Word),
                ('st_info', uchar),
                ('st_other', uchar),
                ('st_shndx', Elf64_Half),
                ('st_value', Elf64_Addr),
                ('st_size', Elf64_Xword)
                ]


class Rel(BigEndianStructure):
    _fields_ = [('r_offset', Elf64_Addr),
                ('r_info', Elf64_Xword)]


class Rela(BigEndianStructure):
    _fields_ = [('r_offset', Elf64_Addr),
                ('r_info', Elf64_Xword),
                ('r_addend', Elf64_Sxword)
                ]


class Phdr(BigEndianStructure):
    _fields_ = [('p_type', Elf64_Word),
                ('p_flags', Elf64_Word),
                ('p_offset', Elf64_Off),
                ('p_vaddr', Elf64_Addr),
                ('p_paddr', Elf64_Addr),
                ('p_filesz', Elf64_Xword),
                ('p_memsz', Elf64_Xword),
                ('p_align', Elf64_Xword)
                ]