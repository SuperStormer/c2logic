from dataclasses import dataclass

from .consts import binary_op_inverses, binary_ops, condition_ops, unary_ops
from .instruction_definition import FUNCS

class Instruction:
	pass

class Noop(Instruction):
	def __str__(self):
		return "noop"

class Set(Instruction):
	def __init__(self, dest: str, src: str):
		self.src = src
		self.dest = dest
	
	def __str__(self):
		return f"set {self.dest} {self.src}"

class BinaryOp(Instruction):
	def __init__(self, dest: str, left: str, right: str, op: str):
		self.left = left
		self.right = right
		self.op = op
		self.dest = dest
	
	def inverse(self):
		return BinaryOp(self.dest, self.left, self.right, binary_op_inverses[self.op])
	
	def __str__(self):
		return f"op {binary_ops[self.op]} {self.dest} {self.left} {self.right}"

class UnaryOp(Instruction):
	def __init__(self, dest: str, src: str, op: str):
		self.src = src
		self.dest = dest
		self.op = op
	
	def __str__(self):
		return f"op {unary_ops[self.op]} {self.dest} {self.src} 0"

@dataclass
class JumpCondition:
	op: str
	left: str
	right: str
	
	@classmethod
	def from_binaryop(cls, binop: BinaryOp):
		return cls(binop.op, binop.left, binop.right)
	
	always: "JumpCondition" = None
	
	def __str__(self):
		return f"{condition_ops[self.op]} {self.left} {self.right}"

JumpCondition.always = JumpCondition("==", "0", "0")

class RelativeJump(Instruction):
	def __init__(self, offset: int, cond: JumpCondition):
		self.offset = offset
		self.func_start: int = None
		self.cond = cond
	
	def __str__(self):
		return f"jump {self.func_start + self.offset} {self.cond}"

class FunctionCall(Instruction):
	def __init__(self, func_name: str):
		self.func_name = func_name
		self.func_start: int = None
	
	def __str__(self):
		return f"jump {self.func_start} {JumpCondition.always}"

class Return(Instruction):
	def __init__(self, func_name: str):
		self.func_name = func_name
	
	def __str__(self):
		return f"set @counter __retaddr_{self.func_name}"

class Goto(Instruction):
	def __init__(self, label: str):
		self.label = label
		self.offset: int = None
		self.func_start: int = None
	
	def __str__(self):
		return f"jump {self.func_start + self.offset} {JumpCondition.always}"

class End(Instruction):
	def __str__(self):
		return "end"

class RawAsm(Instruction):
	def __init__(self, code: str):
		self.code = code
	
	def __str__(self):
		return self.code

class ParsedInstruction(Instruction):
	def __str__(self):
		unescaped = self.assembly_string.replace('\\', '')
		return unescaped.format(**self.__dict__)

class ParsedInstructionFactory():
	RETURN_REGISTER = "__rax"
	
	def __init__(self, name, argn, argt, assembly_string):
		self.argn = argn
		self.argt = argt
		self.name = name
		self.assembly_string = assembly_string
	
	@property
	def returns_data(self):
		return "{dest}" in self.assembly_string
	
	def __call__(self, *args):
		ret_instruction = ParsedInstruction()
		ret_instruction.argt = self.argt
		ret_instruction.assembly_string = self.assembly_string
		if self.returns_data:
			ret_instruction.__setattr__('dest', self.RETURN_REGISTER)
			args = args[1:]
		ret_instruction.name = self.name
		for arg, argn in zip(args, self.argn):
			ret_instruction.__setattr__(argn, arg)
		return ret_instruction

PARSED_INSTRUCTIONS = {}
for func_name, func in FUNCS.items():
	argn = [arg_desc[0] for arg_desc in func['args']]
	argt = [arg_desc[1] for arg_desc in func['args']]
	assembly_string = func['asm']
	PARSED_INSTRUCTIONS[func_name] = ParsedInstructionFactory(
		func_name, argn, argt, assembly_string
	)
