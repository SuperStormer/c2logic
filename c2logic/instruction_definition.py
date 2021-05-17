from pathlib import Path
from pycparser import parse_file, c_ast

def extract_asm(body: c_ast.Compound):
	for item in body.block_items:
		if isinstance(item, c_ast.FuncCall):
			if item.name.name == 'asm':
				for expr in item.args.exprs:
					if isinstance(expr, c_ast.Constant) and expr.type == 'string':
						return expr.value

def get_decl_info(decl: c_ast.Decl):
	decl_info = decl.type
	maybe_string = False
	if isinstance(decl_info, c_ast.PtrDecl):
		maybe_string = True
		decl_info = decl_info.type
	name = decl_info.declname
	datatype = decl_info.type
	if isinstance(datatype, c_ast.Struct):
		return name, datatype.name
	elif maybe_string:
		if datatype.names[0] == 'char':
			return name, 'string'
	else:
		return name, datatype.names[0]

class InstructionReader(c_ast.NodeVisitor):
	def __init__(self):
		self.funcs = dict()
		super().__init__()
	
	def visit_FuncDef(self, node):
		func_name = node.decl.name
		record = self.funcs.setdefault(func_name, dict())
		record['asm'] = extract_asm(node.body)[1:-1]
		self.parse_func_decl(node.decl.type)
	
	def parse_func_decl(self, node: c_ast.FuncDecl):
		return_info = node.type
		func_name = return_info.declname
		record = self.funcs.setdefault(func_name, dict())
		try:
			record['args'] = tuple(get_decl_info(decl) for decl in node.args.params)
		
		except AttributeError:
			record['args'] = tuple()

instructions = parse_file(str(Path(__file__).parent / 'instruction_definition.c'), use_cpp=True)
reader = InstructionReader()
reader.visit(instructions)
FUNCS = reader.funcs
