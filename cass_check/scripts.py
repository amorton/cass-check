"""Entry points for exported scripts."""

import argparse
import datetime
import logging
import os.path
import sys
import traceback

import pkg_resources

import file_util

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Sub Commands take the command line args and call the function to do the 
# work. Sub commands are retrieved from the ``cass-check.tasks`` entry 
# point using :mod:`pkg_resources`, see :func:`arg_parser`.
# The ones here are global.

def execute_help(args):
    """Global sub command than prints the help for a sub command.
    """
    temp_parser = arg_parser()
    if args.command:
        temp_parser.parse_args([args.command, "-h"])
    return temp_parser.format_help()
    
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 
def arg_parser():
    """Builds a :class:`argparse.ArgumentParser` for the ``cass-check`` 
    command. 
    
    The ``cass-check`` script uses a sub command structure, like svn or 
    git. For example::
    
        cass-check --check-name=foo collect task-1
        
    * ``cass-check`` is the script name. 
    * ``check-name`` is an option for the entire script.
    * ``collect`` is the sub command
    * ``task-1`` is a positional arg for the ``collect`` sub command.
    """
    
    # This is the main parser that the script entry point uses.
    main_parser = argparse.ArgumentParser(
        description="cass-check: Cassandra Checkup", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # say we have sub commands
    sub_parsers = main_parser.add_subparsers(title="Commands", 
        description="Commands.")

    # Start adding sub commands
    # use set_default() to specify a function to call for each sub command.

    # Global / static sub commands
    # Show help for a sub command.
    parser = sub_parsers.add_parser("help", help="Get help.")
    parser.set_defaults(func=execute_help)
    parser.add_argument('command', type=str, default="", nargs="?",
        help='Command to print help for.')
    
    for entry_point in pkg_resources.iter_entry_points(
        "cass_check.commands"):
        # Load the class and add it's parser
        entry_point.load().add_sub_parser(sub_parsers)

    # Global Configuration
    main_parser.add_argument("--output-base", dest="output_base", 
        default="/tmp/cass-check",
        help="Base output directory.")
    main_parser.add_argument("--check-name", dest="check_name", 
        default=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        help="Name for this checkup report.")
    main_parser.add_argument("--check-dir", dest="check_dir",
        help="Full path to output to, if specified output-base and "\
            "check-name are ignored.")
        
    main_parser.add_argument("--log-level", default="DEBUG", 
        dest="log_level", 
        choices=["FATAL", "CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"],
        help="Logging level.")
    main_parser.add_argument("--log-file", default="./cass-check.log", 
        dest="log_file", 
        help="Logging file.")

    return main_parser

def validate_global_args(args):
    
    file_util.ensure_dir(args.output_base)
    
    if not args.check_dir:
        args.check_dir = os.path.join(args.output_base, args.check_name)
    file_util.ensure_dir(args.check_dir)
    
    return
    
def cass_check_main():

    """Script entry point for the command line tool
    """
    
    args = arg_parser().parse_args()

    logging.basicConfig(filename=os.path.abspath(args.log_file), 
        level=getattr(logging, args.log_level))
    log = logging.getLogger(__name__)
    log.debug("Got command args %(args)s" % vars())
    
    validate_global_args(args)
    log.info("Output directory is {check_dir}".format(
        check_dir=args.check_dir))
    
    # commands set their ctor as a default argument. 
    # if no commands are specified we run all commands
    # TODO: HELP ?
    if args.func:
        # could be the help command
        cmd_or_help = args.func(args)
        if isinstance(cmd_or_help, basestring):
            sys.stdout.write(str(cmd_or_help) + "\n")
            sys.exit(0)
        commands = [cmd_or_help]
    else:
        commands = [
            entry_point.load()(args)
            for entry_point in pkg_resources.iter_entry_points(
                "cass-check.commands")
        ]
    cmd_names = ", ".join([
        cmd.name
        for cmd in commands
    ])
    log.info("Running commands {cmd_names}".format(cmd_names=cmd_names))
    
    try:
        out = []
        rv = 0
        for cmd in commands:
            log.debug("Starting command {c.name}".format(c=cmd))
            rv, cmd_out = cmd()
            
            out.append(cmd_out)
            if rv !=0:
                break

        sys.stdout.write(str(cmd_out) + "\n")

    except (Exception) as exc:
        print "Error:"
        traceback.print_exc()
        sys.exit(1)
    sys.exit(rv)

