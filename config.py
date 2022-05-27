import configparser

config = configparser.ConfigParser()
config.read('env.ini', encoding='utf-8')
app = config['app']

# App
target_week = app.get('TargetWeek', 'week1')
debug = app.getboolean('Debug', False)
shell = app.get('Shell', '/bin/sh')

# Grading
grade = {
    'correct': 100,
    'wrong': 90,
    'compile_fail': 80,
    'not_paid': 0,
}

# Export
csv_folder = "./result"

# Week Data
week_args = dict()
week_args['week1'] = {
    'Title': '一元二次方程式公式解',
    'Notes': '(2a) 要加括號',
    'stdin': ["4", "32", "28"],
    'output_pattern': [[r'(-1)+', r'(-7)+']],
}
week_args['week2'] = {
    'Title': '課堂完成（一元二次重根與無解）',
}
week_args['week3'] = {
    'Title': '一元二次（x, y可能是負數）',
    'stdin': ["2", "-2"],
    'output_pattern': [[r'((0\.25)+|(1\/4)+)']],
}
week_args['week4'] = {
    'Title': '課堂完成（算圓周率）',
    'stdin': [],
    'output_pattern': [[r'((3)+|(14)+)']],
}
week_args['week5'] = {
    'Title': '用函式找最大公因數',
    'stdin': ["12", "18"],
    'output_pattern': [[r'(6)']],
}
week_args['week11-1'] = {
    'Title': '找出矩陣的平均值，並設為閥值',
    'stdin': [],
    'output_pattern': [[r'(15)+|(0)+|(1)+']],
}
week_args['week11-2'] = {
    'Title': '一維矩陣的卷積範例',
    'stdin': [],
    'output_pattern': [[r'(3)+|(16)+|(23)+|(27)+|(22)+|(5)+']],
}
week_args['week12-1'] = {
    'Title': '字串複製',
    'stdin': ["asdf"],
    'output_pattern': [[r'(asdf)+']],
}
week_args['week12-2'] = {
    'Title': '字串連接',
    'stdin': ["mike", "123"],
    'output_pattern': [[r'(mike123)+']],
}
week_args['week13'] = {
    'Title': '二維矩陣的卷積範例',
    'stdin': [],
    'output_pattern': [[r'(2)+', r'(6)+', r'(-4)+', r'(5)+', r'(4)+', r'(0)+', r'(-1)+', r'(-5)+', r'(3)+', r'(-2)+']],
}
