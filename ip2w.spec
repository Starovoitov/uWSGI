License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/6/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires:	python <= 3.0
Summary:  ""

%description
""

Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc
%define __logdir    /val/log/
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/
%define name	uwsgi_weather

%prep
echo %{buildroot}
echo %{__systemddir}
echo %{name} %{version} %{release}
touch -f %name.log
mkdir -p %{__bindir} 
cd %{__bindir}
virtualenv uwsgi_weather
pip install uwsgi

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}
%{__mkdir} -p %{buildroot}/%{__etcdir}
%{__mkdir} -p %{buildroot}/%{__logdir}
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__install} -pD -m 644 %{name}.service %{buildroot}/%{__systemddir}/%{name}.service
%{__install} -pD -m 644 %{name}.ini %{buildroot}/%{__bindir}/%{name}.ini
%{__install} -pD -m 755 %{name}.py %{buildroot}/%{__bindir}/%{name}.py
%{__install} -pD -m 644 %{name}.conf %{buildroot}/%{__etcdir}/%{name}.conf
%{__install} -pD -m 644 %{name}.log %{buildroot}/%{__logdir}/%{name}.log

%post
%systemd_post %{name}.service
systemctl daemon-reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__logdir}
%{__bindir}
%{__systemddir}
%{__bindir}/%{name}.ini
%{__bindir}/%{name}.py
%{__systemddir}/%{name}.service
%{__logdir}/%{name}.log
%{__etcdir}/%{name}.conf
