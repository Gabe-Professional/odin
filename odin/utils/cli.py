from odin.utils.projects import project_main


def setup_project_parser(parser):
    project_parser = parser.add_parser('project')
    project_parser.add_argument("-v", "--verbose", action='count', default=0,
                                help="Logging Verbosity (Default: %(default)s")
    project_parser.add_argument('--project_directory',
                                help='directory path to where you would like to start your project',
                                required=True)
    project_parser.add_argument('--sub_dirs',
                                help='sub-directories you would like to create within your project directory',
                                nargs='*')

    project_parser.set_defaults(func=project_main)