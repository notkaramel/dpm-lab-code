
### Generating pydoc for helper module

```bash
python -m pydoc -w utils utils.brick utils.sound utils.telemetry utils.filters utils.dummy utils.remote utils.rmi
mv utils*.html ./docs/
```

### Running Scripts within Directories

Make sure you are in the root directory of this repository, whichever directory contains `utils/` folder.  

Then in order to run a script within a folder, perform the following command in terminal/command line:

`python tests/_test_busy_wait.py`

This should work on all platforms, but ensure **on Windows** DO NOT DO:

`python .\tests\_test_busy_wait.py` (it gives an import error)

