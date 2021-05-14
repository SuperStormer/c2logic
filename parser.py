import re
COMMAND_RE = re.compile(r'(?P<command>\w+) (?P<subcommand>\w+) ?(?P<params>.*)')
PARAM_RE = re.compile(r'[\w@]+')

def parse_params(param_text):
	important_params = []
	params = []
	for match in PARAM_RE.finditer(param_text):
		important = True
		s = match.group(0)
		params.append(s)
		if s == '0' or "@" in s:
			important = False
		important_params.append(important)
	return params, important_params

def parse_command(command_text):
	match = COMMAND_RE.match(command_text)
	info = match.groupdict()
	if info['params'] != '':
		parsed_params, important = parse_params(info['params'])
		info['params'] = parsed_params
		info['important'] = important
	else:
		info['params'] = []
		info['important'] = []
	return info

if __name__ == "__main__":
	with open('./new.masm') as command_file:
		command_text = command_file.read()
	l = list(map(parse_command, filter(bool, command_text.split('\n'))))
