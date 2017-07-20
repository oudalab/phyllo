
## Developer Notes

### Install the virtual environment

```
py3clean .
virtualenv -p python3 venv
source venv/bin/activate
pip3 install --editable .
pip3 install appdirs --upgrade
pip3 install -r requirements.txt
python3 setup.py test
```

