import platform
import re
import subprocess
import codecs
from pathlib import Path, PurePosixPath
import pandas as pd
from datetime import datetime
import logging
import sys
import config

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr,
    level=logging.DEBUG if config.debug else logging.INFO,
)

SHELL = Path(config.shell)

# make sure that the operation system is 'Windows' or 'Linux'.
operation_system = platform.system()

def allow_ext(file):
    pattern = r'\.(c|cpp)$'
    regex = re.search(pattern, file)
    if regex is None:
        logging.debug(f'file extension not allowed')
        return False
    logging.debug(f'file extension correct')
    return True


def encoding_to_utf8(filepath):
    """
    deprecated: only can use on windows...
    """
    try:
        file = codecs.open(filepath, 'r', 'ansi').read()
    except UnicodeDecodeError as error:
        pass
    else:
        codecs.open(filepath, 'w', 'utf-8').write(file)


def specify_shell(command):
    return [SHELL.__str__(), '-c', command]


class AssistantTool:
    def __init__(self, target_week, in_out, grade, export_path, debug) -> None:
        super().__init__()
        self.target_week = target_week
        self.stdin = in_out['stdin']
        self.output_pattern = in_out['output_pattern']
        self.CORRECT = grade['correct']
        self.WRONG = grade['wrong']
        self.COMPILE_FAIL = grade['compile_fail']
        self.NOT_PAID = grade['not_paid']
        self.export_path = export_path
        self.debug = debug

        self.traverse_dir = f"./{self.target_week}"

        self.compile_output = 'compile_output'

    def start_program(self):
        logging.info(f'start with: {self.target_week}')
        logging.debug(f'start traversing the directory')
        answers = []

        for directory in Path(self.traverse_dir).iterdir():
            for file in Path(directory).iterdir():
                logging.debug('===================================================')
                logging.debug(f'current file name: {file}')
                if not allow_ext(file.name):
                    continue
                if self.debug:
                    input("Press the Enter key to proceed...")
                return_code = self.compiler(directory, file)
                if return_code == 1:
                    row_answer = [directory.name, self.COMPILE_FAIL]
                else:
                    row_answer = self.executor(directory)
                logging.debug(f'save the result')
                logging.debug(f'row_answer: {row_answer}')
                answers.append(row_answer)
        logging.info(f'program complete')
        return answers

    def compiler(self, directory, file):
        logging.debug(f'start compiling file')

        input_filepath = PurePosixPath(file)
        output_filepath = PurePosixPath(directory.joinpath(self.compile_output))

        # self.encoding_to_utf8(input_filepath)

        compiler_command = 'gcc'
        compiler_argument = '-lstdc++ -lm -w'
        compiler_argument_big5 = '-finput-charset=big5'
        if operation_system == 'Windows':
            command = f"{compiler_command} '{input_filepath}' -o {output_filepath} {compiler_argument}"
            result = subprocess.run(specify_shell(command), shell=True, capture_output=True)
        else:  # Linux
            command = f"{compiler_command} '{input_filepath}' -o {output_filepath} {compiler_argument} {compiler_argument_big5}"
            result = subprocess.run(command, shell=True, capture_output=True, executable=SHELL.__str__())
        if result.returncode == 0:
            logging.debug(f'Compiled successfully')
            return result.returncode
        logging.debug(f'compilation failed, Try compiling with big5')
        if operation_system == 'Windows':
            command = f"{compiler_command} '{input_filepath}' -o {output_filepath} {compiler_argument} {compiler_argument_big5}"
            result = subprocess.run(specify_shell(command), shell=True, capture_output=True)
        else:  # Linux
            command = f"{compiler_command} '{input_filepath}' -o {output_filepath} {compiler_argument}"
            result = subprocess.run(command, shell=True, capture_output=True, executable=SHELL.__str__())
        if result.returncode == 0:
            logging.debug(f'Compiled successfully')
            return result.returncode
        logging.debug(f'compilation fails twice, return failure result')
        return result.returncode

    def executor(self, directory):
        logging.debug(f'start file execution')
        executable_file = PurePosixPath(directory.joinpath(self.compile_output))
        command = f"echo '{' '.join(self.stdin)}' | {executable_file}"
        try:
            if operation_system == 'Windows':
                stdout = subprocess.check_output(specify_shell(command), shell=True, text=True, stderr=subprocess.STDOUT)
            else:  # Linux
                stdout = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT, executable=SHELL.__str__())
        except subprocess.CalledProcessError as error:
            logging.debug(f'execution failed, maybe compilation failed')
            return [directory.name, self.COMPILE_FAIL]
        logging.debug(f'execution succeed')
        logging.debug(f'start checking answers')
        answer = self.check_answer(stdout)
        logging.debug(f'check the answer complete')
        logging.debug(f'execute the file complete')
        return [directory.name, answer]

    def check_answer(self, stdout):
        for or_pattern in self.output_pattern:
            flag = True
            for and_pattern in or_pattern:
                regex = re.search(and_pattern, stdout)
                if regex is None:
                    flag = False
            if flag:
                return self.CORRECT
        return self.WRONG

    def export_to_csv(self, answers):
        csv_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{self.target_week}.csv"
        df = pd.DataFrame(answers)
        directory = Path(self.export_path)
        directory.mkdir(parents=True, exist_ok=True)
        df.to_csv(directory.joinpath(csv_filename), encoding='utf-8')
