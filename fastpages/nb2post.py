#!/usr/bin/env python3
import inspect
from nbdev import export2html

def main():
    fname = '_notebooks/*.ipynb'
    dest = '_posts/'
    template_file = '/fastpages/fastpages.tpl'

    # Build kwargs based on the function signature to be compatible across nbdev versions
    sig = inspect.signature(export2html.notebook2html)
    kw = {'template_file': template_file}

    if 'execute' in sig.parameters:
        kw['execute'] = False
    elif 'run' in sig.parameters:
        kw['run'] = False
    elif 'do_execute' in sig.parameters:
        kw['do_execute'] = False
    # else: function doesn't accept an execution-control arg; call without it.

    # Call the function using named parameters where supported
    try:
        export2html.notebook2html(fname=fname, dest=dest, **kw)
    except TypeError:
        # Fallback: try a simple positional call (many versions accept (fname, dest, ...))
        try:
            export2html.notebook2html(fname, dest)
        except Exception:
            # Re-raise so logs show the full traceback for debugging
            raise

if __name__ == '__main__':
    main()