# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%define buildforkernels akmod

%global debug_package %{nil}

%global zipmodules 1

%define __spec_install_post \
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__mod_compress_install_post}

%define __mod_compress_install_post \
  if [ "%{zipmodules}" -eq "1" ] && [ $kernel_version ]; then \
    find %{buildroot}/usr/lib/modules/ -type f -name '*.ko' | xargs xz; \
  fi

%bcond_with _nv_build_module_instances

Name:           nvidia-kmod
Version:        340.102
Release:        2%{?dist}
Summary:        NVIDIA display driver kernel module
Epoch:          2
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64

Source0:        %{name}-%{version}-i386.tar.xz
Source1:        %{name}-%{version}-x86_64.tar.xz
Source11:       nvidia-kmodtool-excludekernel-filterfile

Patch0:         kernel_4.10.patch

Conflicts:      nvidia-multi-kmod

# get the needed BuildRequires (in parts depending on what we build for)
BuildRequires:  %{_bindir}/kmodtool
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} --obsolete-name nvidia-newest --obsolete-version "%{version}" %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
The NVidia %{version} display driver kernel module for kernel %{kversion}.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}
# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} --obsolete-name nvidia-newest --obsolete-version "%{version}" %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%ifarch %{ix86}
%setup -q -n %{name}-%{version}-i386
%endif

%ifarch x86_64
%setup -q -b 1 -n %{name}-%{version}-x86_64
%endif

%patch0 -p1

for kernel_version in %{?kernel_versions}; do
    mkdir _kmod_build_${kernel_version%%___*}
    cp -fr kernel/* _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
%if !0%{?_nv_build_module_instances}
    pushd _kmod_build_${kernel_version%%___*}/
        make %{?_smp_mflags} \
            IGNORE_XEN_PRESENCE=1 \
            IGNORE_PREEMPT_RT_PRESENCE=1 \
            SYSSRC="${kernel_version##*___}" \
            module
    popd
    pushd _kmod_build_${kernel_version%%___*}/uvm
        make %{?_smp_mflags} \
            IGNORE_XEN_PRESENCE=1 \
            IGNORE_PREEMPT_RT_PRESENCE=1 \
            SYSSRC="${kernel_version##*___}" \
            module
    popd
%else
    pushd _kmod_build_${kernel_version%%___*}/
        make \
            IGNORE_XEN_PRESENCE=1 \
            IGNORE_PREEMPT_RT_PRESENCE=1 \
            SYSSRC="${kernel_version##*___}" \
            NV_BUILD_MODULE_INSTANCES=%{?_nv_build_module_instances} \
            module
    popd
%endif
done

%install
for kernel_version in %{?kernel_versions}; do
    mkdir -p %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
%if !0%{?_nv_build_module_instances}
    install -p -m 0755 \
        _kmod_build_${kernel_version%%___*}/nvidia.ko \
        _kmod_build_${kernel_version%%___*}/uvm/nvidia-uvm.ko \
        %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
%else
    install -p -m 0755 _kmod_build_${kernel_version%%___*}/uvm/nvidia*.ko \
        %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
%endif
done
%{?akmod_install}

%changelog
* Mon Feb 27 2017 Simone Caronni <negativo17@gmail.com> - 2:340.102-2
- Update kernel 4.10 patch.

* Thu Feb 23 2017 Simone Caronni <negativo17@gmail.com> - 2:340.102-1
- Update to 340.102.
- Add kernel 4.10 patch.

* Mon Jan 16 2017 Simone Caronni <negativo17@gmail.com> - 2:340.101-2
- Add kernel 4.9 patch.

* Thu Dec 15 2016 Simone Caronni <negativo17@gmail.com> - 2:340.101-1
- Update to 340.101.

* Sun Oct 02 2016 Simone Caronni <negativo17@gmail.com> - 2:340.98-1
- Update to 340.98.

* Fri Jul 01 2016 Simone Caronni <negativo17@gmail.com> - 2:340.96-3
- Add kernel 4.6 patch.

* Thu Jun 23 2016 Simone Caronni <negativo17@gmail.com> - 2:340.96-2
- Compress modules with xz as all other kernel modules.
- Remove ARM (Carma, Kayla) support.

* Tue Nov 17 2015 Simone Caronni <negativo17@gmail.com> - 2:340.96-1
- Update to 340.96.

* Tue Sep 08 2015 Simone Caronni <negativo17@gmail.com> - 2:340.93-1
- Update to 340.93.

* Thu May 28 2015 Simone Caronni <negativo17@gmail.com> - 2:340.76-2
- Add kernel 4.0 patch.

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
- Attempt building not only if Xen is enabled but also if RT is.

* Sun Aug 17 2014 Simone Caronni <negativo17@gmail.com> - 2:340.32-1
- Update to 340.32.

* Tue Jul 08 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-1
- Update to 340.24.

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
- Import RPMFusion multiple kernel modules building.
- Build the UVM kernel module only if multiple kernel modules are not used.

* Thu Nov 07 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-1
- Update to 331.20.
- Removed upstreamed patch.

* Mon Nov 04 2013 Simone Caronni <negativo17@gmail.com> - 2:331.17-1
- Updated to 331.17.
- Use official patch from Nvidia for 3.11+ kernels.
- Added support for multiple kernel modules along with single one. The single
  one is loaded by default by X.org (typical desktop usage). For all other CUDA
  specific settings the separate modules can be loaded.

* Fri Oct 04 2013 Simone Caronni <negativo17@gmail.com> - 2:331.13-1
- Update to 331.13.

* Thu Sep 12 2013 Simone Caronni <negativo17@gmail.com> - 2:325.15-2
- Fix list of files copied when building.

* Mon Sep 09 2013 Simone Caronni <negativo17@gmail.com> - 2:325.15-1
- Update to 325.15.

* Wed Aug 07 2013 Simone Caronni <negativo17@gmail.com> - 2:319.49-1
- Updated to 319.49.
- Remove patch for kernel 3.10, add patch for kernel 3.11.

* Mon Jul 29 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-3
- Fix copying of files during building.
- Add patch for kernel 3.10.

* Thu Jul 04 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-2
- Update to 319.32.
- Add armv7hl support.

* Fri May 24 2013 Simone Caronni <negativo17@gmail.com> - 1:319.23-1
- Update to 319.23.

* Tue May 21 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-2
- Bump for rpmfusion.

* Thu May 02 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-1
- Update to 319.17.

* Mon Apr 22 2013 Simone Caronni <negativo17@gmail.com> - 1:319.12-2
- Updated to 319.12.
- Simplified spec file.
- Switched to generated sources.

* Thu Apr 04 2013 Nicolas Chauvet <kwizart@gmail.com> - 1:313.30-1
- Update to 313.30.
