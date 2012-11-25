"""Base for commands"""

import argparse
import logging

# ============================================================================
# 

class SubCommand(object):
    """Base for all SubCommands that can be called on the command line. 

    :cls:`SubCommand` instances are created by the script entry point and 
    their ``__call__`` method called. 
    """

    name = None
    """Command line name for the Sub Command.

    Must be specified by sub classes.
    """

    help = None
    """Command line help for the Sub Command."""

    description = None
    """Command line description for the Sub Command."""


    @classmethod
    def add_sub_parser(cls, sub_parsers):
        """Called to add a parser to ``sub_parsers`` for this command. 

        Sub classes may override this method but pass the call up to ensure 
        the sub parser is created correctly. 

        A default ``func`` argument is set on the :cls:``ArgumentParser`` to 
        point to the constructor for the SubCommand class.

        Returns the :cls:`argparser.ArgumentParser`.
        """
        
        assert cls.name, "command_name must be set."

        parser = sub_parsers.add_parser(cls.name,
            help=cls.help or "No help", 
            description=cls.description or "No help", 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.set_defaults(func=cls)
        return parser
    
    def __call__(self):
        """Called to execute the SubCommand.
        
        Must return a tuple of (rv, msg). Rv is returned as the script exit 
        and msg is the std out message.
        
        Must be implemented by sub classes.
        """
        raise NotImplementedError()
        
# ============================================================================
# 

class NoopCommand(SubCommand):
    """Testing no op."""

    name = "noop"
    """Command line name for the Sub Command.

    Must be specified by sub classes.
    """

    help = "some help"
    """Command line help for the Sub Command."""

    description = "some desc"
    """Command line description for the Sub Command."""


    def __init__(self, args):
        pass
        
    def __call__(self):
        """Just return a no op message."""
        return (0, "no op")
