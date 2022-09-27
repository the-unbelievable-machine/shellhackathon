# -*- coding: utf-8 -*-
# system imports
import os
import logging

# third-party
import click
import click_log

# project imports


##############################################################################
log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)
click_log.basic_config(logger)


##############################################################################
def do_work():
    print('working...')


##############################################################################
@click.command()
@click_log.simple_verbosity_option(logger)
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """
    TODO This is the cli documentation
    """
    logger.info('Making something ...')
    do_work()


if __name__ == '__main__':
    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
