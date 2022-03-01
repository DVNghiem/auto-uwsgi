from auto_uwsgi import Deployment

deploy = Deployment(
    'nghiem',
    '/home/nghiem/auto-uwsgi/tests/projecttest',
    '/home/nghiem/auto-uwsgi/tests/venv',
    '192.168.0.105'
)

deploy.start()

