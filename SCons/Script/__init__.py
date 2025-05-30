# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""The main() function used by the scons script.

Architecturally, this *is* the scons script, and will likely only be
called from the external "scons" wrapper.  Consequently, anything here
should not be, or be considered, part of the build engine.  If it's
something that we expect other software to want to use, it should go in
some other module.  If it's specific to the "scons" script invocation,
it goes here.
"""
from __future__ import annotations

import collections
import itertools
import os
import sys
import time
from io import StringIO

start_time = time.time()

# Special chicken-and-egg handling of the "--debug=memoizer" flag:
#
# SCons.Memoize contains a metaclass implementation that affects how
# the other classes are instantiated.  The Memoizer may add shim methods
# to classes that have methods that cache computed values in order to
# count and report the hits and misses.
#
# If we wait to enable the Memoization until after we've parsed the
# command line options normally, it will be too late, because the Memoizer
# will have already analyzed the classes that it's Memoizing and decided
# to not add the shims.  So we use a special-case, up-front check for
# the "--debug=memoizer" flag and enable Memoizer before we import any
# of the other modules that use it.
# Update: this breaks if the option isn't exactly "--debug=memoizer",
# like if there is more than one debug option as a csv. Do a bit more work.

_args = sys.argv + os.environ.get("SCONSFLAGS", "").split()
_args = (
    arg[len("--debug=") :].split(",")
    for arg in _args
    if arg.startswith("--debug=")
)
_args = list(itertools.chain.from_iterable(_args))
if "memoizer" in _args:
    import SCons.Memoize
    import SCons.Warnings
    try:
        SCons.Memoize.EnableMemoization()
    except SCons.Warnings.SConsWarning:
        # Some warning was thrown.  Arrange for it to be displayed
        # or not after warnings are configured.
        from . import Main
        exc_type, exc_value, tb = sys.exc_info()
        Main.delayed_warnings.append((exc_type, exc_value))
del _args

import SCons.Action
import SCons.Builder
import SCons.Environment
import SCons.Node.FS
import SCons.Platform
import SCons.Platform.virtualenv
import SCons.Scanner
import SCons.SConf
import SCons.Subst
import SCons.Tool
import SCons.Util
import SCons.Variables
import SCons.Defaults

from . import Main

main                    = Main.main

# The following are global class definitions and variables that used to
# live directly in this module back before 0.96.90, when it contained
# a lot of code.  Some SConscript files in widely-distributed packages
# (Blender is the specific example) actually reached into SCons.Script
# directly to use some of these.  Rather than break those SConscript
# files, we're going to propagate these names into the SCons.Script
# namespace here.
#
# Some of these are commented out because it's *really* unlikely anyone
# used them, but we're going to leave the comment here to try to make
# it obvious what to do if the situation arises.
BuildTask               = Main.BuildTask
CleanTask               = Main.CleanTask
QuestionTask            = Main.QuestionTask
#SConscriptSettableOptions = Main.SConscriptSettableOptions

AddOption               = Main.AddOption
PrintHelp               = Main.PrintHelp
GetOption               = Main.GetOption
SetOption               = Main.SetOption
ValidateOptions         = Main.ValidateOptions
Progress                = Main.Progress
GetBuildFailures        = Main.GetBuildFailures
DebugOptions            = Main.DebugOptions

#keep_going_on_error     = Main.keep_going_on_error
#print_dtree             = Main.print_dtree
#print_explanations      = Main.print_explanations
#print_includes          = Main.print_includes
#print_objects           = Main.print_objects
#print_time              = Main.print_time
#print_tree              = Main.print_tree
#memory_stats            = Main.memory_stats
#ignore_errors           = Main.ignore_errors
#sconscript_time         = Main.sconscript_time
#command_time            = Main.command_time
#exit_status             = Main.exit_status
#profiling               = Main.profiling
#repositories            = Main.repositories

from . import SConscript as _SConscript  # pylint: disable=import-outside-toplevel

call_stack              = _SConscript.call_stack

#
Action                  = SCons.Action.Action
AddMethod               = SCons.Util.AddMethod
AllowSubstExceptions    = SCons.Subst.SetAllowableExceptions
Builder                 = SCons.Builder.Builder
Configure               = _SConscript.Configure
Environment             = SCons.Environment.Environment
#OptParser               = SCons.SConsOptions.OptParser
FindPathDirs            = SCons.Scanner.FindPathDirs
Platform                = SCons.Platform.Platform
Virtualenv              = SCons.Platform.virtualenv.Virtualenv
Return                  = _SConscript.Return
Scanner                 = SCons.Scanner.ScannerBase
Tool                    = SCons.Tool.Tool
WhereIs                 = SCons.Util.WhereIs

#
BoolVariable            = SCons.Variables.BoolVariable
EnumVariable            = SCons.Variables.EnumVariable
ListVariable            = SCons.Variables.ListVariable
PackageVariable         = SCons.Variables.PackageVariable
PathVariable            = SCons.Variables.PathVariable


# Action factories.
Chmod                   = SCons.Defaults.Chmod
Copy                    = SCons.Defaults.Copy
Delete                  = SCons.Defaults.Delete
Mkdir                   = SCons.Defaults.Mkdir
Move                    = SCons.Defaults.Move
Touch                   = SCons.Defaults.Touch

# Pre-made, public scanners.
CScanner                = SCons.Tool.CScanner
DScanner                = SCons.Tool.DScanner
DirScanner              = SCons.Defaults.DirScanner
ProgramScanner          = SCons.Tool.ProgramScanner
SourceFileScanner       = SCons.Tool.SourceFileScanner

# Functions we might still convert to Environment methods.
CScan                   = SCons.Defaults.CScan
DefaultEnvironment      = SCons.Defaults.DefaultEnvironment

# Other variables we provide.
class TargetList(collections.UserList):
    def _do_nothing(self, *args, **kw) -> None:
        pass
    def _add_Default(self, list) -> None:
        self.extend(list)
    def _clear(self) -> None:
        del self[:]

ARGUMENTS               = {}
ARGLIST                 = []
BUILD_TARGETS           = TargetList()
COMMAND_LINE_TARGETS    = []
DEFAULT_TARGETS         = []

# BUILD_TARGETS can be modified in the SConscript files.  If so, we
# want to treat the modified BUILD_TARGETS list as if they specified
# targets on the command line.  To do that, though, we need to know if
# BUILD_TARGETS was modified through "official" APIs or by hand.  We do
# this by updating two lists in parallel, the documented BUILD_TARGETS
# list, above, and this internal _build_plus_default targets list which
# should only have "official" API changes.  Then Script/Main.py can
# compare these two afterwards to figure out if the user added their
# own targets to BUILD_TARGETS.
_build_plus_default = TargetList()

def _Add_Arguments(alist: list[str]) -> None:
    """Add value(s) to ``ARGLIST`` and ``ARGUMENTS``."""
    for arg in alist:
        a, b = arg.split('=', 1)
        ARGUMENTS[a] = b
        ARGLIST.append((a, b))

def _Add_Targets(tlist: list[str]) -> None:
    """Add value(s) to ``COMMAND_LINE_TARGETS`` and ``BUILD_TARGETS``."""
    if tlist:
        COMMAND_LINE_TARGETS.extend(tlist)
        BUILD_TARGETS.extend(tlist)
        BUILD_TARGETS._add_Default = BUILD_TARGETS._do_nothing
        BUILD_TARGETS._clear = BUILD_TARGETS._do_nothing
        _build_plus_default.extend(tlist)
        _build_plus_default._add_Default = _build_plus_default._do_nothing
        _build_plus_default._clear = _build_plus_default._do_nothing

def _Remove_Argument(aarg: str) -> None:
    """Remove *aarg* from ``ARGLIST`` and ``ARGUMENTS``.

    Used to remove a variables-style argument that is no longer valid.
    This can happpen because the command line is processed once early,
    before we see any :func:`SCons.Script.Main.AddOption` calls, so we
    could not recognize it belongs to an option and is not a standalone
    variable=value argument.

    .. versionadded:: NEXT_RELEASE

    """
    if aarg:
        a, b = aarg.split('=', 1)
        if (a, b) in ARGLIST:
            ARGLIST.remove((a, b))
            ARGUMENTS.pop(a, None)
            # ARGLIST might have had multiple values for 'a'. If there
            # are any left, put that in ARGUMENTS, keeping the last one
            # (retaining cmdline order)
            for item in ARGLIST:
                if item[0] == a:
                    ARGUMENTS[a] = item[1]

def _Remove_Target(targ: str) -> None:
    """Remove *targ* from ``BUILD_TARGETS`` and ``COMMAND_LINE_TARGETS``.

    Used to remove a target that is no longer valid. This can happpen
    because the command line is processed once early, before we see any
    :func:`SCons.Script.Main.AddOption` calls, so we could not recognize
    it belongs to an option and is not a standalone target argument.

    Since we are "correcting an error", we also have to fix up the internal
    :data:`_build_plus_default` list.

    .. versionadded:: NEXT_RELEASE

    """
    if targ:
        if targ in COMMAND_LINE_TARGETS:
            COMMAND_LINE_TARGETS.remove(targ)
        if targ in BUILD_TARGETS:
            BUILD_TARGETS.remove(targ)
        if targ in _build_plus_default:
            _build_plus_default.remove(targ)

def _Set_Default_Targets_Has_Been_Called(d, fs):
    return DEFAULT_TARGETS

def _Set_Default_Targets_Has_Not_Been_Called(d, fs):
    if d is None:
        d = [fs.Dir('.')]
    return d

_Get_Default_Targets = _Set_Default_Targets_Has_Not_Been_Called

def _Set_Default_Targets(env, tlist) -> None:
    global DEFAULT_TARGETS
    global _Get_Default_Targets
    _Get_Default_Targets = _Set_Default_Targets_Has_Been_Called
    for t in tlist:
        if t is None:
            # Delete the elements from the list in-place, don't
            # reassign an empty list to DEFAULT_TARGETS, so that the
            # variables will still point to the same object we point to.
            del DEFAULT_TARGETS[:]
            BUILD_TARGETS._clear()
            _build_plus_default._clear()
        elif isinstance(t, SCons.Node.Node):
            DEFAULT_TARGETS.append(t)
            BUILD_TARGETS._add_Default([t])
            _build_plus_default._add_Default([t])
        else:
            nodes = env.arg2nodes(t, env.fs.Entry)
            DEFAULT_TARGETS.extend(nodes)
            BUILD_TARGETS._add_Default(nodes)
            _build_plus_default._add_Default(nodes)


help_text = None


def HelpFunction(text, append: bool = False, local_only: bool = False) -> None:
    """The implementaion of the the ``Help`` method.

    See :meth:`~SCons.Script.SConscript.Help`.

    .. versionchanged:: 4.6.0
       The *keep_local* parameter was added.
    .. versionchanged:: 4.9.0
       The *keep_local* parameter was renamed *local_only* to match manpage
    """
    global help_text
    if help_text is None:
        if append:
            with StringIO() as s:
                PrintHelp(s, local_only=local_only)
                help_text = s.getvalue()
        else:
            help_text = ""

    help_text += text


# Will be non-zero if we are reading an SConscript file.
sconscript_reading: int = 0

_no_missing_sconscript = True
_warn_missing_sconscript_deprecated = False  # TODO: now unused

def set_missing_sconscript_error(flag: bool = True) -> bool:
    """Set behavior on missing file in SConscript() call.

    Returns:
        previous value
    """
    global _no_missing_sconscript
    old = _no_missing_sconscript
    _no_missing_sconscript = flag
    return old


def Variables(files=None, args=ARGUMENTS):
    return SCons.Variables.Variables(files, args)


# Adding global functions to the SConscript name space.
#
# Static functions that do not trigger initialization of
# DefaultEnvironment() and don't use its state.
GetSConsVersion = _SConscript.SConsEnvironment.GetSConsVersion
EnsureSConsVersion = _SConscript.SConsEnvironment.EnsureSConsVersion
EnsurePythonVersion = _SConscript.SConsEnvironment.EnsurePythonVersion
Exit = _SConscript.SConsEnvironment.Exit
GetLaunchDir = _SConscript.SConsEnvironment.GetLaunchDir
SConscriptChdir = _SConscript.SConsEnvironment.SConscriptChdir

# Functions that end up calling methods or Builders in the
# DefaultEnvironment().
GlobalDefaultEnvironmentFunctions = [
    # Methods from the SConsEnvironment class, above.
    'Default',
    'Export',
    'Help',
    'Import',
    #'SConscript', is handled separately, below.

    # Methods from the Environment.Base class.
    'AddPostAction',
    'AddPreAction',
    'Alias',
    'AlwaysBuild',
    'CacheDir',
    'Clean',
    #The Command() method is handled separately, below.
    'Decider',
    'Depends',
    'Dir',
    'NoClean',
    'NoCache',
    'Entry',
    'Execute',
    'File',
    'FindFile',
    'FindInstalledFiles',
    'FindSourceFiles',
    'Flatten',
    'GetBuildPath',
    'Glob',
    'Ignore',
    'Install',
    'InstallAs',
    'InstallVersionedLib',
    'Literal',
    'Local',
    'ParseDepends',
    'Precious',
    'Pseudo',
    'PyPackageDir',
    'Repository',
    'Requires',
    'SConsignFile',
    'SideEffect',
    'Split',
    'Tag',
    'Value',
    'VariantDir',
]

GlobalDefaultBuilders = [
    # Supported builders.
    'CFile',
    'CXXFile',
    'DVI',
    'Jar',
    'Java',
    'JavaH',
    'Library',
    'LoadableModule',
    'M4',
    'MSVSProject',
    'Object',
    'PCH',
    'PDF',
    'PostScript',
    'Program',
    'RES',
    'RMIC',
    'SharedLibrary',
    'SharedObject',
    'StaticLibrary',
    'StaticObject',
    'Substfile',
    'Tar',
    'Textfile',
    'TypeLibrary',
    'Zip',
    'Package',
]

# DefaultEnvironmentCall() initializes DefaultEnvironment() if it is not
# created yet.
for name in GlobalDefaultEnvironmentFunctions + GlobalDefaultBuilders:
    exec ("%s = _SConscript.DefaultEnvironmentCall(%s)" % (name, repr(name)))
del name

# There are a handful of variables that used to live in the
# Script/SConscript.py module that some SConscript files out there were
# accessing directly as SCons.Script.SConscript.*.  The problem is that
# "SConscript" in this namespace is no longer a module, it's a global
# function call--or more precisely, an object that implements a global
# function call through the default Environment.  Nevertheless, we can
# maintain backwards compatibility for SConscripts that were reaching in
# this way by hanging some attributes off the "SConscript" object here.
SConscript = _SConscript.DefaultEnvironmentCall('SConscript')

# Make SConscript look enough like the module it used to be so
# that pychecker doesn't barf.
SConscript.__name__ = 'SConscript'

SConscript.Arguments = ARGUMENTS
SConscript.ArgList = ARGLIST
SConscript.BuildTargets = BUILD_TARGETS
SConscript.CommandLineTargets = COMMAND_LINE_TARGETS
SConscript.DefaultTargets = DEFAULT_TARGETS

# The global Command() function must be handled differently than the
# global functions for other construction environment methods because
# we want people to be able to use Actions that must expand $TARGET
# and $SOURCE later, when (and if) the Action is invoked to build
# the target(s).  We do this with the subst=1 argument, which creates
# a DefaultEnvironmentCall instance that wraps up a normal default
# construction environment that performs variable substitution, not a
# proxy that doesn't.
#
# There's a flaw here, though, because any other $-variables on a command
# line will *also* be expanded, each to a null string, but that should
# only be a problem in the unusual case where someone was passing a '$'
# on a command line and *expected* the $ to get through to the shell
# because they were calling Command() and not env.Command()...  This is
# unlikely enough that we're going to leave this as is and cross that
# bridge if someone actually comes to it.
Command = _SConscript.DefaultEnvironmentCall('Command', subst=1)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
