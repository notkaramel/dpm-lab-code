
### Generating pydoc for helper module

```bash
python -m pydoc -w utils utils.brick utils.sound utils.telemetry utils.filter
mv utils*.html ./docs/
```