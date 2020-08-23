from .operations import binary_ops, condition_ops, unary_ops

class Instruction:
	pass

class Noop(Instruction):
	def __str__(self):
		return "noop"

class Set(Instruction):
	def __init__(self, dest, src):
		self.src = src
		self.dest = dest
	
	def __str__(self):
		return f"set {self.dest} {self.src}"

class BinaryOp(Instruction):
	def __init__(self, dest, left, right, op):
		self.left = left
		self.right = right
		self.op = op
		self.dest = dest
	
	def __str__(self):
		return f"bop {binary_ops[self.op]} {self.left} {self.right} {self.dest}"

class UnaryOp(Instruction):
	def __init__(self, dest, src, op):
		self.src = src
		self.dest = dest
		self.op = op
	
	def __str__(self):
		return f"uop {unary_ops[self.op]} {self.src} {self.dest}"

class JumpCondition:
	def __init__(self, op: str, left, right):
		self.op = op
		self.left = left
		self.right = right
	
	@classmethod
	def from_binaryop(cls, binop: BinaryOp):
		return JumpCondition(binop.op, binop.left, binop.right)
	
	def __str__(self):
		return f"{condition_ops[self.op]} {self.left} {self.right}"

class RelativeJump(Instruction):
	def __init__(self, offset: int, cond: JumpCondition):
		self.offset = offset
		self.func_start = None
		self.cond = cond
	
	def __str__(self):
		return f"jump {self.func_start+self.offset} {self.cond}"

class Print(Instruction):
	def __init__(self, val):
		self.val = val
	
	def __str__(self):
		return f"print {self.val}"

class PrintFlush(Instruction):
	def __init__(self, val):
		self.val = val
	
	def __str__(self):
		return f"printflush {self.val}"

class Radar(Instruction):
	def __init__(self, dest, src, target1, target2, target3, sort, index):
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
	def __init__(self, dest, src, prop):
		self.dest = dest
		self.src = src
		self.prop = prop
	
	def __str__(self):
		return f"sensor {self.dest} {self.src} @{self.prop}"

class Enable(Instruction):
	def __init__(self, obj, enabled):
		self.obj = obj
		self.enabled = enabled
	
	def __str__(self):
		return f"control enabled {self.obj} {self.enabled} 0 0 0"

class Shoot(Instruction):
	def __init__(self, obj, x, y, shoot):
		self.obj = obj
		self.x = x
		self.y = y
		self.shoot = shoot
	
	def __str__(self):
		return f"control shoot {self.obj} {self.x} {self.y} {self.shoot} 0"

class RawAsm(Instruction):
	def __init__(self, code: str):
		self.code = code
	
	def __str__(self):
		return self.code