import os
import re
import subprocess
import codecs
from pathlib import Path
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


def allow_ext(file):
    pattern = r'\.(c|cpp)$'
    regex = re.search(pattern, file)
    if regex is None:
        logging.debug(f'file ext not allow')
        return False
    logging.debug(f'file ext correct')
    return True


def encoding_to_utf8(filepath):
    """
    only can use on windows...
    """
    try:
        file = codecs.open(filepath, 'r', 'ansi').read()
    except UnicodeDecodeError as error:
        pass
    else:
        codecs.open(filepath, 'w', 'utf-8').write(file)


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

    def start(self):
        logging.info(f'start with: {self.target_week}')
        logging.debug(f'start for traverse folder')
        answers = []
        for root, dirs, files in os.walk(self.traverse_dir):
            if len(files) == 0:
                continue
            for file in files:
                logging.debug('===================================================')
                logging.debug(f'current file name: {self.directory_name(root)}/{file}')
                if allow_ext(file):
                    if self.debug:
                        input("Press the Enter key to proceed...")
                    return_code = self.compiler(root, file)
                else:
                    continue
                if return_code == 1:
                    logging.debug(f'compile fail, store the result')
                    row_answer = [self.directory_name(root), self.COMPILE_FAIL]
                else:
                    row_answer = self.executor(root)
                logging.debug(f'execute file success, store the result')
                logging.debug(f'ans: {row_answer}')
                answers.append(row_answer)
        self.export_to_csv(answers)
        logging.info(f'process complete')

    def directory_name(self, root):
        prefix_pattern = f'\.\/{self.target_week}\/'
        regex = re.search(prefix_pattern, root)
        return root[regex.span()[1]:]

    def compiler(self, root, file):
        input_filepath = f'{root}/{file}'
        output_filepath = f'{root}/{self.compile_output}'

        # self.encoding_to_utf8(input_filepath)

        logging.debug(f'start to compile file')
        compiler_command = 'gcc'
        compiler_argument = '-lstdc++ -lm -w'
        compiler_argument_big5 = '-finput-charset=big5'
        command = f"{compiler_command} '{input_filepath}' -o {output_filepath} {compiler_argument} {compiler_argument_big5}"
        result = subprocess.run(command, shell=True, capture_output=True)
        if result.returncode == 0:
            logging.debug(f'compile success')
            return result.returncode
        logging.debug(f'compile fail, try to compile without big5')
        command = f"{compiler_command} '{input_filepath}' -o {output_filepath} {compiler_argument}"
        result = subprocess.run(command, shell=True, capture_output=True)
        if result.returncode == 0:
            logging.debug(f'compile success')
            return result.returncode
        logging.debug(f'compile fail second time, return fail result')
        return result.returncode

    def executor(self, root):
        logging.debug(f'start to execute file')
        command = f"echo '{' '.join(self.stdin)}' | {root}/{self.compile_output}"
        try:
            stdout = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            logging.debug(f'execute fail, maybe compile fail.')
            return [self.directory_name(root), self.COMPILE_FAIL]
        logging.debug(f'execute success, start check the answer')
        answer = self.check_answer(stdout)
        logging.debug(f'check the answer complete')
        return [self.directory_name(root), answer]

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
        csv_filename = f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.csv"
        df = pd.DataFrame(answers)
        Path(self.export_path).mkdir(parents=True, exist_ok=True)
        df.to_csv(f'{self.export_path}/{csv_filename}', encoding='utf-8')
