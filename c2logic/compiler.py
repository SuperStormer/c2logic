import os
import sysconfig
import dataclasses
from dataclasses import dataclass

from pycparser import c_ast, parse_file
from pycparser.c_ast import (
	Compound, Constant, DeclList, Enum, FileAST, FuncDecl, Struct, TypeDecl, Typename
)

from .consts import builtins, draw_funcs, func_binary_ops, func_unary_ops
from .instructions import (
	BinaryOp, Draw, DrawFlush, Enable, End, FunctionCall, GetLink, Goto, Instruction, JumpCondition,
	Print, PrintFlush, Radar, RawAsm, Read, RelativeJump, Return, Sensor, Set, Shoot, UnaryOp, Write
)

@dataclass
class Function():
	name: str
	params: list
	
	instructions: list = dataclasses.field(default_factory=list)
	locals: list = dataclasses.field(init=False)
	start: int = dataclasses.field(default=None, init=False)
	callees: set = dataclasses.field(init=False, default_factory=set)
	callers: set = dataclasses.field(init=False, default_factory=set)
	labels: dict = dataclasses.field(init=False, default_factory=dict)
	
	def __post_init__(self):
		self.locals = self.params[:]

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
		#TODO replace this with "blocks" attr on Function
		self.loops: list = None
		self.loop_end: int = None
		self.special_vars: dict = None
	
	def compile(self, filename: str):
		self.functions = {}
		self.curr_function = None
		self.globals = []
		self.loops = []
		self.loop_end = None
		self.special_vars = {}
		ast = parse_file(filename, use_cpp=True, cpp_args=["-I", get_include_path()])
		self.visit(ast)
		#remove uncalled functions
		if self.opt_level >= 2:
			self.functions["main"].callers.add("__start")
			self.remove_uncalled_funcs()
		init_call = FunctionCall("main")
		if self.opt_level >= 3:
			if len(self.functions) == 1:
				preamble = []
			else:
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
				elif isinstance(instruction, Goto):
					instruction.offset = function.labels[instruction.label]
					instruction.func_start = function.start
				elif isinstance(instruction, Set) and instruction.dest.startswith("__retaddr"):
					instruction.src += function.start
		out = []
		if preamble:
			out.append("\n".join(map(str, preamble)))
		out.extend(
			"\n".join(map(str, function.instructions)) for function in self.functions.values()
		)
		return "\n".join(out)
	
	def remove_uncalled_funcs(self):
		to_remove = set()
		for name, function in list(self.functions.items()):
			if name in to_remove:
				continue
			callers = set()
			if not self.is_called(function, callers):
				to_remove.add(name)
				to_remove |= callers
		for name in to_remove:
			del self.functions[name]
	
	def is_called(self, function, callers):
		if function.name in callers:  #avoid infinite loops
			return False
		for func_name in function.callers:
			if func_name == "__start":
				return True
			callers.add(function.name)
			if self.is_called(self.functions[func_name], callers):
				return True
		return False
	
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
	
	def get_special_var(self, varname):
		#avoids special variables clobbering each other
		if varname not in self.special_vars:
			self.special_vars[varname] = -1
		self.special_vars[varname] += 1
		#print(f"create {varname}_{self.special_vars[varname]}")
		return f"{varname}_{self.special_vars[varname]}"
	
	def delete_special_var(self, varname):
		name, _, num = varname.rpartition("_")
		try:
			if int(num) != self.special_vars[name]:
				#print(varname, self.special_vars[name])
				return
				#raise ValueError(f"{varname} was attempted to be deleted when self.special_vars[{name}] was {num}")
			#print(f"delete {name}_{self.special_vars[name]}")
			self.special_vars[name] -= 1
		except (ValueError, KeyError):  # not deleting a special var, this is normal
			pass
	
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
		#TODO make retaddr and local variables use get_special_var and delete_special_var
		if self.opt_level >= 3 and self.curr_function.name == "main":
			top = self.peek()
			if isinstance(top, Set) and top.dest == "__rax":
				self.pop()
			self.push(End())
		else:
			self.push(Return(self.curr_function.name))
	
	def optimize_builtin_args(self, args):
		if self.opt_level >= 1:
			for i, arg in reversed(list(enumerate(args))):
				if self.can_avoid_indirection(arg):
					args[i] = self.pop().src
					self.delete_special_var(arg)
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
		left_name = self.get_special_var(f"__{name}_arg0")
		self.visit(args[0])
		self.set_to_rax(left_name)
		self.visit(args[1])
		left = left_name
		right = "__rax"
		if self.can_avoid_indirection():
			self.delete_special_var(right)
			right = self.pop().src
		if self.can_avoid_indirection(left_name):
			self.delete_special_var(left)
			left = self.pop().src
		return left, right
	
	def get_multiple_builtin_args(self, args, name):
		argnames = []
		for i, arg in enumerate(args):
			self.visit(arg)
			argname = self.get_special_var(f"__{name}_arg{i}")
			self.set_to_rax(argname)
			argnames.append(argname)
		return self.optimize_builtin_args(argnames)
	
	#visitors
	def visit_FuncDef(self, node):  # function definitions
		func_name = node.decl.name
		if func_name in self.functions:
			self.curr_function = self.functions[func_name]
		else:
			func_decl = node.decl.type
			if func_decl.args is None or isinstance(func_decl.args.params[0], Typename):
				params = []
			else:
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
				func_decl = node.type
				if func_decl.args is None or isinstance(func_decl.args.params[0], Typename):
					params = []
				else:
					params = [param_decl.name for param_decl in func_decl.args.params]
				self.functions[node.name] = Function(node.name, params)
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
			if self.opt_level < 3:
				self.push(Set("__rax", varname))
	
	def visit_Constant(self, node):  # literals
		self.push(Set("__rax", node.value))
	
	def visit_ID(self, node):  # identifier
		varname = node.name
		if varname not in self.functions:
			varname = self.get_varname(varname)
		if varname in ("links", "ipt", "counter", "time"):
			varname = "@" + varname
		self.push(Set("__rax", varname))
	
	def visit_BinaryOp(self, node):
		self.visit(node.left)
		left = self.get_special_var("__rbx")
		self.set_to_rax(left)
		self.visit(node.right)
		right = "__rax"
		if self.can_avoid_indirection():
			right = self.pop().src
		if self.can_avoid_indirection(left):
			self.delete_special_var(left)
			left = self.pop().src
		self.push(BinaryOp("__rax", left, right, node.op))
		self.delete_special_var(left)
	
	def visit_UnaryOp(self, node):
		if node.op == "p++" or node.op == "p--":  #postincrement/decrement
			varname = self.get_varname(node.expr.name)
			if self.opt_level < 3:
				self.push(Set("__rax", varname))
			self.push(BinaryOp(varname, varname, "1", node.op[1]))
		elif node.op == "++" or node.op == "--":
			varname = self.get_varname(node.expr.name)
			self.push(BinaryOp(varname, varname, "1", node.op[0]))
			if self.opt_level < 3:
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
		if node.expr is None:
			self.push(Set("__rax","null"))
		else:	
			self.visit(node.expr)
		self.push_ret()
	
	def visit_Label(self, node):
		self.curr_function.labels[node.name] = self.curr_offset() + 1
		self.visit(node.stmt)
	
	def visit_Goto(self, node):
		self.push(Goto(node.name))
	
	def visit_FuncCall(self, node):
		name = node.name.name
		if node.args is not None:
			args = node.args.exprs
		else:
			args = []
		#TODO avoid duplication in builtin calls
		builtins_dict = {
			"print": Print,
			"printd": Print,
			"printflush": PrintFlush,
			"enable": Enable,
			"shoot": Shoot,
			"get_link": lambda index: GetLink("__rax", index),
			"read": lambda cell, index: Read("__rax", cell, index),
			"write": Write,
			"drawflush": DrawFlush
		}
		if name in builtins_dict:
			argnames = self.get_multiple_builtin_args(args, name)
			self.push(builtins_dict[name](*argnames))
			for argname in argnames:
				if argname.startswith(f"__{name}_arg"):
					self.delete_special_var(argname)
		elif name == "asm":
			arg = args[0]
			if not isinstance(arg, Constant) or arg.type != "string":
				raise TypeError("Non-string argument to asm", node)
			self.push(RawAsm(arg.value[1:-1]))
		elif name == "radar":
			argnames = []
			for i, arg in enumerate(args):
				if 1 <= i <= 4:
					if not isinstance(arg, Constant) or arg.type != "string":
						raise TypeError("Non-string argument to radar", node)
					self.push(Set("__rax", arg.value[1:-1]))
				else:
					self.visit(arg)
				argname = self.get_special_var(f"__radar_arg{i}")
				self.set_to_rax(argname)
				argnames.append(argname)
			argnames = self.optimize_builtin_args(argnames)
			self.push(Radar("__rax", *argnames))  #pylint: disable=no-value-for-parameter
			for argname in argnames:
				if argname.startswith("__radar_arg"):
					self.delete_special_var(argname)
		elif name == "sensor":
			self.visit(args[0])
			left = self.get_special_var("__sensor_arg0")
			self.set_to_rax(left)
			arg = args[1]
			if not isinstance(arg, Constant) or arg.type != "string":
				raise TypeError("Non-string argument to sensor", node)
			self.push(Set("__rax", arg.value[1:-1]))
			right = "__rax"
			if self.can_avoid_indirection():
				right = self.pop().src
			if self.can_avoid_indirection(left):
				self.delete_special_var(left)
				left = self.pop().src
			self.push(Sensor("__rax", left, right))
			if left.startswith("__sensor_arg0"):
				self.delete_special_var(left)
		elif name == "end":
			self.push(End())
		elif name in draw_funcs:
			argnames = self.get_multiple_builtin_args(args, name)
			cmd = draw_funcs[name]
			self.push(Draw(cmd, *argnames))
			for argname in argnames:
				if argname.startswith(f"__{name}_arg"):
					self.delete_special_var(argname)
		elif name in func_binary_ops:
			left, right = self.get_binary_builtin_args(args, name)
			self.push(BinaryOp("__rax", left, right, name))
			if left.startswith(f"__{name}_arg"):
				self.delete_special_var(left)
		elif name in func_unary_ops:
			self.push(UnaryOp("__rax", self.get_unary_builtin_arg(args), name))
		else:
			try:
				func = self.functions[name]
			except KeyError:
				raise ValueError(f"{name} is not a function")
			if self.opt_level >= 2:
				self.curr_function.callees.add(name)
				func.callers.add(self.curr_function.name)
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

def get_include_path():
	if os.name == "posix":
		return sysconfig.get_path("include", "posix_user")
	elif os.name == "nt":
		return sysconfig.get_path("include", "nt")
	else:
		raise ValueError(f"Unknown os {os.name}")

def main():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("file")
	parser.add_argument("-O", "--optimization-level", type=int, choices=range(4), default=1)
	parser.add_argument("-o", "--output", type=argparse.FileType('w'), default="-")
	args = parser.parse_args()
	print(Compiler(args.optimization_level).compile(args.file), file=args.output)

if __name__ == "__main__":
	main()
