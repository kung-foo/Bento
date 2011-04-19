import os
import errno

from bento.installed_package_description \
    import \
        InstalledSection
from bento.commands.errors \
    import \
        CommandExecutionFailure

def toyext_to_distext(e):
    """Convert a bento Extension instance to a distutils
    Extension."""
    # FIXME: this is temporary, will be removed once we do not depend
    # on distutils to build extensions anymore. That's why this is not
    # a method of the bento Extension class.
    from distutils.extension import Extension as DistExtension
    return DistExtension(e.name, sources=[s for s in e.sources],
                         include_dirs=[inc for inc in e.include_dirs])

def to_dist_compiled_library(library):
    name = module_to_path(library.name)
    return (os.path.basename(name), dict(sources=library.sources))

def module_to_path(module):
    return module.replace(".", os.path.sep)

class DistutilsBuilder(object):
    def __init__(self, verbosity=1):
        from distutils.dist import Distribution
        from distutils import log

        log.set_verbosity(verbosity)

        self._dist = Distribution()
        self._compilers = {}
        self._cmds = {}

    def _setup_cmd(self, cmd, t):
        from distutils.ccompiler import new_compiler
        from distutils.sysconfig import customize_compiler

        bld_cmd = cmd(self._dist)
        bld_cmd.initialize_options()
        bld_cmd.finalize_options()
        compiler = new_compiler(compiler=bld_cmd.compiler,
                                dry_run=bld_cmd.dry_run,
                                force=bld_cmd.force)
        customize_compiler(compiler)
        return bld_cmd, compiler

    def _setup_clib(self):
        from distutils.command.build_clib import build_clib
        return self._setup_cmd(build_clib, "compiled_libraries")

    def _setup_ext(self):
        from distutils.command.build_ext import build_ext
        return self._setup_cmd(build_ext, "extensions")

    def _extension_filename(self, name, cmd):
        m = module_to_path(name)
        d, b = os.path.split(m)
        return os.path.join(d, cmd.get_ext_filename(b))

    def _compiled_library_filename(self, name, compiler):
        m = module_to_path(name)
        d, b = os.path.split(m)
        return os.path.join(d, compiler.library_filename(b))

    def build_extension(self, extension):
        import distutils.errors

        dist = self._dist
        dist.ext_modules = [toyext_to_distext(extension)]

        bld_cmd, compiler = self._setup_ext()
        try:
            bld_cmd.run()

            base, filename = os.path.split(self._extension_filename(extension.name, bld_cmd))
            fullname = os.path.join(bld_cmd.build_lib, base, filename)
            return [fullname]
        except distutils.errors.DistutilsError, e:
            raise BuildError(str(e))

    def build_compiled_library(self, library):
        import distutils.errors

        dist = self._dist
        dist.libraries = [to_dist_compiled_library(library)]

        bld_cmd, compiler = self._setup_clib()
        base, filename = os.path.split(self._compiled_library_filename(library.name, compiler))
        old_build_clib = bld_cmd.build_clib
        if base:
            # workaround for a distutils issue: distutils put all C libraries
            # in the same directory, and we cannot control the output directory
            # from the name - we need to hack build_clib directory
            bld_cmd.build_clib = os.path.join(old_build_clib, base)
        try:
            try:
                # workaround for yet another bug in distutils: distutils fucks up when
                # building a static library if the target alread exists on at least mac
                # os x.
                target = os.path.join(old_build_clib, base, filename)
                try:
                    os.remove(target)
                except OSError, e:
                    if e.errno != errno.ENOENT:
                        raise
                bld_cmd.run()

                return [target]
            except distutils.errors.DistutilsError, e:
                raise BuildError(str(e))
        finally:
            bld_cmd.build_clib = old_build_clib

def build_isection(bld, name, files, category):
    # TODO: refactor to merge this with the one in build_yaku
    if len(files) < 1:
        return InstalledSection.from_source_target_directories(category, name,
            "", "", files)
    print files
    nodes = [bld.top_node.find_node(f) for f in files]

    # FIXME: do package -> location translation correctly
    pkg_dir = os.path.dirname(name.replace('.', os.path.sep))

    source_dir = nodes[0].parent.path_from(bld.top_node)
    target_dir = os.path.join('$sitedir', pkg_dir)
    return InstalledSection.from_source_target_directories(
        "extensions", name, source_dir, target_dir, [node.name for node in nodes])

