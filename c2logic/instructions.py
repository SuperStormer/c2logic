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

class Print(Instruction):
	def __init__(self, val: str):
		self.val = val
	
	def __str__(self):
		return f"print {self.val}"

class PrintFlush(Instruction):
	def __init__(self, message: str):
		self.message = message
	
	def __str__(self):
		return f"printflush {self.message}"

class Radar(Instruction):
	def __init__(
		self, dest: str, src: str, target1: str, target2: str, target3: str, sort: str, index: str
	):
		self.src = src
		self.dest = dest
		self.target1 = target1
		self.target2 = target2
		self.target3 = target3
		self.sort = sort
		self.index = index
	
	def __str__(self):
		return f"radar {self.target1} {self.target2} {self.target3} {self.sort} {self.src} {self.index} {self.dest}"

class Sensor(Instruction):
	def __init__(self, dest: str, src: str, prop: str):
		self.dest = dest
		self.src = src
		self.prop = prop
	
	def __str__(self):
		return f"sensor {self.dest} {self.src} @{self.prop}"

class Enable(Instruction):
	def __init__(self, obj: str, enabled: str):
		self.obj = obj
		self.enabled = enabled
	
	def __str__(self):
		return f"control enabled {self.obj} {self.enabled} 0 0 0"

class Shoot(Instruction):
	def __init__(self, obj: str, x: str, y: str, shoot: str):
		self.obj = obj
		self.x = x
		self.y = y
		self.shoot = shoot
	
	def __str__(self):
		return f"control shoot {self.obj} {self.x} {self.y} {self.shoot} 0"

class GetLink(Instruction):
	def __init__(self, dest: str, index: str):
		self.dest = dest
		self.index = index
	
	def __str__(self):
		return f"getlink {self.dest} {self.index}"

class Read(Instruction):
	def __init__(self, dest: str, src: str, index: str):
		self.dest = dest
		self.src = src
		self.index = index
	
	def __str__(self):
		return f"read {self.dest} {self.src} {self.index}"

class Write(Instruction):
	def __init__(self, dest: str, src: str, index: str):
		self.dest = dest
		self.src = src
		self.index = index
	
	def __str__(self):
		return f"write {self.src} {self.dest} {self.index}"

class Draw(Instruction):
	def __init__(self, cmd: str, *args):
		self.cmd = cmd
		self.args = args
	
	def __str__(self):
		args = list(self.args) + ['0'] * (6 - len(self.args))
		return f"draw {self.cmd} {' '.join(args)}"

class DrawFlush(Instruction):
	def __init__(self, display: str):
		self.display = display
	
	def __str__(self):
		return f"drawflush {self.display}"

class End(Instruction):
	def __str__(self):
		return "end"

class RawAsm(Instruction):
	def __init__(self, code: str):
		self.code = code
	
	def __str__(self):
		return self.code