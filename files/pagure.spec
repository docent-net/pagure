%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from
%distutils.sysconfig import get_python_lib; print (get_python_lib())")}

Name:           pagure
Version:        0.1.24
Release:        1%{?dist}
Summary:        A git-centered forge

License:        GPLv2+
URL:            https://pagure.io/pagure
Source0:        https://pagure.io/releases/pagure/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-nose

BuildRequires:  python-alembic
BuildRequires:  python-arrow
BuildRequires:  python-bleach
BuildRequires:  python-blinker
BuildRequires:  python-chardet
BuildRequires:  python-docutils
BuildRequires:  python-flask
BuildRequires:  python-flask-wtf
BuildRequires:  python-markdown
BuildRequires:  python-psutil
BuildRequires:  python-pygit2 >= 0.20.1
BuildRequires:  python-pygments
BuildRequires:  python-fedora
BuildRequires:  python-openid
BuildRequires:  python-openid-cla
BuildRequires:  python-openid-teams
BuildRequires:  python-straight-plugin
BuildRequires:  python-wtforms
BuildRequires:  python-munch
BuildRequires:  python-enum34
BuildRequires:  python-redis

# EPEL6
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
BuildRequires:  python-sqlalchemy0.8
Requires:  python-sqlalchemy0.8
%else
BuildRequires:  python-sqlalchemy > 0.8
Requires:  python-sqlalchemy > 0.8
%endif

Requires:  python-alembic
Requires:  python-arrow
Requires:  python-bleach
Requires:  python-blinker
Requires:  python-chardet
Requires:  python-docutils
Requires:  python-enum34
Requires:  python-flask
Requires:  python-flask-wtf
Requires:  python-markdown
Requires:  python-psutil
Requires:  python-pygit2 >= 0.20.1
Requires:  python-pygments
Requires:  python-fedora
Requires:  python-openid
Requires:  python-openid-cla
Requires:  python-openid-teams
Requires:  python-straight-plugin
Requires:  python-wtforms
Requires:  python-munch
Requires:  python-redis
Requires:  mod_wsgi

# No dependency of the app per se, but required to make it working.
Requires:  gitolite3

%description
Pagure is a light-weight git-centered forge based on pygit2.

Currently, Pagure offers a web-interface for git repositories, a ticket
system and possibilities to create new projects, fork existing ones and
create/merge pull-requests across or within projects.

%package milters
Summary:            Milter to integrate pagure with emails
BuildArch:          noarch
BuildRequires:      systemd-devel
Requires:           python-pymilter
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
# It would work with sendmail but we configure things (like the tempfile)
# to work with postfix
Requires:           postfix


%description milters
Milters (Mail filters) allowing the integration of pagure and emails.
This is useful for example to allow commenting on a ticket by email.


%package ev
Summary:   EventSource server for pagure
BuildArch: noarch

BuildRequires:      systemd-devel
Requires:  python-redis
Requires:  python-trollius
Requires:  python-trollius-redis
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%description ev
Pagure comes with an eventsource server allowing live update of the pages
supporting it. This packages provides it.


%prep
%setup -q


%build
%{__python2} setup.py build


%install
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Install apache configuration file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/
install -m 644 files/pagure.conf $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/pagure.conf

# Install configuration file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/pagure
install -m 644 files/pagure.cfg.sample $RPM_BUILD_ROOT/%{_sysconfdir}/pagure/pagure.cfg

# Install WSGI file
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/pagure
install -m 644 files/pagure.wsgi $RPM_BUILD_ROOT/%{_datadir}/pagure/pagure.wsgi

# Install the createdb script
install -m 644 createdb.py $RPM_BUILD_ROOT/%{_datadir}/pagure/pagure_createdb.py

# Install the alembic configuration file
install -m 644 files/alembic.ini $RPM_BUILD_ROOT/%{_sysconfdir}/pagure/alembic.ini

# Install the alembic revisions
cp -r alembic $RPM_BUILD_ROOT/%{_datadir}/pagure


# Install the milter files
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/run/pagure
mkdir -p $RPM_BUILD_ROOT/%{_tmpfilesdir}
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
install -m 0644 milters/milter_tempfile.conf \
    $RPM_BUILD_ROOT/%{_tmpfilesdir}/%{name}-milter.conf
install -m 644 milters/pagure_milter.service \
    $RPM_BUILD_ROOT/%{_unitdir}/pagure_milter.service
install -m 644 milters/comment_email_milter.py \
    $RPM_BUILD_ROOT/%{_datadir}/pagure/comment_email_milter.py

# Install the eventsource
mkdir -p $RPM_BUILD_ROOT/%{_libexecdir}/pagure-ev
install -m 755 ev-server/pagure-stream-server.py \
    $RPM_BUILD_ROOT/%{_libexecdir}/pagure-ev/pagure-stream-server.py
install -m 644 ev-server/pagure_ev.service \
    $RPM_BUILD_ROOT/%{_unitdir}/pagure_ev.service


%post milters
%systemd_post pagure_milter.service
%post ev
%systemd_post pagure_ev.service

%preun milters
%systemd_preun pagure_milter.service
%preun ev
%systemd_preun pagure_ev.service

%postun milters
%systemd_postun_with_restart pagure_milter.service
%postun ev
%systemd_postun_with_restart pagure_ev.service


%files
%doc README.rst
%license LICENSE
%config(noreplace) %{_sysconfdir}/httpd/conf.d/pagure.conf
%config(noreplace) %{_sysconfdir}/pagure/pagure.cfg
%config(noreplace) %{_sysconfdir}/pagure/alembic.ini
%dir %{_sysconfdir}/pagure/
%dir %{_datadir}/pagure/
%{_datadir}/pagure/pagure*
%{_datadir}/pagure/alembic/
%{python_sitelib}/pagure/
%{python_sitelib}/pagure*.egg-info


%files milters
%license LICENSE
%attr(755,postfix,postfix) %dir %{_localstatedir}/run/pagure
%dir %{_datadir}/pagure/
%{_tmpfilesdir}/%{name}-milter.conf
%{_unitdir}/pagure_milter.service
%{_datadir}/pagure/comment_email_milter.py*


%files ev
%license LICENSE
%{_libexecdir}/pagure-ev/
%{_unitdir}/pagure_ev.service


%changelog
* Tue Sep 08 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.24-1
- Update to 0.1.24
- Fix changelog to add the -release
- Block the <img> tag on titles
- Better fedmsg notifications (for example for new branches or rebase)
- Support uploading multiple files at once
- Add a load_from_disk utility script to the sources
- Fix indentation to the right on very long pull-request

* Sun Aug 30 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.23-1
- Update to 0.1.23
- Return a 404 error if we can't find the doc repo asked
- Fix for #106 Allow setting the default branch of the git repo and in the UI
  (Ghost-script)
- Improve unit-tests suite
- Add a global boolean to disable entirely tickets on all projects of a pagure
  instance (with no way to re-set them per project)
- Do display uploading a tarball if it is not entirely configured
- Ensure we do not offer to reply by email if the milter is not set up
- Ensure there is no new line character on the msg-id and improve logging in the
  milter
- Add a configuration key to globally disable creating projects
- Add a configuration key to globally disable deleting projects
- Add the possibility to search projects/users
- Drop links to the individual commits in a remote pull-request
- Input that are cleaned via the noJS filter are safe to be displayed (avoid
  double HTML escaping)
- When writing the authorized_key file, encode the data in UTF-8
- Makes page title easier to find in multi-tab cases (dhrish20)
- Fix authorized_keys file creation (Patrick Uiterwijk)
- Honor also symlinked README's in repo overview (Jan Pakorný)
- Fix the patch generation for remote PR
- Fix showing the comment's preview on the pull-request page
- Fix bug in checking if a PR can be merged

* Fri Aug 07 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.22-1
- Update to 0.1.22
- Adjust the README to the current state of pagure
- Rework how we integrate our custom tags into markdown to avoid the infinite
  loop we run into once in a while

* Wed Aug 05 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.21-1
- Update to 0.1.21
- Make SSH protocol explicit for SSH URLs (Till Maas)
- Adjust the documentation (layout and content)
- Rework the doc server to allow showing html files directly
- Fix installing the pagure hook correctly (tickets and requests)
- Give proper attribution to the pagure logo to Micah Deen in the documentation
- Increase pull request text field lengths to 80 (Till Maas)
- Fix who can open a remote PR and the check that the repo allows PR
- If there is no commit and no content, it means we didn't find the file: 404

* Wed Jul 29 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.20-1
- Update to 0.1.20
- Include the tags in the JSON representation of a project
- Add the ability to open a pull-request from a git repo not hosted on pagure
- Fix pagination when browsing the list of commits
- Fix the fork button when viewing the Settings of a project
- Adjust the example apache configuration file
- Add a favicon with pagure's logo
- Fix asynchronous commentting on pull-requests
- Start working on some documentation on how to install pagure
- Do no flash messages when a comment is submitted via javascript (ie: async)
- Do not blink the tittle of the page if the page is already on focus
- Retrieve ssh key from FAS and set it up in pagure if none is currently set-up
- Fix anchors for comments on the pull-request pages
- Fix checking the merge status of a PR when user is not logged in

* Mon Jul 20 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.19-1
- Update to 0.1.19
- Prettify the JSON stored in the git for tickets/requests... (Simo Sorce)
- Use the project name as subject tag in the notifications sent (Simo Sorce)
- Add an X-pagure header with either the pagure instance or the project name
- Reset the merge status of all the open PR when one is merged
- Add a second server listing the number of connections opened on the first
  eventsource server
- Log the info instead of printing them in the eventsource server
- Split the documentation to a different wsgi application to avoid any risk of
  cross-site forgery
- Fix the JS logic when adding a tag or a dependency to avoid having duplicates
  in the input field
- Allow deleting a git branch of a project via the UI
- Include the font-awesome in the source rather than relying on an external cdn
- Do not try to connect to the eventsource server if we're not viewing a
  pull-request
- Fix showing the first comment made on a PR via the eventsource server
- Fix showing the git URLs in the doc server
- Much better API documentation (Lei Yang)
- Handle showing closed PR that were not merged
- Fix refreshing the UI of private tickets via the eventsource (making calls to
  the API to get the info while only getting what changed via the SSE)
- Fix the anchor links in the API documentation
- Blink the tab upon changes in the page
- Ensure we close both SSE server when stopping pagure_ev
- Let the HTML form trigger if we did not connect to the EV server successfully
- The admins of a repo are anyone with commit access to the repo, directly or
  via a group
- Order the project by names in the front page (instead of creation date)
- Add the ability to tag a project
- Fix the fedmsg_hook when there are only deletions or only additions
- Add a new API endpoint allowing to search projects (by name, author, tag ...)
- Make pagure compatible with pygit 0.22.0
- Adjust unit-tests for all these changes

* Mon Jun 22 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.18-1
- Update to 0.1.18
- Fix the eventsource server for CORS
- Fix showing/checking the merge status of a PR

* Mon Jun 22 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.17-1
- Update to 0.1.17
- Fix for missing docs of API issue add comment (Kunaal Jain)
- Fix the systemd init file
- Be more careful about the URL specified, it may be of the wrong format in the
  eventsource server
- Allow configuring the port where the event source server runs in the
  configuration
- Fix bug in filter_img_src introduced with its moved to the backend library

* Thu Jun 18 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.16-1
- Update to 0.1.16
- Clone all the remote branches when cloning a project
- Allow online editing to a new branch or any of the existing ones
- Allow the <hr /> html tags in markdown
- Add eventsource support in the ticket and pull-request pages

* Tue Jun 16 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.15-1
- Update 0.1.15
- Use a monospace font for the commit hash
- Remove duplicated "commit" id in the HTML (causing a graphical bug in the
  commit page)
- Secure the input using the no_js filter instead of relying on a restrictive
  regex for PR and issue titles
- Support ',' in the tags field since it's required to specify multiple tags

* Fri Jun 12 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.14-1
- Update to 0.1.14
- Remove all new lines characters from the ssh key uploaded
- Adjust the URL in the footer to point to https://pagure.io/pagure
- Fix displaying the time of a comment
- Forbid the use of spaces in group name
- Do not get the list of not-merged commits if there is only 1 branch in the
  repo
- Display the error message if pagure.lib.add_group raises an exception
- Add a new setting enforcing that all commits in a PR are signed-off by their
  author
- Enforce that all commits are signed-off by the author if the repo is
  configured for this
- Also check for the signed-off status before merging a pull-request
- Adjust online-editing to allow specifying which email address to use in the
  commit
- Add an avatar_email field to projects
- Change the PullRequest's status from a Boolean to a Text restricted at the DB
  level (Allows to distinguish Open/Merged/Closed)
- Show in the pull-request view who merged the pull-request
- Specify who closed the pull-request in the API output
- Catch GitError when merging and checking merge status of a PR
- Hide the form to create pull-requests if the user is not an admin of the repo
- Replace the Pull-Request button by a Compare button if the user it not a repo
  admin
- Set the title of the tab as URL hash to allow directly linking to it
- Adjust the API to be able to distinguish API authentication and UI
  authentication
- Fix API documentation to create new issues
- Drop the status from the requirements to open a new issue via the API
- Expand the list of blacklisted project names
- Have the code tags behave like pre tags (html tags)
- Allow project to specify an URL and display it on their page
- Strip the ssh keys when writing them to the authorized_keys file
- Disable javascript in all the markdown fields
- Validate early the input submitted in the forms (using more or less strict
  regex)
- If the session timed-out, redirect to the setting page after authentication
  and inform the user that the action was canceled
- Catch PagureException when adjusting the project's settings
- Redirect the /api endpoint to the api documentation place
- Fix how is retrieved the list of emails to send the notification to
- Sanitize the html using bleach to avoid potential XSS exploit
- Do not give READ access to everyone on the tickets and pull-requests repos to
  avoid leaking private tickets
- Adjust the unit-tests for all these changes

* Fri Jun 05 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.13-1
- Update to 0.1.13
- Do not show the edit button if the user cannot edit the file
- Fix who is allowed to drop comments
- Fix showing the drop comment button on issue comments
- Fix creating the pull-request for fast people like @lmacken
- Display the target of the PR as well as the origin in the PR page
- Limit the size of the lists on the front page

* Fri Jun 05 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.12-1
- Update to 0.1.12
- Fix the URL where the sources upload are done
- Upload the new sources under the project's name (be it project or
  user/project)

* Fri Jun 05 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.11-1
- Update to 0.1.11
- Another fix for the fedmsg_hook git hook
- Adjust how we display the README page to avoid XSS there as well
- Add the possibility to disable plugins via the configuration file
- Present the git tags in the UI
- As soon as the API user present a token, validate it or not, even if the
  endpoint would work without token
- Integrate alembic for DB scheme migration
- Cache the PR's merge status into the DB
- Only people with access to the project can add/remove API token
- Make the unit-tests run on bare repos as in prod
- First stab at online editing
- Simplify the API output to drop the project's settings where it doesn't
  make sense
- First stag at allowing upstream to upload their release to pagure
- Fix merging a PR into another branch than master
- Reduce code duplication when checking if a PR can be merged or merging it
- Code style clean-up

* Tue Jun 02 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.10-1
- Update to 0.1.10
- Add support for URL ending with a trailing slash where it makes sense (so
  we support both with and without trailing slash)
- Fix XSS issue by disabling <script> tags in the documentation pages
- Expend the unit-test suite for the api.project controller
- Add the possibility for 3rd party apps to 'flag' a pull-request with for
  example the result of a build
- Handle the situation where there are multiple branch of the same name in
  the same repo
- Fix the color of the link on hover when displayed within a tab view
  (for example in the PR pages)
- Redirect the user to the pull-request created after its the creation
- Do not leak emails over fedmsg
- Fix the fedmsg_hook plugin

* Fri May 29 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.9-1
- Update to 0.1.9
- Initial API work
- Document the initial API
- Fix the CSS to present the links correctly
- Add new API endpoint to list the git tags of a project
- Ensure the DB is updated regarding the start and stop commits before merging

* Wed May 27 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.8-1
- Update 0.1.8
- Add the possibility to do Asynchronous in-line comment posting
  (Patrick Uiterwijk)
- Handle the situation where the branch asked is not found in the git repo
- Handle the situation where we cannot find a desired commit
- Do not display a value in the settings page if there are none
- Rework the pull-request view to move the list of commits into a tab
- Make email sending optional (Patrick Uiterwijk)

* Fri May 22 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.7-1
- Update to 0.1.7
- Drop debugging code on the milter and the hooks
- Adjust the search_issues method to support filter for some tags, excluding
  some others (for example ?tags=easfix&tags=!0.2)
- Support groups when searching an user's projects (ie: finding the projects an
  user has access to via the group their are in)
- Do not load the git repo from the FS when loading an user's page
- Present and document the SSH keys in a dedicated documentation page

* Wed May 20 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.6-1
- Update to 0.1.6
- Fix sending notification emails to multiple users, avoid sending private into
  to all of them

* Tue May 19 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.5-1
- Update to 0.1.5
- Bug fix on the milter and the internal API endpoint

* Tue May 19 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.4-1
- Update to 0.1.4
- Fix loading requests and tickets from git (allows syncing projects between
  pagure instances)
- Add to the template .wsgi file a way to re-locate the tmp folder to work
  around a bug in libgit2
- Fix unit-tests suite
- Adjust the spec file to install all the files required for the milters
- Fix the `View` button on the pull-request pages

* Wed May 13 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.3-1
- Update to 0.1.3
- Add support for gitolite3
- Fix unit-tests suite to work on jenkins

* Sat May 09 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.2-2
- Fix the Requires on the milter subpackage (adding: post, preun and postun)
- Add systemd scriptlet to restart the service gracefully
- Use versioned python macro (py2)
- Ship the license in the milter subpackage as well
- Use the %%license macro

* Thu May 07 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.2-1
- Update to 0.1.2
- Fix bug in the fedmsg hook file (Thanks Zbigniew Jędrzejewski-Szmek)

* Wed May 06 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.1-1
- Update to 0.1.1
- Port to python-munch and list it in the dependencies
- Fix exporting patch when they contain unicode characters or accent
- After creating an issue, user is brought back to the new issue page
- Fix unit-tests
- Stop the pagure hook if the user is deleting a branch (no need to run through
  all the commits of that branch)
- Fix the requirements.txt file (Sayan Chowdhury)
- Fix the tree page to show the commit sha on its proper line (Sayan Chowdhury)
- Fix typo in the form of some of the plugin (Sayan Chowdhury)
- Improve the README (Sayan Chowdhury)
- Fix highlighting the commits tab when accessing it (Sayan Chowdhury)

* Mon May 04 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1-1
- First official release: 0.1

* Thu Apr 02 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0-1.20150402
- Cut a RPM for testing on Thu Apr 2nd 2015

* Wed Oct 08 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0-1.20141008
- Initial packaging work for Fedora
