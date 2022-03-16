import os
import re
import subprocess
import codecs
from pathlib import Path
import pandas as pd
from datetime import datetime
from config import week

target_week = 'week1'

# Grading
CORRECT = 100
WRONG = 90
COMPILE_FAIL = 80
NOT_PAID = 0
# Compiler
COMPILE_OUTPUT = 'compile_result'
COMPILER_COMMAND = 'gcc'
COMPILER_ARGUMENT = '-lstdc++ -lm -w'
COMPILER_ARGUMENT_BIG5 = '-finput-charset=big5'
# Executor
TRAVERSE_DIRECTORY = f"./{target_week}"
FILE_INPUT = week[target_week]['file_input']
OUTPUT_PATTERN = week[target_week]['output_pattern']
CSV_FOLDER = "./result"
CSV_FILENAME = f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.csv"


def encoding_to_utf8(file_path):
    try:
        file = codecs.open(file_path, 'r', 'gbk').read()
    except UnicodeDecodeError as error:
        pass
    else:
        codecs.open(file_path, 'w', 'utf-8').write(file)


def compiler(root, file):
    input_file = f'{root}/{file}'
    output_file = f'{root}/{COMPILE_OUTPUT}'

    # encoding_to_utf8(input_file)

    pattern = r'\.(c|cpp)$'
    regex = re.search(pattern, input_file)
    if regex is None:
        return None
    else:
        command = f"{COMPILER_COMMAND} '{input_file}' -o {output_file} {COMPILER_ARGUMENT} {COMPILER_ARGUMENT_BIG5}"
        result = subprocess.run(command, shell=True, capture_output=True)
        if result == 1:
            command = f"{COMPILER_COMMAND} '{input_file}' -o {output_file} {COMPILER_ARGUMENT}"
            result = subprocess.run(command, shell=True, capture_output=True)
        return result


def command_with_stdin(parameters, target):
    return f"echo '{' '.join(parameters)}' | {target}"


def check_answer(pattern, output_text):
    for or_pattern in pattern:
        flag = True
        for and_pattern in or_pattern:
            regex = re.search(and_pattern, output_text)
            if regex == None:
                flag = False
        if flag == True:
            return CORRECT
    return WRONG


def get_directory_name(root):
    prefix_pattern = f'\.\/{target_week}\/'
    regex = re.search(prefix_pattern, root)
    return root[regex.span()[1]:]


def executor(root, parameters, pattern):
    info = get_directory_name(root)
    command = command_with_stdin(parameters, f'{root}/{COMPILE_OUTPUT}')
    try:
        output_text = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return [info, COMPILE_FAIL]
    answer = check_answer(pattern, output_text)
    return [info, answer]


if __name__ == '__main__':
    buffer = []
    for root, dirs, files in os.walk(TRAVERSE_DIRECTORY):
        if len(files) == 0:
            continue
        for file in files:
            res = compiler(root, file)
            if res is None:
                continue
            elif res == 1:
                ans = [get_directory_name(root), COMPILE_FAIL]
            else:
                ans = executor(root, FILE_INPUT, OUTPUT_PATTERN)
            buffer.append(ans)
    df = pd.DataFrame(buffer)
    Path(CSV_FOLDER).mkdir(parents=True, exist_ok=True)
    df.to_csv(f'{CSV_FOLDER}/{CSV_FILENAME}', encoding='utf-8')
