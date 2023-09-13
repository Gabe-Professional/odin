from odin.utils.projects import project_main


def setup_project_parser(parser, parents=[]):
    project_parser = parser.add_parser('project',
                                       help='sub-command for creating new analytics projects',
                                       parents=parents)

    project_parser.add_argument('--project_directory',
                                help='directory path to where you would like to start your project',
                                required=True)
    project_parser.add_argument('--sub_dirs',
                                help='sub-directories you would like to create within your project directory',
                                nargs='*')

    project_parser.set_defaults(func=project_main)