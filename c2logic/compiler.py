import site
import dataclasses
from dataclasses import dataclass

from pycparser import c_ast, parse_file
from pycparser.c_ast import (
	Compound, Constant, DeclList, Enum, FileAST, FuncDecl, Struct, TypeDecl
)

from .consts import builtins, draw_funcs, func_binary_ops, func_unary_ops
from .instructions import (
	BinaryOp, Draw, DrawFlush, Enable, End, FunctionCall, GetLink, Instruction, JumpCondition,
	Print, PrintFlush, Radar, RawAsm, Read, RelativeJump, Return, Sensor, Set, Shoot, UnaryOp, Write
)

@dataclass
class Function():
	name: str
	params: list
	
	instructions: list = dataclasses.field(default_factory=list)
	locals: list = dataclasses.field(init=False)
	start: int = dataclasses.field(init=False)
	
	def __post_init__(self):
		self.locals = self.params[:]
		self.start = None
		self.called = False

@dataclass
class Loop():
	start: int
	end_jumps: list = dataclasses.field(default_factory=list)

"""
@dataclass
class Variable():
	type: str
	name: str
"""

class Compiler(c_ast.NodeVisitor):
	def __init__(self, opt_level=0):
		self.opt_level = opt_level
		self.functions: dict = None
		self.curr_function: Function = None
		self.globals: list = None
		self.loops: list = None
		self.loop_end: int = None
	
	def compile(self, filename: str):
		self.functions = {}
		self.curr_function = None
		self.globals = []
		self.loops = []
		self.loop_end = None
		ast = parse_file(
			filename, use_cpp=True, cpp_args=["-I", site.getuserbase() + "/include/python3.8"]
		)
		self.visit(ast)
		
		init_call = FunctionCall("main")
		if self.opt_level >= 2:
			preamble = [init_call]
		else:
			preamble = [Set("__retaddr_main", "2"), init_call, End()]
		
		offset = len(preamble)
		
		#set function starts
		for function in self.functions.values():
			function.start = offset
			offset += len(function.instructions)
		
		#rewrite relative jumps and func calls
		init_call.func_start = self.functions["main"].start
		for function in self.functions.values():
			instructions = function.instructions
			for instruction in instructions:
				if isinstance(instruction, RelativeJump):
					instruction.func_start = function.start
				elif isinstance(instruction, FunctionCall):
					instruction.func_start = self.functions[instruction.func_name].start
				elif isinstance(instruction, Set) and instruction.dest.startswith("__retaddr"):
					instruction.src += function.start
		out = ["\n".join(map(str, preamble))]
		out.extend(
			"\n".join(map(str, function.instructions)) for function in self.functions.values()
		)
		return "\n".join(out)
	
	#utilities
	def push(self, instruction: Instruction):
		self.curr_function.instructions.append(instruction)
	
	def pop(self):
		return self.curr_function.instructions.pop()
	
	def peek(self):
		return self.curr_function.instructions[-1]
	
	def curr_offset(self):
		return len(self.curr_function.instructions) - 1
	
	def get_varname(self, varname):
		if varname in self.curr_function.locals:
			return f"_{varname}_{self.curr_function.name}"
		elif varname not in self.globals:
			raise NameError(f"Unknown variable {varname}")
		return varname
	
	def can_avoid_indirection(self, var="__rax"):
		top = self.peek()
		return self.opt_level >= 1 and isinstance(top, Set) and top.dest == var
	
	def set_to_rax(self, varname: str):
		top = self.peek()
		if self.opt_level >= 1 and hasattr(top, "dest") and top.dest == "__rax":
			#avoid indirection through __rax
			self.curr_function.instructions[-1].dest = varname
		else:
			self.push(Set(varname, "__rax"))
	
	def push_body_jump(self):
		""" jump over loop/if body when cond is false """
		if self.opt_level >= 1 and isinstance(self.peek(), BinaryOp):
			try:
				self.push(RelativeJump(None, JumpCondition.from_binaryop(self.pop().inverse())))
			except KeyError:
				self.push(RelativeJump(None, JumpCondition("==", "__rax", "0")))
		else:
			self.push(RelativeJump(None, JumpCondition("==", "__rax", "0")))
	
	def start_loop(self, cond):
		self.loops.append(Loop(self.curr_offset() + 1))
		self.visit(cond)
		self.push_body_jump()
		self.loops[-1].end_jumps = [self.curr_offset()]  # also used for breaks
	
	def end_loop(self):
		loop = self.loops.pop()
		self.push(RelativeJump(loop.start, JumpCondition.always))
		self.loop_end = self.curr_offset() + 1
		for offset in loop.end_jumps:
			self.curr_function.instructions[offset].offset = self.loop_end
	
	def push_ret(self):
		if self.opt_level >= 2 and self.curr_function.name == "main":
			top = self.peek()
			if isinstance(top, Set) and top.dest == "__rax":
				self.pop()
			self.push(End())
		else:
			self.push(Return(self.curr_function.name))
	
	def optimize_psuedofunc_args(self, args):
		if self.opt_level >= 1:
			for i, arg in reversed(list(enumerate(args))):
				if self.can_avoid_indirection(arg):
					args[i] = self.pop().src
				else:
					break
		return args
	
	def get_unary_builtin_arg(self, args):
		self.visit(args[0])
		if self.can_avoid_indirection():
			return self.pop().src
		else:
			return "__rax"
	
	def get_binary_builtin_args(self, args, name):
		left_name = f"__{name}_arg0"
		self.visit(args[0])
		self.set_to_rax(left_name)
		self.visit(args[1])
		left = left_name
		right = "__rax"
		if self.can_avoid_indirection():
			right = self.pop().src
		if self.can_avoid_indirection(left_name):
			left = self.pop().src
		return left, right
	
	def get_multiple_psuedofunc_args(self, args):
		argnames = []
		for i, arg in enumerate(args):
			self.visit(arg)
			self.set_to_rax(f"__write_arg{i}")
			argnames.append(f"__write_arg{i}")
		return self.optimize_psuedofunc_args(argnames)
	
	#visitors
	def visit_FuncDef(self, node):  # function definitions
		func_name = node.decl.name
		func_decl = node.decl.type
		params = [param_decl.name for param_decl in func_decl.args.params]
		
		self.curr_function = Function(func_name, params)
		self.visit(node.body)
		#implicit return
		#needed if loop/if body is at end of function or hasn't returned yet
		if self.loop_end == self.curr_offset() + 1 or not isinstance(self.peek(), Return):
			self.push(Set("__rax", "null"))
			self.push_ret()
		self.functions[func_name] = self.curr_function
	
	def visit_Decl(self, node):
		if isinstance(node.type, TypeDecl):  # variable declaration
			#TODO fix local/global split
			varname = node.name
			if self.curr_function is None:  # globals
				self.globals.append(varname)
			else:
				self.curr_function.locals.append(varname)
				varname = f"_{varname}_{self.curr_function.name}"
			if node.init is not None:
				self.visit(node.init)
				self.set_to_rax(varname)
		elif isinstance(node.type, FuncDecl):
			if node.name not in builtins + func_unary_ops + func_binary_ops:
				#create placeholder function for forward declarations
				self.functions[node.name] = Function(
					node.name, [param_decl.name for param_decl in node.type.args.params]
				)
		elif isinstance(node.type, Struct):
			if node.type.name != "MindustryObject":
				#TODO structs
				raise NotImplementedError(node)
		elif isinstance(node.type, Enum):
			#TODO enums
			raise NotImplementedError(node)
		else:
			raise NotImplementedError(node)
	
	def visit_Assignment(self, node):
		self.visit(node.rvalue)
		varname = self.get_varname(node.lvalue.name)
		if node.op == "=":  #normal assignment
			self.set_to_rax(varname)
		else:  #augmented assignment(+=,-=,etc)
			if self.can_avoid_indirection():
				#avoid indirection through __rax
				self.push(BinaryOp(varname, varname, self.pop().src, node.op[:-1]))
			else:
				self.push(BinaryOp(varname, varname, "__rax", node.op[:-1]))
			if self.opt_level < 2:
				self.push(Set("__rax", varname))
	
	def visit_Constant(self, node):  # literals
		self.push(Set("__rax", node.value))
	
	def visit_ID(self, node):  # identifier
		varname = node.name
		if varname not in self.functions:
			varname = self.get_varname(varname)
		self.push(Set("__rax", varname))
	
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
			varname = self.get_varname(node.expr.name)
			if self.opt_level < 2:
				self.push(Set("__rax", varname))
			self.push(BinaryOp(varname, varname, "1", node.op[1]))
		elif node.op == "++" or node.op == "--":
			varname = self.get_varname(node.expr.name)
			self.push(BinaryOp(varname, varname, "1", node.op[0]))
			if self.opt_level < 2:
				self.push(Set("__rax", varname))
		elif node.op == "!":
			self.visit(node.expr)
			if self.opt_level >= 1 and isinstance(self.peek(), BinaryOp):
				try:
					self.push(self.pop().inverse())
				except KeyError:
					self.push(BinaryOp("__rax", "__rax", "0", "=="))
			else:
				self.push(BinaryOp("__rax", "__rax", "0", "=="))
		else:
			self.visit(node.expr)
			self.push(UnaryOp("__rax", "__rax", node.op))
	
	def visit_For(self, node):
		self.visit(node.init)
		self.start_loop(node.cond)
		self.visit(node.stmt)  # loop body
		self.visit(node.next)
		self.end_loop()
	
	def visit_While(self, node):
		self.start_loop(node.cond)
		self.visit(node.stmt)
		self.end_loop()
	
	def visit_DoWhile(self, node):
		#jump over the condition on the first iterattion
		self.push(RelativeJump(None, JumpCondition.always))
		init_jump_offset = self.curr_offset()
		self.start_loop(node.cond)
		self.curr_function.instructions[init_jump_offset].offset = len(
			self.curr_function.instructions
		)
		self.visit(node.stmt)
		self.end_loop()
	
	def visit_If(self, node):
		self.visit(node.cond)
		self.push_body_jump()
		cond_jump_offset = self.curr_offset()
		self.visit(node.iftrue)
		#jump over else body from end of if body
		if node.iffalse is not None:
			self.push(RelativeJump(None, JumpCondition.always))
			cond_jump_offset2 = self.curr_offset()
		self.curr_function.instructions[cond_jump_offset].offset = len(
			self.curr_function.instructions
		)
		if node.iffalse is not None:
			self.visit(node.iffalse)
			self.curr_function.instructions[cond_jump_offset2].offset = len(
				self.curr_function.instructions
			)
	
	def visit_Break(self, node):  #pylint: disable=unused-argument
		self.push(RelativeJump(None, JumpCondition.always))
		self.loops[-1].end_jumps.append(self.curr_offset())
	
	def visit_Continue(self, node):  #pylint: disable=unused-argument
		self.push(RelativeJump(self.loops[-1].start, JumpCondition.always))
	
	def visit_Return(self, node):
		self.visit(node.expr)
		self.push_ret()
	
	def visit_FuncCall(self, node):
		name = node.name.name
		if node.args is not None:
			args = node.args.exprs
		else:
			args = []
		#TODO avoid duplication in builtin calls
		if name == "asm":
			arg = args[0]
			if not isinstance(arg, Constant) or arg.type != "string":
				raise TypeError("Non-string argument to asm", node)
			self.push(RawAsm(arg.value[1:-1]))
		elif name in ("print", "printd"):
			self.push(Print(self.get_unary_builtin_arg(args)))
		elif name == "printflush":
			self.push(PrintFlush(self.get_unary_builtin_arg(args)))
		elif name == "radar":
			argnames = []
			for i, arg in enumerate(args):
				if 1 <= i <= 4:
					if not isinstance(arg, Constant) or arg.type != "string":
						raise TypeError("Non-string argument to radar", node)
					self.push(Set("__rax", arg.value[1:-1]))
				else:
					self.visit(arg)
				self.set_to_rax(f"__radar_arg{i}")
				argnames.append(f"__radar_arg{i}")
			argnames = self.optimize_psuedofunc_args(argnames)
			self.push(Radar("__rax", *argnames))  #pylint: disable=no-value-for-parameter
		elif name == "sensor":
			self.visit(args[0])
			self.set_to_rax("__sensor_arg0")
			arg = args[1]
			if not isinstance(arg, Constant) or arg.type != "string":
				raise TypeError("Non-string argument to sensor", node)
			self.push(Set("__rax", arg.value[1:-1]))
			left = "__sensor_arg0"
			right = "__rax"
			if self.can_avoid_indirection():
				right = self.pop().src
			if self.can_avoid_indirection("__sensor_arg0"):
				left = self.pop().src
			self.push(Sensor("__rax", left, right))
		elif name == "enable":
			left, right = self.get_binary_builtin_args(args, "enable")
			self.push(Enable(left, right))
		elif name == "shoot":
			self.push(Shoot(*self.get_multiple_psuedofunc_args(args)))  #pylint: disable=no-value-for-parameter
		elif name == "get_link":
			self.visit(args[0])
			if self.can_avoid_indirection():
				self.push(GetLink("__rax", self.pop().src))
			else:
				self.push(GetLink("__rax", "__rax"))
		elif name == "read":
			cell, index = self.get_binary_builtin_args(args, "read")
			self.push(Read("__rax", cell, index))
		elif name == "write":
			self.push(Write(*self.get_multiple_psuedofunc_args(args)))  #pylint: disable=no-value-for-parameter
		elif name == "end":
			self.push(End())
		elif name in draw_funcs:
			argnames = self.get_multiple_psuedofunc_args(args)
			cmd = draw_funcs[name]
			self.push(Draw(cmd, *argnames))
		elif name == "drawflush":
			self.push(DrawFlush(self.get_unary_builtin_arg(args)))
		elif name in func_binary_ops:
			left, right = self.get_binary_builtin_args(args, "binary")
			self.push(BinaryOp("__rax", left, right, name))
		elif name in func_unary_ops:
			self.visit(args[0])
			if self.can_avoid_indirection():
				self.push(UnaryOp("__rax", self.pop().src, name))
			else:
				self.push(UnaryOp("__rax", "__rax", name))
		else:
			try:
				func = self.functions[name]
			except KeyError:
				raise ValueError(f"{name} is not a function")
			for param, arg in zip(func.params, args):
				self.visit(arg)
				self.set_to_rax(f"_{param}_{name}")
			self.push(Set("__retaddr_" + name, self.curr_offset() + 3))
			self.push(FunctionCall(name))
	
	def generic_visit(self, node):
		if isinstance(node, (FileAST, Compound, DeclList)):
			super().generic_visit(node)
		else:
			raise NotImplementedError(node)

def main():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("file")
	parser.add_argument("-O", "--optimization-level", type=int, choices=range(3), default=1)
	parser.add_argument("-o", "--output", type=argparse.FileType('w'), default="-")
	args = parser.parse_args()
	print(Compiler(args.optimization_level).compile(args.file), file=args.output)

if __name__ == "__main__":
	main()
