%global longcommit 6bb085f5704dd4c3841c79504f2aed2228e6d76a
%global shortcommit %(echo %{longcommit}|cut -c1-8)
%global modified %(echo %{longcommit}-|cut -f2 -d-)
%global github_owner Clusterlabs
%global buildnum 1
%global watchdog_timeout_default 5
%global sync_resource_startup_sysconfig ""

%bcond_without sync_resource_startup_default

Name:           sbd
Summary:        Storage-based death
License:        GPLv2 and MIT
Group:          System Environment/Daemons
Version:        1.5.1
Release:        %{buildnum}
Url:            https://github.com/%{github_owner}/%{name}
Source0:        https://github.com/%{github_owner}/%{name}/archive/%{longcommit}/%{name}-%{longcommit}.tar.gz
Patch0:         0001-Fix-the-problem-of-service-error-when-uninstalling.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libuuid-devel
BuildRequires:  glib2-devel
BuildRequires:  libaio-devel
BuildRequires:  corosynclib-devel
BuildRequires:  pacemaker-libs-devel > 1.1.12
BuildRequires:  libtool
BuildRequires:  libuuid-devel
BuildRequires:  libxml2-devel
BuildRequires:  pkgconfig
BuildRequires:  systemd
BuildRequires:  make
Conflicts:      fence-agents-sbd < 4.2.1
Conflicts:      pacemaker-libs < 2.0.5

ExclusiveArch: x86_64 aarch64

%if %{defined systemd_requires}
%systemd_requires
%endif

%description
This package contains the storage-based death functionality.
Available rpmbuild rebuild options:
  --with(out) : sync_resource_startup_default

%package 	tests
Summary:        Storage-based death environment for regression tests
License:        GPLv2 and MIT
Group:          System Environment/Daemons

%description tests
This package provides an environment + testscripts for
regression-testing sbd.

%prep
%autosetup -p1 -n %{name}-%{longcommit}

%build
./autogen.sh
export CFLAGS="$RPM_OPT_FLAGS -Wall -Werror"
%configure --with-watchdog-timeout-default=%{watchdog_timeout_default} \
           --with-sync-resource-startup-default=%{?with_sync_resource_startup_default:yes}%{!?with_sync_resource_startup_default:no} \
           --with-sync-resource-startup-sysconfig=%{sync_resource_startup_sysconfig} \
           --with-runstatedir=%{_rundir}
make %{?_smp_mflags}


%install
make DESTDIR=$RPM_BUILD_ROOT LIBDIR=%{_libdir} install
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/stonith
install -D -m 0755 tests/regressions.sh $RPM_BUILD_ROOT/usr/share/sbd/regressions.sh
%if %{defined _unitdir}
install -D -m 0644 src/sbd.service $RPM_BUILD_ROOT/%{_unitdir}/sbd.service
install -D -m 0644 src/sbd_remote.service $RPM_BUILD_ROOT/%{_unitdir}/sbd_remote.service
%endif

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
install -m 644 src/sbd.sysconfig ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/sbd

# Don't package static libs
find %{buildroot} -name '*.a' -type f -print0 | xargs -0 rm -f
find %{buildroot} -name '*.la' -type f -print0 | xargs -0 rm -f


%clean
rm -rf %{buildroot}

%if %{defined _unitdir}
%post
%systemd_post sbd.service
%systemd_post sbd_remote.service
if [ $1 -ne 1 ] ; then
	if systemctl --quiet is-enabled sbd.service 2>/dev/null
	then
		systemctl --quiet reenable sbd.service 2>/dev/null || :
	fi
	if systemctl --quiet is-enabled sbd_remote.service 2>/dev/null
	then
		systemctl --quiet reenable sbd_remote.service 2>/dev/null || :
	fi
fi

%preun
%systemd_preun sbd.service
%systemd_preun sbd_remote.service

%postun
%systemd_postun sbd.service
%systemd_postun sbd_remote.service
%endif

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/sysconfig/sbd
%{_sbindir}/sbd
%{_datadir}/sbd
%{_datadir}/pkgconfig/sbd.pc
%exclude %{_datadir}/sbd/regressions.sh
%doc %{_mandir}/man8/sbd*
%if %{defined _unitdir}
%{_unitdir}/sbd.service
%{_unitdir}/sbd_remote.service
%endif
%doc COPYING

%files tests
%defattr(-,root,root)
%dir %{_datadir}/sbd
%{_datadir}/sbd/regressions.sh
%{_libdir}/libsbdtestbed*

%changelog
* Mon Jul 25 2022 liupei <liupei@kylinos.cn> - 1.5.1-1
- update to 1.5.1

* Mon Mar 28 2022 jiangxinyu <jiangxinyu@kylinos.cn> - 1.4.0-17
- Fix the problem of service error when uninstalling

* Thur Dec 16 2021 liqiuyu <liqiuyu@kylinos.cn> - 1.4.0-16
- Remove the release suffix

* Fri Oct 30 2020 jiangxinyu <jiangxinyu@kylinos.cn> - 1.4.0-15
- Init sbd project

