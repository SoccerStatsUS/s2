import argparse
import os
import sys

import django


def main(argv=None):
    stages = {
        'base': 'load1',
        'lineups': 'load2',
        'game-stats': 'load3',
        'news-stats': 'load4',
    }
    aliases = dict(zip(('1', '2', '3', '4'), stages))
    parser = argparse.ArgumentParser(description='Run a stage of the Mongo → Postgres build.')
    parser.add_argument('stage', choices=(*stages, 'generate', *aliases))
    parser.add_argument('--settings', default='build_settings')
    args = parser.parse_args(argv)

    os.environ['DJANGO_SETTINGS_MODULE'] = args.settings
    django.setup()

    if not sys.stdin.isatty():
        import pdb

        def _fail_set_trace(*args, **kwargs):
            raise RuntimeError('pdb.set_trace() hit in non-interactive build')
        pdb.set_trace = _fail_set_trace

    if args.stage == 'generate':
        from build.generate import generate
        generate()
    else:
        from build import load
        getattr(load, stages[aliases.get(args.stage, args.stage)])()


if __name__ == '__main__':
    main()
