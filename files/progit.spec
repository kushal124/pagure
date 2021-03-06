%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from
%distutils.sysconfig import get_python_lib; print (get_python_lib())")}

Name:           pagure
Version:        0.0
Release:        1.20141008%{?dist}
Summary:        A git-centered forge

License:        GPLv2+
URL:            http://fedorahosted.org/pagure/
Source0:        https://fedorahosted.org/releases/p/r/pagure/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-nose

BuildRequires:  python-alembic
BuildRequires:  python-arrow
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
Requires:  python-docutils
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
Requires:  mod_wsgi

%description
Pagure is a light-weight git-centered forge based on pygit2.

Currently, Pagure offers a web-interface for git repositories, a ticket
system and possibilities to create new projects, fork existing ones and
create/merge pull-requests across or within projects.

%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

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


%files
%doc README.rst LICENSE
%config(noreplace) %{_sysconfdir}/httpd/conf.d/pagure.conf
%config(noreplace) %{_sysconfdir}/pagure/pagure.cfg
%dir %{_sysconfdir}/pagure/
%{_datadir}/pagure/
%{python_sitelib}/pagure/
%{python_sitelib}/pagure*.egg-info


%changelog
* Wed Oct 08 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0-1.20141008
- Initial packaging work for Fedora
