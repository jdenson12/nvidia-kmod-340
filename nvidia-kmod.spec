# Define the kmod package name here.
%global	kmod_name nvidia

# If kversion isn't defined on the rpmbuild line, define it here. For Fedora,
# kversion needs always to be defined as there is no kABI support.

# RHEL 6.8
%if 0%{?rhel} == 6
%{!?kversion: %global kversion 2.6.32-642.el6.%{_target_cpu}}
%endif

# RHEL 7.2
%if 0%{?rhel} == 7
%{!?kversion: %global kversion 3.10.0-327.el7.%{_target_cpu}}
%endif

Name:           %{kmod_name}-kmod
Version:        340.101
Release:        1%{?dist}
Summary:        NVIDIA display driver kernel module
Epoch:          2
License:        NVIDIA License
URL:            http://www.nvidia.com/
ExclusiveArch:  %{ix86} x86_64

Source0:        %{kmod_name}-kmod-%{version}-i386.tar.xz
Source1:        %{kmod_name}-kmod-%{version}-x86_64.tar.xz
Source10:       kmodtool-%{kmod_name}-el6.sh

BuildRequires:  redhat-rpm-config
BuildRequires:  kernel-abi-whitelists

%if 0%{?rhel} == 6
BuildRequires:  module-init-tools
%else
BuildRequires:  kmod
%endif

Conflicts:      nvidia-multi-kmod

# Magic hidden here.
%global kmodtool sh %{SOURCE10}
%{expand:%(%{kmodtool} rpmtemplate %{kmod_name} %{kversion} "" 2>/dev/null)}

# Disable building of the debug package(s).
%global	debug_package %{nil}

%description
This package provides the proprietary NVIDIA OpenGL kernel driver module.
It is built to depend upon the specific ABI provided by a range of releases of
the same variant of the Linux kernel and not on any one specific build.

%prep
%ifarch %{ix86}
%setup -q -n %{kmod_name}-kmod-%{version}-i386
%endif

%ifarch x86_64
%setup -q -T -b 1 -n %{kmod_name}-kmod-%{version}-x86_64
%endif

mv kernel/* .

echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf

%build
export SYSSRC=%{_usrsrc}/kernels/%{kversion}
export IGNORE_XEN_PRESENCE=1
export IGNORE_PREEMPT_RT_PRESENCE=1

make %{?_smp_mflags} module
cd uvm
make %{?_smp_mflags} module

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=extra/%{kmod_name}
ksrc=%{_usrsrc}/kernels/%{kversion}
make -C "${ksrc}" modules_install M=$PWD
make -C "${ksrc}" modules_install M=$PWD/uvm

install -d %{buildroot}%{_sysconfdir}/depmod.d/
install kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/
# Remove the unrequired files.
rm -f %{buildroot}/lib/modules/%{kversion}/modules.*

%changelog
* Thu Dec 15 2016 Simone Caronni <negativo17@gmail.com> - 2:340.101-1
- Update to 340.101

* Sun Oct 02 2016 Simone Caronni <negativo17@gmail.com> - 2:340.98-1
- Update to 340.98.

* Thu Jun 23 2016 Simone Caronni <negativo17@gmail.com> - 2:340.96-2
- Remove ARM (Carma, Kayla) support.

* Tue Nov 17 2015 Simone Caronni <negativo17@gmail.com> - 2:340.96-1
- Update to 340.96.

* Tue Sep 08 2015 Simone Caronni <negativo17@gmail.com> - 2:340.93-1
- Update to 340.93.

* Thu May 28 2015 Simone Caronni <negativo17@gmail.com> - 2:340.76-2
- Add kernel 4.0 patch

* Wed Jan 28 2015 Simone Caronni <negativo17@gmail.com> - 2:340.76-1
- Update to 340.76.
- Remove obsolete patch.

* Tue Jan 20 2015 Simone Caronni <negativo17@gmail.com> - 2:340.65-2
- Add patch for kernel 3.18.

* Mon Dec 08 2014 Simone Caronni <negativo17@gmail.com> - 2:340.65-1
- Update to 340.65.

* Wed Nov 05 2014 Simone Caronni <negativo17@gmail.com> - 2:340.58-1
- Update to 340.58.

* Wed Oct 01 2014 Simone Caronni <negativo17@gmail.com> - 2:340.46-1
- Update to 340.46.
- Attempt building even if Xen or RT are enabled.

* Sun Aug 17 2014 Simone Caronni <negativo17@gmail.com> - 2:340.32-1
- Update to 340.32.

* Tue Jul 08 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-1
- Update to 340.24.
- Require modinfo for building.
- Use global instead of define.
- Use default different kernel version for different RHEL releases.

* Mon Jun 09 2014 Simone Caronni <negativo17@gmail.com> - 2:340.17-1
- Update to 340.17.

* Mon Jun 02 2014 Simone Caronni <negativo17@gmail.com> - 2:337.25-1
- Update to 337.25.

* Tue May 06 2014 Simone Caronni <negativo17@gmail.com> - 2:337.19-1
- Update to 337.19.

* Tue Apr 08 2014 Simone Caronni <negativo17@gmail.com> - 2:337.12-1
- Update to 337.12.

* Tue Mar 04 2014 Simone Caronni <negativo17@gmail.com> - 2:334.21-1
- Update to 334.21, update patch.

* Tue Feb 18 2014 Simone Caronni <negativo17@gmail.com> - 2:334.16-2
- Add kernel 3.14 patch.

* Sat Feb 08 2014 Simone Caronni <negativo17@gmail.com> - 2:334.16-1
- Update to 334.16.

* Tue Jan 14 2014 Simone Caronni <negativo17@gmail.com> - 2:331.38-1
- Update to 331.38.

* Fri Dec 13 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-2
- Update required kernel version to 6.5 release.

* Thu Nov 07 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-1
- Update to 331.20.
- Removed upstreamed patch.
- Support for multiple kernels is currently disabled, as kABI symbols are not
  correctly extracted from the multiple kernel modules.

* Fri Nov 01 2013 Simone Caronni <negativo17@gmail.com> - 2:319.60-2
- Use official patch from Nvidia for 3.11+ kernels.

* Wed Oct 02 2013 Simone Caronni <negativo17@gmail.com> - 0:319.60-1
- Update to 319.60.

* Wed Aug 21 2013 Simone Caronni <negativo17@gmail.com> - 2:319.49-1
- Updated to 319.49.

* Tue Jul 02 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-2
- Add armv7hl support.
- Fix nvidia driver dependency.

* Sat Jun 29 2013 Simone Caronni <negativo17@gmail.com> - 1:319.32-1
- Updated to 319.32.

* Fri May 31 2013 Simone Caronni <negativo17@gmail.com> - 1:319.23-1
- Updated to 319.23.

* Tue May 07 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-1
- Update to 319.17; based on elrepo package.
- Bump epoch.
- Switch source to generated source.

* Sat Mar 09 2013 Philip J Perry <phil@elrepo.org> - 310.40-1.el6.elrepo
- Updated to version 310.40
