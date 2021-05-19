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
unary_ops = {"~": "not"}

binary_op_inverses = {"==": "!=", "!=": "==", "<": ">=", "<=": ">", ">": "<=", ">=": "<"}

func_binary_ops = ["pow", "max", "min", "angle", "len", "land", "idiv", "strictEqual", "noise"]
func_unary_ops = ["abs", "log", "log10", "sin", "cos", "tan", "floor", "ceil", "sqrt", "rand"]
binary_ops.update(dict(zip(func_binary_ops, func_binary_ops)))
unary_ops.update(dict(zip(func_unary_ops, func_unary_ops)))
SPECIAL_VARS = ("links", "ipt", "counter", "time", "unit")
