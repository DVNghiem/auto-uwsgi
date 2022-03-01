import os


class Deployment(object):
    def __init__(self, username, path_project, path_venv, domain) -> None:

        print('-------------Install nginx------------')
        status = os.system('sudo apt-get install nginx -y')
        assert status==0, 'install nginx error'
        
        self.path_project = path_project if path_project[-1] != '/' else path_project[:-1]
        self.project_name = os.path.split(self.path_project)[-1]
        self.domain = domain
        self.path_venv = path_venv
        self.username = username

    def nginx_conf(self):
        nginx_config = """
# the upstream component nginx needs to connect to
upstream django {
    server unix://"""+self.path_project+"""/"""+self.project_name+""".sock;
}

# configuration of the server
server {
    listen      80;
    server_name """+self.domain+""";
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;

    # Django media and static files
    location /media  {
        alias """+self.path_project+"""/media;
    }
    location /static {
        alias """+self.path_project+"""/static;
    }

    # Send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     """+self.path_project+"""/uwsgi_params;
    }
}
                """
        with open(f'{self.path_project}/{self.project_name}.conf', 'w') as f:
            f.write(nginx_config)
        os.system(f'sudo mv {self.path_project}/{self.project_name}.conf /etc/nginx/sites-available/')
        os.system(
            f'sudo ln -s /etc/nginx/sites-available/{self.project_name}.conf /etc/nginx/sites-enabled/')

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
        status = os.system(f'python3 {self.path_project}/manage.py collectstatic')
        assert status == 0, 'error collectstatic django'

    def restart_nginx(self):
        os.system('sudo /etc/init.d/nginx restart')

    def create_ini(self):
        with open(os.path.join(self.path_project, self.project_name+'.ini'), 'w') as f:
            f.write(f'''
[uwsgi]
# full path to Django project's root directory
chdir            = {self.path_project}
# Django's wsgi file
module           = {self.project_name}.wsgi
# full path to python virtual env
home             = {self.path_venv}
# enable uwsgi master process
master          = true
# maximum number of worker processes
processes       = 10
# the socket (use the full path to be safe
socket          = {self.path_project}/{self.project_name}.sock
# socket permissions
chmod-socket    = 666
# clear environment on exit
vacuum          = true
# daemonize uwsgi and write messages into given log
daemonize       = {self.path_project}/uwsgi-emperor.log
            
            ''')

    def ln_init(self):
        os.system(f'mkdir {os.path.join(self.path_project, "vas")}')
        os.system(
            f'sudo ln -s {self.path_project}/{self.project_name}.ini {self.path_project}/vas/')

    def create_service(self):
        with open(os.path.join(self.path_project, 'emperor.uwsgi.service'), 'w') as f:
            f.write(f'''
[Unit]
Description=uwsgi emperor for micro domains website
After=network.target
[Service]
User={self.username}
Restart=always
ExecStart={self.path_venv}/bin/uwsgi --emperor {self.path_project}/vas --uid www-data --gid www-data
[Install]
WantedBy=multi-user.target
            ''')
        os.system(f'sudo mv {os.path.join(self.path_project, "emperor.uwsgi.service")} /etc/systemd/system/')
    
    def start(self):

        print('------------Nginx config-----------')
        self.nginx_conf()
        print('------------UWSGI param-----------')
        self.create_uwsgi_params()
        print('------------Static file-----------')
        self.create_static()
        print('------------Restart nginx-----------')
        self.restart_nginx()
        print('------------ini file-----------')
        self.create_ini()
        print('------------ln config-----------')
        self.ln_init()
        print('------------Service-----------')
        self.create_service()
        os.system('sudo systemctl enable emperor.uwsgi.service')
        os.system('sudo systemctl start emperor.uwsgi.service')
