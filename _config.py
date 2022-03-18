import configparser


config = configparser.ConfigParser()
config.read('env.ini')
app = config['app']

# App
target_week = app.get('TargetWeek', 'week1')
debug = app.getboolean('Debug', False)

# Grading
correct = 100
wrong = 90
compile_fail = 80
not_paid = 0

# Week Data
week_args = dict()
week_args['week1'] = {
    'Title': '一元二次方程式公式解',
    'Notes': '(2a) 要加括號',
    'file_input': ["4", "32", "28"],
    'output_pattern': [[r'(-1)+', r'(-7)+']],
}
week_args['week2'] = {
    'Notes': '課堂完成（一元二次重根與無解）',
}
week_args['week3'] = {
    'file_input': ["2", "-2"],
        'output_pattern': [[r'((0\.25)+|(1\/4)+)']],
}
week_args['week4'] = {
    'Notes': '課堂完成（算圓周率）',
}

# Output
csv_folder = "./result"