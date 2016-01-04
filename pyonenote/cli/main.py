import argparse

from pyonenote.database import notebook_db, section_db


class CommandArgPar:
    notebook = notebook_db.NotebookDB()
    section = section_db.SectionDB()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', action='store_true', help='foo help')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    # create the parser for the "a" command
    parser_a = subparsers.add_parser('notebook', help='fetch help')
    parser_a.add_argument('level', choices=["fetch", "list"], help='fetch level help', default='list', nargs='?')

    # create the parser for the "b" command
    parser_b = subparsers.add_parser('page', help='list help')
    parser_b.add_argument('level', choices=["fetch", "list", "push"], help='list level help', default='list', nargs='?')
    parser_b.add_argument('file', help='file name to push', nargs='?')
    parsed_args = parser.parse_args()
    command_choice = parsed_args.command
    function_choice = parsed_args.level
    print(command_choice + '.' + function_choice)
    command_parser = CommandArgPar()
    try:
        obj = getattr(command_parser, command_choice)
        if hasattr(parsed_args, 'file'):
            print('file location given')
            getattr(obj, function_choice)(parsed_args.file)
        else:
            getattr(obj, function_choice)()
    except:
        raise AttributeError


if __name__ == '__main__':
    main()
