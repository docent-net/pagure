Pagure
======

:Author: Pierre-Yves Chibon <pingou@pingoured.fr>


Pagure is a light-weight git-centered forge based on pygit2.

Currently, Pagure offers a decent web-interface for git repositories, a
simplistic ticket system (that needs improvements) and possibilities to create
new projects, fork existing ones and create/merge pull-requests across or
within projects.


Homepage: https://github.com/pypingou/pagure

See it at work: https://pagure.io

Playground version: https://stg.pagure.io



Get it running
==============

* Retrieve the sources::

    git clone git://github.com/pypingou/pagure


* Create the folder that will receive the projects, forks, docs and tickets'
  git repo::

    mkdir {repos,docs,forks,tickets}


* Create the inital database scheme::

    python createdb.py


* Run it::

    ./runserver.py


* To get some profiling information you can also run it as::

    ./runserver.py --profile



This will launch the application at http://127.0.0.1:5000

