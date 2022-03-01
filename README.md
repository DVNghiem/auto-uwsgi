# Auto deploy Django project

## Install:

    pip install auto-uwsgi

## Using

```python
>>> from auto_uwsgi import Deployment
>>> deploy = Deployment(
    '<username>',
    '<path to project>',
    '<path to virtual environment>',
    '<domain name or ip>'
)
>>> deploy.start()
```

### Change setting

```python
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

## Example

```python
>>> from auto_uwsgi import Deployment
>>> deploy = Deployment(
    'nghiem',
    '/home/nghiem/auto-uwsgi/tests/projecttest',
    '/home/nghiem/auto-uwsgi/tests/venv',
    '192.168.0.105'
)
>>> deploy.start()
```
