from distutils.command.config \
    import \
        config as old_config

from bento.core.platforms \
    import \
        get_scheme
from bento.distutils.utils \
    import \
        run_cmd_in_context

class config(old_config):
    def __init__(self, *a, **kw):
        old_config.__init__(self, *a, **kw)

    def initialize_options(self):
        old_config.initialize_options(self)

    def finalize_options(self):
        old_config.finalize_options(self)

    def _get_install_scheme(self):
        pkg = self.distribution.pkg
        install = self.get_finalized_command("install")

        scheme = {}
        if hasattr(install, "install_dir"):
            scheme["sitedir"] = install.install_dir
        scheme["prefix"] = install.install_base

        return scheme

    def run(self):
        from bento.commands.configure import ConfigureCommand
        from bento.commands.context import ConfigureYakuContext

        dist = self.distribution

        scheme = self._get_install_scheme()
        argv = []
        for k, v in scheme.iteritems():
            argv.append("--%s=%s" % (k, v))

        run_cmd_in_context(ConfigureCommand, "configure", argv, ConfigureYakuContext,
                           dist.run_node, dist.top_node, dist.pkg)
