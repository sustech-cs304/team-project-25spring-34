import re

def detect_language(code_str):
    """
    检测代码是Python还是Java。
    基于关键字判断。
    """
    java_keywords = ['public class', 'import java.', 'void main', 'System.out.println']
    for keyword in java_keywords:
        if keyword in code_str:
            return 'java'

    python_keywords = ['def ', 'import sys', 'print(', 'elif ', 'except ']
    for keyword in python_keywords:
        if keyword in code_str:
            return 'python'

    # 检查大括号数量作为备用判断
    if code_str.count('{') + code_str.count('}') > 0:
        return 'java'
    return 'python'  # 默认Python

def detect_indent_unit(lines):
    """
    检测代码中最小的非零缩进空格数，作为单级缩进单位
    """
    indentations = [len(line) - len(line.lstrip(' ')) for line in lines if line.strip()]
    nonzero = [i for i in indentations if i > 0]
    if nonzero:
        return min(nonzero)
    return 4  # 如果没有缩进，默认返回 4


def balance_code(code):
    """
    对代码中未闭合的括号、方括号和花括号进行简单补全，
    直接在代码末尾追加缺失的闭合符号。
    """
    counts = {'(': 0, ')': 0, '[': 0, ']': 0, '{': 0, '}': 0}
    for char in code:
        if char in counts:
            counts[char] += 1
    # 按顺序补全：先圆括号，再方括号，再花括号
    if counts['('] > counts[')']:
        code += ')' * (counts['('] - counts[')'])
    if counts['['] > counts[']']:
        code += ']' * (counts['['] - counts[']'])
    if counts['{'] > counts['}']:
        code += '}' * (counts['{'] - counts['}'])
    return code


def fix_dictionary_key_quotes(code):
    """
    修正字典 key 中的引号问题，包括：
      1. 如果字典 key 前后引号不匹配，则统一转换为默认的单引号。
         匹配模式解释：
           ([{\s,])       匹配左大括号、逗号或空白字符（作为键前缀）
           (["'])        捕获开头的引号（单或双引号）
           ([A-Za-z_][A-Za-z0-9_]*)  匹配有效的标识符
           (["'])        捕获结尾的引号（可能与前面不同）
           (\s*:)        匹配冒号之前的可选空白字符
      2. 如果字典 key 后错误地附加了额外字母（例如：{'text's 或 'text's），
         则去除这些额外字母并加上正确的冒号分隔符。
    """

    # 修正引号不匹配问题
    def repl(match):
        prefix = match.group(1)
        quote1 = match.group(2)
        key = match.group(3)
        quote2 = match.group(4)
        suffix = match.group(5)
        if quote1 != quote2:
            fixed_quote = "'"  # 统一使用单引号
            return f"{prefix}{fixed_quote}{key}{fixed_quote}{suffix}"
        else:
            return match.group(0)

    code = re.sub(r'([{\s,])(["\'])([A-Za-z_][A-Za-z0-9_]*)(["\'])(\s*:)', repl, code)

    # 修正 key 后错误附加一串字母的情况
    code = re.sub(r"([{\s])([A-Za-z_][A-Za-z0-9_]*)'([A-Za-z]+)(\s+)", r"\1'\2':\4", code)
    code = re.sub(r"('\w+')([A-Za-z]+)(\s+)", r"\1:\3", code)
    # code = re.sub(r"([\{\s])([A-Za-z_][A-Za-z0-9_]*)'([A-Za-z]+)(\s+)", r"\1'\2':\4", code)
    # code = re.sub(r"('(?:\w+)')([A-Za-z]+)(\s+)", r"\1:\3", code)

    return code


def fix_mismatched_quotes_in_comparisons(code):
    """
    修正代码中比较语句中引号不匹配的问题，
    适用于形如：if xxx == "somevalue' 或 if xxx == 'somevalue"
    统一将引号修正为默认的单引号。

    匹配模式解释：
      (==\s*)                 匹配比较操作符及紧随的空白字符
      (["'])([^"']+?)(["'])   分别捕获开头的引号、内容和结束的引号
    """

    def repl(match):
        operator = match.group(1)
        quote1 = match.group(2)
        content = match.group(3).strip()
        quote2 = match.group(4)
        fixed_quote = "'" if quote1 == "'" or quote2 == "'" else '"'
        return f"{operator}{fixed_quote}{content}{fixed_quote}"
    return re.sub(r'(==\s*)(["\'])([^"\']+?)(["\'])', repl, code)


def fix_extra_spaces(code):
    """
    移除对象属性调用中的多余空格，
    例如将 "request .POST" 修正为 "request.POST"
    """
    return re.sub(r'(\w+)\s+\.(\w+)', r'\1.\2', code)


def format_java_indent(lines):
    """
    Java代码缩进格式化
    """
    indent_level = 0
    formatted = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted.append('')
            continue
        current_indent = ' ' * (indent_level * 4)
        formatted_line = current_indent + stripped

        open_braces = line.count('{')
        close_braces = line.count('}')
        indent_level += (open_braces - close_braces)
        indent_level = max(indent_level, 0)

        formatted.append(formatted_line)
    return formatted


def balance_java_code(code):
    """
    Java代码括号补全
    """
    counts = {'{': 0, '}': 0, '(': 0, ')': 0, '[': 0, ']': 0}
    for char in code:
        if char in counts:
            counts[char] += 1
    missing = counts['{'] - counts['}']
    if missing > 0:
        code += '}' * missing
    missing = counts['('] - counts[')']
    if missing > 0:
        code += ')' * missing
    missing = counts['['] - counts[']']
    if missing > 0:
        code += ']' * missing
    return code


def fix_java_quotes(code):
    """
    Java引号修正
    """
    code = re.sub(r"'(.*?)'", lambda m: '"%s"' % m.group(1) if len(m.group(1)) != 1 else "'%s'" % m.group(1), code)
    return code


def auto_format_code_improved(code_str):
    """
    自动补全缩进并检查符号缺失的代码格式化函数（改进版）
    功能：
      1. 替换中文引号为英文引号
      2. 自动为需要的行补全缺失的冒号
      3. 根据检测到的实际缩进单位，结合原始缩进层级（base_level）来调整缩进，
         保持部分正确缩进信息，同时统一输出为每层4个空格
      4. 后处理：修正字典中识别错误导致的缺失冒号问题
      5. 简单补全未闭合的括号
    """
    lang = detect_language(code_str)

    if lang == 'python':
        # Python处理流程
        code_str = re.sub(r'[‘’]', "'", code_str)
        code_str = re.sub(r'[“”]', '"', code_str)
        lines = code_str.splitlines()
        indent_unit = detect_indent_unit(lines)
        formatted_lines = []
        indent_level = 0
        block_keywords = ('def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with')
        dedent_trigger_keywords = ('elif', 'else', 'except', 'finally')
        dedent_line_keywords = ('return', 'break', 'continue', 'pass', 'raise')

        for line in lines:
            orig_indent = len(line) - len(line.lstrip(' '))
            base_level = orig_indent // indent_unit if indent_unit else 0
            if base_level > indent_level:
                indent_level = base_level

            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue

            if any(stripped.startswith(kw) for kw in dedent_trigger_keywords):
                indent_level = max(indent_level - 1, 0)

            words = stripped.split()
            if words and words[0] in block_keywords and not stripped.endswith(':'):
                stripped += ':'

            formatted_lines.append(' ' * (indent_level * 4) + stripped)

            if stripped.endswith(':'):
                indent_level += 1
            elif any(stripped.startswith(kw) for kw in dedent_line_keywords):
                indent_level = max(indent_level - 1, 0)

        formatted_code = "\n".join(formatted_lines)
        formatted_code = fix_extra_spaces(formatted_code)
        formatted_code = fix_mismatched_quotes_in_comparisons(formatted_code)
        formatted_code = fix_dictionary_key_quotes(formatted_code)
        code = balance_code(formatted_code)
        for char in ['·', '~', '`', '《', '》', '<', '>']:
            code = code.replace(char, '')
        return code, "p"

    else:  # Java处理流程
        # 预处理
        code_str = re.sub(r'[‘’]', "'", code_str)
        code_str = re.sub(r'[“”]', '"', code_str)

        # 修正引号
        code_str = fix_java_quotes(code_str)

        # 修正比较语句
        code_str = re.sub(r'==\s*\'', '== "', code_str)

        # 修正多余空格
        code_str = fix_extra_spaces(code_str)

        # 括号补全
        code_str = balance_java_code(code_str)

        # 处理缩进
        lines = code_str.splitlines()
        formatted_lines = format_java_indent(lines)

        # 补充分号
        formatted_code = []
        control_keywords = {'if', 'for', 'while', 'do', 'switch', 'try', 'catch', 'else'}
        for line in formatted_lines:
            line = re.sub(r'[\u4e00-\u9fff]', '', line)
            stripped = line.strip()
            if not stripped or stripped.endswith(('{', '}', ';')) \
                    or stripped.startswith(tuple(control_keywords)):
                formatted_code.append(line)
            else:
                formatted_code.append(line.rstrip() + ';')

        code = '\n'.join(formatted_code)
        code = code.replace('printin', 'println')
        for char in ['·', '~', '`', '《', '》', '<', '>']:
            code = code.replace(char, '')
        code = re.sub(r'String\s*\w*\s*\]', 'String[]', code)
        return code, "j"
