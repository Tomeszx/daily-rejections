from gooey import Gooey, GooeyParser


@Gooey(
    program_name="Daily rejection tool",
    terminal_font_color='black',
    terminal_panel_color='white',
    show_restart_button=False,
    progress_regex=r"^progress: (\d+)/(\d+)$",
    progress_expr="x[0] / x[1] * 100",
    disable_progress_bar_animation=False,
    default_size=(810, 530),
)
def handle():
    parser = GooeyParser()
    parser.add_argument("username_ps", metavar='Username_PS')
    parser.add_argument("password_ps", metavar='Password_PS', widget='PasswordField')
    parser.add_argument("username_pms", metavar='Username_PMS')
    parser.add_argument("password_pms", metavar='Password_PMS', widget='PasswordField')
    parser.add_argument("threads_num", metavar="How many workers??", type=int, default=1)

    return parser.parse_args()
