To-Do-List
==========

Thank you for visiting my repository. This is a simple example of a to-do list application done with Django.
Though simple, it is fully tested and deployed on AWS services here: https://todolist.ovh. Fell free to visit this website and play around.

:License: MIT


Short Description
--------------------

I added a little twist to standard to-do lists to make things interesting.
The principle is simple: each user chooses a team then creates Tasks.
Tasks have a visibility setting which can be either:

* private, in which case only the creator can see them

* team_only, visible within a team

* public. Anyone can see them

If a task is visible to a user, she can mark it as done.
The creator can then check this is the case and mark it as closed.
This increases the reputation of the user who completed it, based on how difficult the task was


Getting started
----------------

* Go to https://todolist.ovh and click "Sign up for free" to create a normal user account. Fill out the form and upon submission, you will find a "Verify Your E-mail Address" page. The email will arrive to the address you provided, it's possible it ends up in the spam folder. Use the link and the user is now active.

* You will then have to choose a Team (this is a permanent choice) and enter your name to access the main page.

* On the main page, you can see all the tasks that are visible to you. From there, you can create a new task, browse the existing tasks or mark a task as done using the "Action" button. You can also edit and delete the tasks that you created if they are still new.


Technical Stack
----------------

* EC2 running Gunicorn / Django 1.10 with Nginx as reverse proxy via unix socket.

* RDS PostgreSQL Database

* Automatic Certificate creation by let's encrypt (A+ on SSL labs https://www.ssllabs.com/ssltest/analyze.html?d=todolist.ovh)


Running the project locally
----------------------------

* I use Python 3.6 compiled from source. The first step is to create a virtual environment preferable outside of the project::

    $ cd ~/your-path/virtual/
    $ python -m venv name_of_virtual
    $ source name_of_virtual/bin/activate

* Then, cd to the root folder of the project. Note that I've set the database to sqlite in local and test. This is strongly discouraged when using PostgreSQL in production (as it should be) but that way you don't need to set up a PostgreSQL server::

    $ cd path/to/project
    $ pip install -r requirements/local.txt
    $ pip install -r requirements/test.txt
    $ python manage.py makemigrations
    $ python manage.py migrate
    $ python manage.py test --settings=config.settings.test

* To create a **superuser account**, use this command::

    $ python manage.py createsuperuser

The admin panel is accessible at http://localhost:8000/admin after you start the developement server. To do so::

    $ python manage.py runserver --settings=config.settings.local



A few technical points
------------------------------

* The initial boilerplate was generated with cookie-cutter. The project follows the 12 factor philosophy. Unlike the skeleton created with django_startapp, the settings, docs and requirements are kept separate from the source code. The settings rely on django.environ to set up values that shouldn't be version-controlled such as the different credentials and the secret_key. Defaults are included for convenience in case the .env is not found and should work in local.

* The registration is handled by django_allauth. The package users was provided by cookie-cutter, I've written the 'tasks' package.

* The popups are managed by Sweet Alert 2. As this javascript module has been recently rewritten to use ES6 features, especially Promises, it requires es6-promise.js to polyfill (included by CDN).

* All my code follows PEP8 with --max-line-length=120 as specified per Django, I tend to stick to shorter lines though.

* HTML with Bootstrap v4, SASS for the CSS, Font-Awesome

* Actions on a task, filtering and ordering the main table are all done in AJAX with jQuery to avoid reloading everything.


Testing
---------

The system has been unittested quite thoroughly, using factory_boy as a fixture replacement

To run the tests::

    $ python manage.py test --settings=config.settings.test


To check the coverage and generate an HTML coverage report::

    $ coverage run manage.py test --settings=config.settings.test
    $ coverage html

Then open htmlcov/index.html


Possible Future Work
--------------------

A few extra features I can think of that may (or not) make this project useful to the world:

* Create the historic tables for the task status and display the history in details

* Completing a task takes some time, add the possibility to claim the exclusivity of a task (status 'assigned' already included)

* In combination with the 'assign' story above, add deadline management. This would affect the reputation gain

* Increase the incentive by having

* Use React + Redux to build a single page app using the Django back-end as an API


Deployment
----------

Additional info to deploy are given in doc/deploy.rst
