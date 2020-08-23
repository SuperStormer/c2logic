from pycparser.c_ast import Compound, Constant, DeclList, Enum, FileAST, FuncDecl, Struct, TypeDecl
from .instructions import BinaryOp, Enable, JumpCondition, Print, PrintFlush, Radar, RawAsm, RelativeJump, Sensor, Shoot, UnaryOp, Instruction, Set, Noop
from pycparser import c_parser, c_ast, parse_file
from dataclasses import dataclass
"""
@dataclass
class LoopState():
	start: int
	end: int
	cond_jump_offset: int
"""

@dataclass
class Function():
	name: str
	args: list
	instructions: list
	start: int

"""
@dataclass
class Variable():
	type: str
	name: str
"""

class Compiler(c_ast.NodeVisitor):
	"""special variables:
	__rax: similar to x86 rax
	__rbx: stores left hand side of binary ops to avoid clobbering by the right side
	__retaddr: stores return address of func call
	optimization levels:
	1: assignments set directly to the variable instead of indirectly through __rax
	"""
	def __init__(self, opt_level=0):
		self.opt_level = opt_level
	
	def compile(self, filename: str):
		self.functions = []
		self.curr_function = None
		self.loop_start = None
		self.cond_jump_offset = None
		ast = parse_file(filename, use_cpp=True, cpp_args=["-I", "include/"])
		self.visit(ast)
		#TODO actually handle functions properly
		out = []
		offset = 0
		for function in self.functions:
			function.start = offset
			offset += len(function.instructions)
		for function in self.functions:
			instructions = function.instructions
			out2 = []
			for instruction in instructions:
				if isinstance(instruction, RelativeJump):
					instruction.func_start = function.start
				out2.append(str(instruction))
			out.append("\n".join(out2))
		return "\n\n".join(out)
	
	#utilities
	def push(self, instruction: Instruction):
		self.curr_function.instructions.append(instruction)
	
	def pop(self):
		return self.curr_function.instructions.pop()
	
	def peek(self):
		return self.curr_function.instructions[-1]
	
	def can_avoid_indirection(self, var="__rax"):
		top = self.peek()
		return self.opt_level >= 1 and isinstance(top, Set) and top.dest == var
	
	def set_to_rax(self, varname: str):
		top = self.peek()
		if self.opt_level >= 1 and hasattr(top, "dest") and top.dest == "__rax":
			#avoid indirection through __rax
			self.curr_function.instructions[-1].dest = varname
			
			#self.push(Set(varname, self.pop().src))
		else:
			self.push(Set(varname, "__rax"))
	
	#visitors
	def visit_FuncDef(self, node):  # function definitions
		func_decl = node.decl.type
		args = [arg_decl.name for arg_decl in func_decl.args.params]
		
		self.curr_function = Function(node.decl.name, args, [], None)
		self.visit(node.body)
		#in case for loop is the last thing in a function to ensure the jump target is valid
		#TODO avoid this when for loop isn't last thing
		self.push(Noop())
		self.functions.append(self.curr_function)
	
	def visit_Decl(self, node):
		if isinstance(node.type, TypeDecl):  # variable declaration
			if node.init is not None:
				self.visit(node.init)
				self.set_to_rax(node.name)
		elif isinstance(node.type, FuncDecl):
			#TODO actually process func declarations
			pass
		elif isinstance(node.type, Struct):
			if node.type.name != "MindustryObject":
				#TODO structs
				raise NotImplementedError(node)
		elif isinstance(node.type, Enum):
			if node.type.name != "RadarTarget":
				#TODO enums
				raise NotImplementedError(node)
		else:
			raise NotImplementedError(node)
	
	def visit_Assignment(self, node):
		self.visit(node.rvalue)
		varname = node.lvalue.name
		if node.op == "=":  #normal assignment
			self.set_to_rax(varname)
		else:  #augmented assignment(+=,-=,etc)
			if self.can_avoid_indirection():
				#avoid indirection through __rax
				self.push(BinaryOp(varname, varname, self.pop().src, node.op[0]))
			else:
				self.push(BinaryOp(varname, varname, "__rax", node.op[0]))
	
	def visit_Constant(self, node):  # literals
		self.push(Set("__rax", node.value))
	
	def visit_ID(self, node):  # identifier
		self.push(Set("__rax", node.name))
	
	def visit_BinaryOp(self, node):
		self.visit(node.left)
		self.set_to_rax("__rbx")
		self.visit(node.right)
		left = "__rbx"
		right = "__rax"
		if self.can_avoid_indirection():
			right = self.pop().src
		if self.can_avoid_indirection("__rbx"):
			left = self.pop().src
		self.push(BinaryOp("__rax", left, right, node.op))
	
	def visit_UnaryOp(self, node):
		if node.op == "p++" or node.op == "p--":  #postincrement/decrement
			varname = node.expr.name
			self.push(Set("__rax", varname))
			self.push(BinaryOp(varname, varname, "1", node.op[1]))
		else:
			self.visit(node.expr)
			self.push(UnaryOp("__rax", "__rax", node.op))
	
	def visit_For(self, node):
		self.visit(node.init)
		self.loop_start = len(self.curr_function.instructions)
		self.visit(node.cond)
		# jump over loop body when cond is false
		if isinstance(self.peek(), BinaryOp):
			self.push(RelativeJump(None, JumpCondition.from_binaryop(self.pop())))
		else:
			self.push(RelativeJump(None, JumpCondition("==", "__rax", "0")))
		self.cond_jump_offset = len(self.curr_function.instructions) - 1
		self.visit(node.stmt)
		self.visit(node.next)
		#jump to start of loop
		self.push(RelativeJump(self.loop_start, JumpCondition("==", "0", "0")))
		self.curr_function.instructions[self.cond_jump_offset].offset = len(
			self.curr_function.instructions
		)
	
	def visit_While(self, node):
		self.loop_start = len(self.curr_function.instructions)
		self.visit(node.cond)
		# jump over loop body when cond is false
		if isinstance(self.peek(), BinaryOp):
			self.push(RelativeJump(None, JumpCondition.from_binaryop(self.pop())))
		else:
			self.push(RelativeJump(None, JumpCondition("==", "__rax", "0")))
		self.loop_end_jumps = [len(self.curr_function.instructions) - 1]  # also used for breaks
		self.visit(node.stmt)
		#jump to start of loop
		self.push(RelativeJump(self.loop_start, JumpCondition("==", "0", "0")))
		for offset in self.loop_end_jumps:
			self.curr_function.instructions[offset].offset = len(self.curr_function.instructions)
	
	def visit_If(self, node):
		self.visit(node.cond)
		# jump over if body when cond is false
		#TODO optimize for when cond is a binary operation
		if isinstance(self.peek(), BinaryOp):
			self.push(RelativeJump(None, JumpCondition("!=", "__rax", "0")))
		else:
			self.push(RelativeJump(None, JumpCondition("!=", "__rax", "0")))
		cond_jump_offset = len(self.curr_function.instructions) - 1
		self.visit(node.iftrue)
		#jump over else body from end of if body
		if node.iffalse is not None:
			self.push(RelativeJump(None, JumpCondition("==", "0", "0")))
			cond_jump_offset2 = len(self.curr_function.instructions) - 1
		self.curr_function.instructions[cond_jump_offset].offset = len(
			self.curr_function.instructions
		)
		if node.iffalse is not None:
			self.visit(node.iffalse)
			self.curr_function.instructions[cond_jump_offset2].offset = len(
				self.curr_function.instructions
			)
	
	def visit_Break(self, node):
		self.push(RelativeJump(None, JumpCondition("==", "0", "0")))
		self.loop_end_jumps.append(len(self.curr_function.instructions) - 1)
	
	def visit_FuncCall(self, node):
		name = node.name.name
		if name == "_asm":
			arg = node.args.exprs[0]
			if not isinstance(arg, Constant) or arg.type != "string":
				raise TypeError("Non-string argument to _asm", node)
			self.push(RawAsm(arg.value[1:-1]))
		elif name in ("print", "printd"):
			self.visit(node.args.exprs[0])
			if self.can_avoid_indirection():
				self.push(Print(self.pop().src))
			else:
				self.push(Print("__rax"))
		elif name == "printflush":
			self.visit(node.args.exprs[0])
			if self.can_avoid_indirection():
				self.push(PrintFlush(self.pop().src))
			else:
				self.push(PrintFlush("__rax"))
		elif name == "radar":
			args = []
			for i, arg in enumerate(node.args.exprs):
				if 1 <= i <= 4:
					if not isinstance(arg, Constant) or arg.type != "string":
						raise TypeError("Non-string argument to radar", node)
					self.push(Set("__rax", arg.value[1:-1]))
				else:
					self.visit(arg)
				self.set_to_rax(f"__radar_arg{i}")
				args.append(f"__radar_arg{i}")
			
			for i, arg in reversed(list(enumerate(args))):
				if self.can_avoid_indirection(arg):
					args[i] = self.pop().src
				else:
					break
			self.push(Radar("__rax", *args))  #pylint: disable=no-value-for-parameter
		elif name == "sensor":
			self.visit(node.args.exprs[0])
			self.set_to_rax("__sensor_arg0")
			arg = node.args.exprs[1]
			if not isinstance(arg, Constant) or arg.type != "string":
				raise TypeError("Non-string argument to sensor", node)
			self.push(Set("__rax", arg.value[1:-1]))
			src = "__sensor_arg0"
			prop = "__rax"
			if self.can_avoid_indirection():
				prop = self.pop().src
			if self.can_avoid_indirection("__sensor_arg0"):
				src = self.pop().src
			self.push(Sensor("__rax", src, prop))
		elif name == "enable":
			self.visit(node.args.exprs[0])
			self.set_to_rax("__enable_arg0")
			self.visit(node.args.exprs[1])
			src = "__enable_arg0"
			prop = "__rax"
			if self.can_avoid_indirection():
				prop = self.pop().src
			if self.can_avoid_indirection("__enable_arg0"):
				src = self.pop().src
			self.push(Enable(src, prop))
		elif name == "shoot":
			args = []
			for i, arg in enumerate(node.args.exprs):
				self.visit(arg)
				self.set_to_rax(f"__shoot_arg{i}")
				args.append(f"__shoot_arg{i}")
			
			for i, arg in reversed(list(enumerate(args))):
				if self.can_avoid_indirection(arg):
					args[i] = self.pop().src
				else:
					break
			self.push(Shoot(*args))  #pylint: disable=no-value-for-parameter
		
		else:
			raise NotImplementedError(node)
	
	def generic_visit(self, node):
		if isinstance(node, (FileAST, Compound, DeclList)):
			super().generic_visit(node)
		else:
			raise NotImplementedError(node)

def main():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("file")
	parser.add_argument("-O", "--optimization-level", type=int, default=1)
	args = parser.parse_args()
	print(Compiler(args.optimization_level).compile(args.file))

if __name__ == "__main__":
	main()