#!/usr/bin/env python


"""
Fabric file to initialize a EC2 instance and have it run a Django + gunicorn
server with Nginx as reverse proxy, served over https secured by Let's encrypt:
should rank A+ on SSLlab

Note that this script is just a quick example and has not been extensively
tested, idempotence is not guaranteed.

This script assumes that .ssh/config has been properly setup with the private
key to access the EC2 instance. Here, we call our instance Origin
"""


from fabric.api import env, run, sudo, cd,  put, prefix
import boto.ec2
from fabric.colors import green as _green, yellow as _yellow
import os
from contextlib import contextmanager as _contextmanager


env.use_ssh_config = True
env.hosts = ['Origin', ]
current_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
DOMAIN_NAME = 'todolist.ovh'
py_version = '3.6.0'
py_name = 'Python-' + py_version
PROJECT = 'to_do_list'
env.directory = '~/{0}/'.format(PROJECT)
# The path to the .env file used to configure with Django.environ
env.activate = 'source ~/virtual/bin/activate'.format(PROJECT)


@_contextmanager
def virtualenv(extension=''):
    """
    Context manager acting as shortcut to launch command within the virtual
    environment.
    """

    with cd(env.directory + extension):
        with prefix(env.activate):
            yield


def compile_python_from_source():
    """
    Install the necessary package to build Python 3.6 from source as well as
    all relevant packages (PIL for instance).
    """

    sudo('apt-get update')
    sudo('apt-get dist-upgrade -y')
    sudo('apt-get upgrade -y')
    packages_required = (
        'build-essential', 'libncursesw5-dev', 'libreadline-gplv2-dev',
        'libssl-dev', 'libgdbm-dev', 'libc6-dev', 'libsqlite3-dev',
        'tk-dev', 'libbz2-dev', 'liblzma-dev', 'python3-dev', 'python3-PIL',
        'git', 'libpq-dev', 'gettext',
    )
    sudo('apt-get install -y {0}'.format(' '.join(packages_required)))
    sudo('mkdir -p /usr/local/opt/python-{0}'.format(py_version))
    run('mkdir -p ~/tmp')
    with cd('~/tmp'):
        run('wget http://www.python.org/ftp/python/'
            '{0}/Python-{0}.tgz'.format(py_version))
        run('tar -zxf {0}.tgz'.format(py_name))

    with cd('~/tmp/{0}'.format(py_name)):
        run('./configure --prefix=/usr/local/opt/python-{0}'.format(py_version))
        run('make')
        sudo('make install')
    run('rm -rf ~/tmp')


def install_servers():
    """
    Purge the useless apache2 and install nginx and supervisor (used to keep
    Gunicorn running even if the server restarts).
    """

    sudo('apt-get purge apache2')
    sudo('apt-get install -y nginx supervisor')


def setup_lets_encrypt():
    """
    Setting up the nginx server to only serve over HTTPS with strong encryption
    algorithm and HSTS. The certificate is issued by Letsencrypt using their
    automated process. A cron task has to be set up to renew it every 90 days.

    A good tutorial can be found here:
    https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-l
    et-s-encrypt-on-ubuntu-14-04
    """

    with cd('/usr/local/sbin'):
        sudo('wget https://dl.eff.org/certbot-auto')
        sudo('chmod a+x certbot-auto')
    nginx_conf = current_dir + 'nginx.config'
    put(nginx_conf, '/etc/nginx/sites-available/default', use_sudo=True)
    sudo('nginx -t')
    sudo('/etc/init.d/nginx restart')
    with cd('/usr/local/sbin'):
        sudo('certbot-auto certonly -a webroot --webroot-path=/usr/share/nginx/'
             'html -d {0} -d www.{0}'.format(DOMAIN_NAME))
    sudo('openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048')


def cron():
    sudo("crontab -e")
    # When prompted, add the following lines
    # 30 2 * * 1 /usr/local/sbin/certbot-auto renew >> /var/log/le-renew.log
    # 35 2 * * 1 /etc/init.d/nginx reload


def setup_nginx():
    """Load the nginx.conf to the EC2, test and reload the server."""

    nginx_conf = current_dir + 'nginx.config'
    put(nginx_conf, '/etc/nginx/sites-available/default', use_sudo=True)
    sudo('unlink /etc/nginx/sites-enabled/default')
    sudo('ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled')
    sudo('nginx -t')
    sudo('/etc/init.d/nginx stop')
    sudo('/etc/init.d/nginx start')


def set_virtual_env():
    """Set up a virtual environment using our compiled Python 3.6."""

    run('/usr/local/opt/python-{0}/bin/python3 -m venv virtual'.format(py_version))


def set_project_and_gunicorn():
    """
    Clone the repository where the project lives, install in the virtual env
    the production requirement, collectstatic, migrate, then put the
    supervisor script and execute it.
    """

    run('git clone https://www.github.com/arnaudblois/{0}/'.format(PROJECT))
    with virtualenv():
        run('pip install -r requirements/production.txt')
        run('python manage.py collectstatic --settings=config.settings.production')
        run('python manage.py compilemessages --settings=config.settings.production')
        run('python manage.py makemigrations --settings=config.settings.production')
        run('python manage.py migrate --settings=config.settings.production')
    put(current_dir + '.env', env.directory + 'config/settings')
    put(current_dir + PROJECT.replace('_', '') + ".conf",
        "/etc/supervisor/conf.d/{}.conf".format(PROJECT), use_sudo=True)
    run('mkdir -p ~/web/logs/')
    run('touch ~/web/logs/gunicorn_supervisor.log')
    put(current_dir + 'gunicorn_start', '~/web/gunicorn_start', use_sudo=True)
    sudo('chown ubuntu:ubuntu /home/ubuntu/web/gunicorn_start')
    sudo('chmod 755 /home/ubuntu/web/gunicorn_start')
    sudo('supervisorctl reread')
    sudo('supervisorctl update')
    sudo('supervisorctl restart todolist')
