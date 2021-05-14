from dataclasses import dataclass
from .consts import binary_op_inverses, binary_ops, condition_ops, unary_ops

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

class RawAsm(Instruction):
	def __init__(self, code: str):
		self.code = code
	
	def __str__(self):
		return self.code

class ParsedInstruction(Instruction):
	pass
