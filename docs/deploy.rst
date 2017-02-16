=========================================================================
Deploy
=========================================================================

The project is currently deployed on AWS with an EC2 instance as a Django +
Gunicorn web server with Nginx as reverse proxy.
The database is on RDS.

Prerequisites
--------------

To start the project, we need:

    * An AWS account with a RDS and a EC2 instance
    * A Google developer account to get Recaptch keys and set up their postmaster protection
    * A valid valid
    * A SendGrid account
    * Github account


Configuring SSH
----------------

The first step is to set up the .ssh/config to ssh into the EC2 without
password::

    Host Origin
        User user_name
        HostName ec2_instance.compute.amazonaws.com
        IdentityFile ~/path/to/certificate/todolist.pem


Setting up the servers
-----------------------

I use Fabric3 to streamline this. Alternatives would be Ansible or Docker, the learning curve is steeper.
To set up the EC2, using deploy/fabfile.py::

    pip install fabric3
    fab compile_python_from_source
    fab install_servers
    fab setup_lets_encrypt
    fab cron
    fab setup_nginx
    fab set_virtual_env
    fab set_project_and_gunicorn

This installs the latest python built from source, installs the servers and
sets up the certificate with let's encrypt. It then sets up Nginx and finally
starts a Gunicorn server


Email
-----------------

To avoid the emails being flagged systematically as spam, or even blocked,
we have to set up the Sender Policy Framework by setting our DNS record.
We create a SPF record with::

    "v=spf1 a include:sendgrid.net ~all"

This says that emails can be sent by sendgrid on our behalf.
There is also the postmaster tool by Google which is worth completing,
it requires adding the TXT record that they need.
