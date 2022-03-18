import os
import re
import subprocess
import codecs
from pathlib import Path
import pandas as pd
from datetime import datetime
import logging, sys
import config


# Config
TARGET_WEEK = config.target_week
DEBUG = config.debug
# Grading
CORRECT = config.correct
WRONG = config.wrong
COMPILE_FAIL = config.compile_fail
NOT_PAID = config.not_paid
# Compiler
COMPILE_OUTPUT = 'compile_result'
COMPILER_COMMAND = 'gcc'
COMPILER_ARGUMENT = '-lstdc++ -lm -w'
COMPILER_ARGUMENT_BIG5 = '-finput-charset=big5'
# Executor
TRAVERSE_DIRECTORY = f"./{TARGET_WEEK}"
FILE_INPUT = config.week_args[TARGET_WEEK]['file_input']
OUTPUT_PATTERN = config.week_args[TARGET_WEEK]['output_pattern']
CSV_FOLDER = "./result"
CSV_FILENAME = f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.csv"

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr,
    level=logging.DEBUG if DEBUG else logging.INFO,
)

# def encoding_to_utf8(file_path):
#     try:
#         file = codecs.open(file_path, 'r', 'gbk').read()
#     except UnicodeDecodeError as error:
#         pass
#     else:
#         codecs.open(file_path, 'w', 'utf-8').write(file)


def check_file_ext(root, file):
    input_file = f'{root}/{file}'
    pattern = r'\.(c|cpp)$'
    regex = re.search(pattern, input_file)
    if regex is None:
        logging.debug(f'file ext not allow')
        return False
    logging.debug(f'file ext correct')
    return True


def compiler(root, file):
    input_file = f'{root}/{file}'
    output_file = f'{root}/{COMPILE_OUTPUT}'

    # encoding_to_utf8(input_file)

    logging.debug(f'start to compile file')
    command = f"{COMPILER_COMMAND} '{input_file}' -o {output_file} {COMPILER_ARGUMENT} {COMPILER_ARGUMENT_BIG5}"
    result = subprocess.run(command, shell=True, capture_output=True)
    if result.returncode == 0:
        logging.debug(f'compile success')
        return result.returncode
    logging.debug(f'compile fail, try to compile without big5')
    command = f"{COMPILER_COMMAND} '{input_file}' -o {output_file} {COMPILER_ARGUMENT}"
    result = subprocess.run(command, shell=True, capture_output=True)
    if result.returncode == 0:
        logging.debug(f'compile success')
        return result.returncode
    logging.debug(f'compile fail second time, return fail result')
    return result.returncode
    


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
    prefix_pattern = f'\.\/{TARGET_WEEK}\/'
    regex = re.search(prefix_pattern, root)
    return root[regex.span()[1]:]


def executor(root, parameters, pattern):
    info = get_directory_name(root)
    logging.debug(f'start to execute file')
    command = command_with_stdin(parameters, f'{root}/{COMPILE_OUTPUT}')
    try:
        output_text = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        logging.debug(f'execute fail, maybe complie fail.')
        return [info, COMPILE_FAIL]
    logging.debug(f'execute success, start check the answer')
    answer = check_answer(pattern, output_text)
    logging.debug(f'check the answer complete')
    return [info, answer]


if __name__ == '__main__':
    logging.info(f'start with: {TARGET_WEEK}')
    logging.debug(f'start for traverse folder')
    buffer = []
    for root, dirs, files in os.walk(TRAVERSE_DIRECTORY):
        if len(files) == 0:
            continue
        for file in files:
            logging.debug('===================================================')
            logging.debug(f'current file name: {get_directory_name(root)}/{file}')
            if check_file_ext(root, file):
                if DEBUG:
                    input("Press the Enter key to proceed...")
                res = compiler(root, file)
            else:
                continue
            if res == 1:
                logging.debug(f'compile fail, store the result')
                ans = [get_directory_name(root), COMPILE_FAIL]
            else:
                ans = executor(root, FILE_INPUT, OUTPUT_PATTERN)
            logging.debug(f'execute file success, store the result')
            logging.debug(f'ans: {ans}')
            buffer.append(ans)
    df = pd.DataFrame(buffer)
    Path(CSV_FOLDER).mkdir(parents=True, exist_ok=True)
    df.to_csv(f'{CSV_FOLDER}/{CSV_FILENAME}', encoding='utf-8')
