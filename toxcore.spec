%define full_name c-toxcore
%define commit 0
%if "${commit}" != "0"
%define shortcommit %(c=%{commit}; echo ${c:0:7})
%endif

Name:		toxcore
Version:	0.2.12
Release:	4%{?dist}
Summary:	All-in-one secure communication platform

License:	GPLv3
URL:		https://github.com/TokTok/%{full_name}
%if "%{commit}" == "0"
Source0:	%{url}/archive/v%{version}.tar.gz
%else
Source0:	%{url}/archive/%{commit}/%{full_name}-%{shortcommit}.tar.gz
%endif

# See https://fedoraproject.org/wiki/Changes/Remove_GCC_from_BuildRoot
BuildRequires:	gcc
BuildRequires:	gcc-c++

BuildRequires:	cmake
BuildRequires:	libvpx-devel
BuildRequires:	opus-devel
BuildRequires:	libsodium-devel
BuildRequires:	libconfig-devel
BuildRequires:	systemd

%description
With the rise of governmental monitoring programs, Tox, a FOSS initiative, aims
to be an easy to use, all-in-one communication platform that ensures their users
full privacy and secure message delivery.

%package devel
Summary:	Development files for %{name}
Requires:	%{name} = %{version}-%{release}

%description devel
Development package for %{name}

%package static
Summary:	%{name} static libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
%{name} static libraries

%package tox-bootstrapd
Summary:	Tox DHT bootstrap daemon.
Requires:	%{name} = %{version}-%{release}
%{?systemd_requires}

%description tox-bootstrapd
Tox DHT bootstrap daemon.

%prep
%if "%{commit}" == "0"
%setup -q -n %{full_name}-%{version}
%else
%setup -q -n %{full_name}-%{commit}
%endif

%build
export CFLAGS="%{optflags} -fPIC"
export CXXFLAGS="%{optflags} -fPIC"
%cmake -DSTRICT_ABI=ON -DDHT-BOOTSTRAP=OFF
%cmake_build


%install
%cmake_install
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 other/rpm/tox-bootstrapd.service %{buildroot}%{_unitdir}/tox-bootstrapd.service
install -d "%{buildroot}%{_sharedstatedir}/tox-bootstrapd"
mkdir -p %{buildroot}%{_sysconfdir}
install -m 0644 other/bootstrap_daemon/tox-bootstrapd.conf %{buildroot}%{_sysconfdir}/tox-bootstrapd.conf

%pre tox-bootstrapd
getent group tox-bootstrapd >/dev/null || groupadd -r tox-bootstrapd
getent passwd tox-bootstrapd >/dev/null || \
    useradd -r -g tox-bootstrapd -d /var/lib/tox-bootstrapd -s /sbin/nologin \
    -c "Account to run Tox's DHT bootstrap daemon" tox-bootstrapd

%post tox-bootstrapd
%systemd_post tox-bootstrapd.service

%postun tox-bootstrapd
%systemd_postun_with_restart tox-bootstrapd.service

%preun tox-bootstrapd
%systemd_preun tox-bootstrapd.service

%files
%defattr(-, root, root)
%license LICENSE
%doc README.md CHANGELOG.md
%{_libdir}/libtoxcore.so*

%files devel
%defattr(-, root, root)
%{_includedir}/tox/
%{_libdir}/pkgconfig/toxcore.pc

%files static
%defattr(-, root, root)
%{_libdir}/libtoxcore.a

%files tox-bootstrapd
%defattr(-, root, root)
%{_bindir}/tox-bootstrapd
%{_unitdir}/tox-bootstrapd.service
%{_sharedstatedir}/tox-bootstrapd
%attr(-,tox-bootstrapd,tox-bootstrapd) %{_sharedstatedir}/tox-bootstrapd/
%config(noreplace) %{_sysconfdir}/tox-bootstrapd.conf


%changelog
* Sat Nov 25 2017 SmokedCheese <root@ubuntology.ru> - 0.0.0-2
- Rewrite spec file

* Tue Mar  3 2015 Sergey 'Jin' Bostandzhyan <jin@mediatomb.cc> - 0.0.0-1
- initial package
