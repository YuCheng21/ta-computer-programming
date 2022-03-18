import config
import assistant_tool


if __name__ == '__main__':
    arguments = {
        'target_week': config.target_week,
        'in_out': config.week_args[config.target_week],
        'grade': config.grade,
        'export_path': config.csv_folder,
        'debug': config.debug,
    }
    tool = assistant_tool.AssistantTool(**arguments)
    answers = tool.start_program()
    tool.export_to_csv(answers)
