
### Generating pydoc for helper module

```bash
python -m pydoc -w utils utils.brick utils.sound utils.telemetry utils.filters utils.dummy utils.remote utils.rmi
mv utils*.html ./docs/
```