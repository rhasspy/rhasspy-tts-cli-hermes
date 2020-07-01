AC_INIT([rhasspy-tts-cli-hermes], [0.2.0], [mike@rhasspy.org])
AC_CONFIG_MACRO_DIR([m4])
PC_INIT([3.7.0])

dnl ---------------------------------------------------------------------------

AC_PREFIX_DEFAULT([$PWD/.venv])

dnl Template files to write
AC_CONFIG_FILES([Makefile rhasspy-tts-cli-hermes])

AC_CANONICAL_HOST
AC_PROG_INSTALL
AC_PROG_MKDIR_P
AC_PROG_CC
AC_PROG_CXX

dnl ---------------------------------------------------------------------------

is_virtualenv_enabled=yes

dnl An in-place install does not include Rhasspy Python modules, since they will
dnl be used directly from source.
is_in_place=no

dnl --------------
dnl Text to Speech
dnl --------------

is_nanotts_enabled=UNKNOWN
nanotts_from=prebuilt

dnl Set architectures based on host CPU
AS_CASE([$host_cpu],
    [armv6l],[
        dnl ARM 32-bit v6 (Pi 1/0)
        docker_arch=armv6
        is_nanotts_enabled=yes
    ],
    [armv7l],[
        dnl ARM 32-bit v7 (Pi 2/3/4)
        docker_arch=armv7
        is_nanotts_enabled=yes
    ],
    [aarch64],[
        dnl ARM 64-bit (Pi 3/4)
        docker_arch=arm64
        is_nanotts_enabled=yes
    ],
    [x86_64],[
        dnl x86_64 compatible
        docker_arch=amd64
        is_nanotts_enabled=yes
    ])

dnl ---------------------------------------------------------------------------

AC_ARG_ENABLE([in-place],
    AS_HELP_STRING([--enable-in-place],
        [do not install Rhasspy Python modules in virtual environment (will be used from source)]))

precompiled_binaries_enabled=yes

AC_ARG_ENABLE([precompiled-binaries],
    AS_HELP_STRING([--disable-precompiled-binaries],
        [build dependencies from source instead of downloading prebuilt binaries]))

dnl ---------------------------------------------------------------------------
dnl Python virtual environment
dnl ---------------------------------------------------------------------------

AC_ARG_ENABLE([virtualenv],
    [AS_HELP_STRING([--disable-virtualenv],
        [don't create a Python virtual environment at prefix])])

AC_ARG_VAR([VIRTUALENV_FLAGS], [flags to pass to when creating virtual environment])

dnl In-place install
AS_CASE([$enable_in_place],
    [yes],[is_in_place=yes],
    [no],[is_in_place=no])

dnl ---------------------------------------------------------------------------
dnl Text to Speech
dnl ---------------------------------------------------------------------------

AC_ARG_ENABLE([nanotts],
    AS_HELP_STRING([--disable-nanotts],
        [disable installation of nanoTTS text to speech system]))

dnl ---------------------------------------------------------------------------
dnl Summary
dnl ---------------------------------------------------------------------------

dnl Prefix is NONE for some reason instead of default value
summary_prefix=$prefix
AS_IF([test "x$summary_prefix" = xNONE], [
    summary_prefix=$PWD/.venv
])

AS_ECHO(["
configuration summary:

architecture: ${host_cpu}/${docker_arch}
prefix: ${summary_prefix}
virtualenv: ${is_virtualenv_enabled}
in-place: ${is_in_place}"])

AS_ECHO(["
text to speech:"])

AS_ECHO(["  nanoTTS: ${is_nanotts_enabled} (${nanotts_from})"])

AS_ECHO([""])

dnl ---------------------------------------------------------------------------
dnl Output
dnl ---------------------------------------------------------------------------

AC_SUBST([VIRTUALENV], [$is_virtualenv_enabled])

AC_SUBST([DOCKER_ARCH], [$docker_arch])

AC_SUBST([ENABLE_NANOTTS], [$is_nanotts_enabled])
AC_SUBST([NANOTTS_FROM], [$nanotts_from])

AC_SUBST([IN_PLACE], [$is_in_place])

AC_OUTPUT
