# coding=utf-8
#
# Copyright 2017 Sascha Schirra
#
# This file is part of Ropper.
#
# Ropper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ropper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from ropper.common.error import RopperError

class ConstraintCompiler(object):
    """
    Compile a user given constraints to z3 expressions

    constraint := assignment | pop_reg
    assignment := reg, adjust, reg | number
    pop_reg := "pop", reg
    adjust := "==" | "+=" | "-=" | "*=" | "/="
    reg := a register of the current architecture
    number := int
    """

    NUMBER_REGEX = '(-?[0-9]+)'
    REG_REGEX = '([a-zA-Z0-9]+)'
    ADJUST_REGEX = '([\\+\-\*/=]=)'
    ASSIGNMENT_REGEX = '('+REG_REGEX + ' *' + ADJUST_REGEX + ' *('+NUMBER_REGEX+'|'+REG_REGEX+'|(\[)'+REG_REGEX+'(\])))'
    POP_REGEX = '((pop) +([a-zA-Z0-9]+))'
    CONSTRAINT_REGEX = '(' + ASSIGNMENT_REGEX + '|' + POP_REGEX + ')'

    def __init__(self, architecture, semantic_info):
        self.__architecture = architecture
        self.__semantic_info = semantic_info

    def compile(self, constraints):
        """
        compile a line of semantic expressions
        """
        tokens = self._tokenize(constraints)[::-1]
        to_return = None
        constraint = None
        while True:
            if not tokens:
                break

            token = tokens.pop()
            if token in self.__architecture.info.registers:
                constraint = self._assignment(token, tokens)
            elif token == 'pop':
                constraint = self._popReg(token, tokens)
            elif token == ';':
                if to_return is None:
                    to_return = constraint
                else:
                    to_return = 'And(%s, %s)' % (to_return, constraint)
            else:
                raise ConstraintError('Invalid token: %s' % token)

        return to_return

    def _tokenize(self, constraints):
        """
        return a list of tokens
        """
        tokens = []
        for constraint in constraints.split(';'):
            constraint = constraint.strip()
            if not constraint:
                continue
            match = re.match(ConstraintCompiler.CONSTRAINT_REGEX, constraint)
            if match is None:
                raise ConstraintError('Invalid Syntax: %s' % constraint)
            last_valid_index = -1
            for index in range(1, len(match.regs)):
                start = match.regs[index][0]
                if start == -1:
                    continue
                if last_valid_index == -1:
                    last_valid_index = index
                    continue
                if match.regs[last_valid_index][0] != start:
                    tokens.append(match.group(last_valid_index))
                last_valid_index = index
            tokens.append(match.group(last_valid_index))
            tokens.append(';')
        return tokens

    def _assignment(self, register, tokens):
        register = self.__architecture.getRegisterName(register)
        reg1_last = self.__semantic_info.regs[register][-1]
        reg1_init = self.__semantic_info.regs[register][0]
        op = tokens.pop()
        if not re.match(ConstraintCompiler.ADJUST_REGEX, op):
            raise ConstraintError('Invalid syntax: %s' % op)
        value = tokens.pop()
        if value == '[':
            value = self._readMemory(tokens.pop())
            tokens.pop()
        elif re.match(ConstraintCompiler.NUMBER_REGEX, value):
            value = create_number_expression(int(value), int(reg1_last.split('_')[-1]))
        elif value in self.__architecture.info.registers:
            value = self.__architecture.getRegisterName(value)
            value = self.__semantic_info.regs[value][0]
            value = create_register_expression(value, int(value.split('_')[-1]))
        else:
            print(re.match(ConstraintCompiler.NUMBER_REGEX, value))
            raise ConstraintError('Invalid Assignment: %s%s%s' % (register, op, value))
        reg1_last = create_register_expression(reg1_last, int(reg1_last.split('_')[-1]))
        reg1_init = create_register_expression(reg1_init, int(reg1_init.split('_')[-1]))
        return self._create(reg1_last, reg1_init, value, op[0])

    def _create(self, left_last, left_init, right, adjust):
        if adjust != '=':
            return '%s == %s %s %s' % (left_last, left_init, adjust, right)
        else:
            return '%s == %s' % (left_last, right)

    def _readMemory(self, register):
        pass

    def _popReg(self, pop, tokens):
        reg = tokens.pop()
        

class ConstraintError(RopperError):
    """
    ConstraintError
    """
    pass


def create_register_expression(register_accessor, size, high=False):
    register_size = int(register_accessor.split('_')[2])
    if size < register_size:
        if high:
            return 'Extract(%d, 8, self.%s)' % (size+8-1, register_accessor)
        else:
            return 'Extract(%d, 0, self.%s)' % (size-1, register_accessor)
    else:
        return 'self.%s' % register_accessor

def create_number_expression(number, size):
    return "BitVecVal(%d, %d)" % (number, size)