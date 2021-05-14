# see https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/logic/LogicOp.java
binary_ops = {
	"+": "add",
	"-": "sub",
	"*": "mul",
	"/": "div",
	"%": "mod",
	"==": "equal",
	"!=": "notEqual",
	"<": "lessThan",
	"<=": "lessThanEq",
	">": "greaterThan",
	">=": "greaterThanEq",
	">>": "shl",
	"<<": "shr",
	"|": "or",
	"&": "and",
	"^": "xor"
}

condition_ops = {
	"==": "equal",
	"!=": "notEqual",
	"<": "lessThan",
	"<=": "lessThanEq",
	">": "greaterThan",
	">=": "greaterThanEq"
}
#TODO remove negate b/c its deprecated
unary_ops = {"~": "not"}

binary_op_inverses = {"==": "!=", "!=": "==", "<": ">=", "<=": ">", ">": "<=", ">=": "<"}

func_binary_ops = ["pow", "max", "min", "angle", "len", "land", "idiv", "strictEqual", "noise"]
func_unary_ops = ["abs", "log", "log10", "sin", "cos", "tan", "floor", "ceil", "sqrt", "rand"]
binary_ops.update(dict(zip(func_binary_ops, func_binary_ops)))
unary_ops.update(dict(zip(func_unary_ops, func_unary_ops)))

draw_funcs = {
	"draw" + func.lower(): func
	for func in
	["clear", "color", "stroke", "line", "rect", "lineRect", "poly", "linePoly", "triangle"]
}

builtins = [
	"print", "printd", "printflush", "radar", "sensor", "enable", "shoot", "get_link", "read",
	"write", "drawflush", "end"
] + list(draw_funcs.keys())
