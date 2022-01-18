# Vendored packages

## Why?

I'd like to avoid installing from Git (especially as I'd like Inboxen to be on
PyPI) but sometimes upstream is just not fast enough at getting a new release
out.

Packages should only be added here on a temporary basis. If a package has been
abandoned and you want it to be part of Inboxen, add it as a Django app i.e.
"inboxen.somepackage". Things like tests are not included during vendoring!

## How?

First, move `pyproject.toml` to the project root dir. This file can't live
there because Pip won't ignore it even if it has no build config and there's a
`setup.py` just setting there. Also `vendoring` won't let you configure it via
any other mechanism.

Edit `vendor.txt` and run `vendoring sync` from the project root dir. Commit
changes and you're done.

Remember to rename imports and remove the dependency from `setup.py`!
