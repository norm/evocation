from watchdog.tricks import ShellCommandTrick


class MakeTrick(ShellCommandTrick):
    def __init__(self, target=None, patterns=None):
        make_command='make -B %s' % target
        super(MakeTrick, self).__init__(
            shell_command=make_command,
            patterns=patterns,
            wait_for_process=True,
        )
