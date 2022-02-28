import os


class Deployment(object):
    def __init__(self, path_project, path_libs, domain, sudo_password='') -> None:
        os.system(f'cd {path_project}')
        os.open('sudo apt-get install nginx').write(sudo_password)
        os.system(f'pip install -r {path_libs}')
        self.path_project = path_project if path_project[-1] != '/' else path_project[-1]
        self.project_name = os.path.split(self.path_project)
        self.domain = domain
        self.sudo_password = sudo_password

    def create_venv(self):
        status = os.system('python3 -m venv venv')
        assert status == 0, "venv is not installed"

    def nginx_conf(self):
        nginx_config = '''
                # the upstream component nginx needs to connect to
                upstream django {
                    server unix://%s/%s.sock;
                }

                # configuration of the server
                server {
                    listen      80;
                    server_name %s;
                    charset     utf-8;

                    # max upload size
                    client_max_body_size 75M;

                    # Django media and static files
                    location /media  {
                        alias %s/media;
                    }
                    location /static {
                        alias %s/static;
                    }

                    # Send all non-media requests to the Django server.
                    location / {
                        uwsgi_pass  django;
                        include     %s/uwsgi_params;
                    }
                }
                '''.format(self.path_project, self.project_name, self.domain, self.project_name, self.project_name, self.project_name)
        with open(f'/etc/nginx/sites-available/{self.project_name}.conf', 'w') as f:
            f.write(nginx_config)

        if self.sudo_password == '':
            os.system(
                f'sudo ln -s /etc/nginx/sites-available/{self.project_name}.conf /etc/nginx/sites-enabled/')
        else:
            os.system(
                f'echo {self.sudo_password}|sudo -S ln -s /etc/nginx/sites-available/{self.project_name}.conf /etc/nginx/sites-enabled/')

    def create_uwsgi_params(self):
        with open(os.path.join(self.path_project, 'uwsgi_params'), 'w') as f:
            f.write('''
                    uwsgi_param  QUERY_STRING       $query_string;
                    uwsgi_param  REQUEST_METHOD     $request_method;
                    uwsgi_param  CONTENT_TYPE       $content_type;
                    uwsgi_param  CONTENT_LENGTH     $content_length;
                    uwsgi_param  REQUEST_URI        $request_uri;
                    uwsgi_param  PATH_INFO          $document_uri;
                    uwsgi_param  DOCUMENT_ROOT      $document_root;
                    uwsgi_param  SERVER_PROTOCOL    $server_protocol;
                    uwsgi_param  REQUEST_SCHEME     $scheme;
                    uwsgi_param  HTTPS              $https if_not_empty;
                    uwsgi_param  REMOTE_ADDR        $remote_addr;
                    uwsgi_param  REMOTE_PORT        $remote_port;
                    uwsgi_param  SERVER_PORT        $server_port;
                    uwsgi_param  SERVER_NAME        $server_name;
            ''')

    def create_static(self):
        status = os.system('python3 manage.py collectstatic')
        assert status == 0, 'error collectstatic django'

    def restart_nginx(self):
        if self.sudo_password == '':
            os.system('sudo /etc/init.d/nginx restart')
        else:
            os.system('echo %s|sudo -S /etc/init.d/nginx restart' %
                      (self.sudo_password))

    def create_ini(self):
        with open(os.path.join(self.project_name, self.project_name+'.ini'), 'w') as f:
            f.write('''
                [uwsgi]
                # full path to Django project's root directory
                chdir            = %s
                # Django's wsgi file
                module           = %s.wsgi
                # full path to python virtual env
                home             = %s
                # enable uwsgi master process
                master          = true
                # maximum number of worker processes
                processes       = 10
                # the socket (use the full path to be safe
                socket          = %s/%s.sock
                # socket permissions
                chmod-socket    = 666
                # clear environment on exit
                vacuum          = true
                # daemonize uwsgi and write messages into given log
                daemonize       = %s/uwsgi-emperor.log
            
            '''.format(self.path_project, self.project_name, os.path.join(self.path_project, 'venv'), self.path_project, self.project_name, self.project_name))

    def ln_init(self):
        os.system('mkdir vas')
        os.system(
            f'sudo ln -s {self.path_project}/{self.project_name}.ini {self.path_project}/vas/')

    def create_service(self):
        with open('/etc/systemd/system/emperor.uwsgi.service', 'w') as f:
            f.write(f'''
                [Unit]
                Description=uwsgi emperor for micro domains website
                After=network.target
                [Service]
                User=ubuntu
                Restart=always
                ExecStart={self.path_project}/venv/bin/uwsgi --emperor {self.path_project}/vas --uid www-data --gid www-data
                [Install]
                WantedBy=multi-user.target
            ''')

    def start(self):
        self.create_venv()
        self.nginx_conf()
        self.create_uwsgi_params()
        self.create_static()
        self.restart_nginx()
        self.create_ini()
        self.ln_init()
        self.create_service()
        if self.sudo_password == '':
            os.system('sudo systemctl enable emperor.uwsgi.service')
            os.system('sudo systemctl start emperor.uwsgi.service')
        else:
            os.system(
                'echo %s|sudo -S systemctl enable emperor.uwsgi.service' % (self.sudo_password))
            os.system(
                'echo %s|sudo -S systemctl start emperor.uwsgi.service' % (self.sudo_password))
