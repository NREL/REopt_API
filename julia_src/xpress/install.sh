#!/bin/bash

#
# Output to stderr
#
echoerr() {
  echo "$1" 1>&2;
  echo "$1" >> $SOURCE/error.log
}

failure()
{
  echoerr "$1"
  exit 1
}

get_parameter()
{
  VARIABLE=$1
  PROMPT=$2

  eval DEFAULT=\$$VARIABLE

  printf "$PROMPT "
  if [ "$DEFAULT" ]; then
    printf "[$DEFAULT] "
  fi
  read REPLY
  if [ "$REPLY" ]; then
    eval $VARIABLE=$REPLY
  else
    eval $VARIABLE=$DEFAULT
  fi
}

check_continue()
{
  if [ "$DISABLE_USER_PROMPT" ]; then
    return
  fi

  PROMPT=$1

  if [ "$PROMPT" ]; then
    echo $PROMPT
  fi

  R=n
  get_parameter R "Do you want to continue the installation?"
  if echo $R | grep -i n > /dev/null; then
    exit 1
  fi
}

choose_installation()
{
  PLATFORMS=`ls $SOURCE/x*.tar.gz`

  numbertgz=0;
  for g in $PLATFORMS; do
    numbertgz=`expr $numbertgz + 1`
  done

  i=1
  for f in $PLATFORMS; do
    eval PKG_$i=$f
    p=`basename $f .tar.gz | cut -f 2- -d _`


    if [ $p = linux_x86 ]; then
      plat="Linux (GLIBC 2.2) on x86"
    elif [ $p = linuxrh9_x86 ]; then
      plat="Linux (GLIBC 2.3+) on x86"
    elif [ $p = linux_ia64 ]; then
      plat="Linux (GLIBC 2.3+) on Itanium 2 (64-bit)"
    elif [ $p = linux_x86_64 ]; then
      plat="Linux (GLIBC 2.3+) on AMD64 / EM64T"
    elif [ $p = linux_openmp_x86_64 ]; then
      plat="Linux (GLIBC 2.5+ with OpenMP) on AMD64 / EM64T"
    elif [ $p = sun_sparc ]; then
      plat="Sun Solaris on SPARC"
    elif [ $p = sun_sparc64 ]; then
      plat="Sun Solaris on 64-bit SPARC"
    elif [ $p = sun_x86_64 ]; then
      plat="Sun Solaris on AMD64 / EM64T"
    elif [ $p = aix_ppc ]; then
      plat="IBM AIX on PowerPC"
    elif [ $p = aix43_rs64 ]; then
      plat="IBM AIX 4.3 on 64-bit PowerPC"
    elif [ $p = aix51_rs64 ]; then
      plat="IBM AIX 5 on 64-bit PowerPC"
    elif [ $p = hpux_pa ]; then
      plat="HP-UX on PA-RISC"
    elif [ $p = hpux_pa64 ]; then
      plat="HP-UX on 64-bit PA-RISC"
    elif [ $p = hpux_ia64 ]; then
      plat="HP-UX on Itanium 2 (64-bit)"
    elif [ $p = macos_x86_64 ]; then
      plat="MacOS on AMD64 / EM64T"
    else
      plat="Unknown platform ($p)"
    fi

    if [ $numbertgz -gt 1 ]; then
      echo "$i) $f for $plat"
    fi

    i=`expr $i + 1`
  done

  i=`expr $i - 1`

  if [ $numbertgz -gt 1 ]; then
    echo
  fi

  if [ $i = 0 ]; then
    echo "Unable to find any FICO Xpress packages in the $SOURCE directory."
    echo "Please ensure that this installer is run from the directory in which"
    echo "you extracted the FICO Xpress tar file."
    exit 1

  elif [ $i = 1 ]; then

    PKGFILE=$PKG_1

  else
    while [ "$PKGFILE" = "" ]; do
      get_parameter PNUM "Which package do you wish to install? (1 - $i)"

      if [ "$PNUM" -lt 1 ] || [ "$PNUM" -gt $i ]; then
        check_continue "Invalid option chosen."
        PNUM=
      else
        PKGFILE=`eval echo \$\{PKG_$PNUM\}`
      fi
    done
  fi

  #Add package name entered to log:
  echo "$PKGFILE" >> $SOURCE/install.log

  #Check whether we want this to be a static or distributed install:
  license_method=

  if [ "$OPT_LICENSE_TYPE" ]; then
    case $OPT_LICENSE_TYPE in
      community) license_method=community
        ;;
      static) license_method=static
        ;;
      floating-server) license_method=distributed
        ;;
      floating-client) license_method=distributed
        ;;
      \?)
        echo "Error: unknown license method specified"
        exit 1
        ;;
    esac
  else
    while [ ! "$license_method" ]; do
      Q=
      echo "Please Select Licence Type"
      echo "Community Licensing (use Xpress for free; some usage restrictions apply)"
      echo "Static Licensing ('Node-locked' or 'USB dongle')"
      echo "Floating licensing (separate license server)"
      get_parameter Q "Do you want to use [c]ommunity, [s]tatic or [f]loating licensing?"

      if echo $Q | grep -i c > /dev/null; then
        license_method=community
      elif echo $Q | grep -i s > /dev/null; then
        license_method=static
      elif echo $Q | grep -i f > /dev/null; then
        license_method=distributed
      elif echo $Q | grep -i q > /dev/null; then
        exit 1
      else
        echo "Could not understand response, enter C, S or D or quit"
        echo
      fi
    done
  fi

  #Add license method entered to log:
  echo "$license_method" >> $SOURCE/install.log

  echo

  if [ $license_method = "distributed" ]; then
    INSTALL_TYPE=

    if [ "$OPT_LICENSE_TYPE" ]; then
      case $OPT_LICENSE_TYPE in
        floating-server) INSTALL_TYPE=distrib_server
          ;;
        floating-client) INSTALL_TYPE=distrib_client
          ;;
        \?)
          echo "Error: unknown install type specified"
          exit 1
          ;;
      esac
    else
      while [ ! "$INSTALL_TYPE" ]; do
        R=
        get_parameter R "Is this a [s]erver or a [c]lient installation? "

        if echo $R | grep -i c > /dev/null; then
          INSTALL_TYPE=distrib_client
        elif echo $R | grep -i s > /dev/null; then
          INSTALL_TYPE=distrib_server
        elif echo $R | grep -i q > /dev/null; then
          exit 1
        else
          echo "Could not understand response, enter C or S or quit"
          echo
        fi
      done
    fi

    #Add distributed install type to log:
    echo "$INSTALL_TYPE" >> $SOURCE/install.log

  else
    INSTALL_TYPE=xpress_package
    if [ $license_method = "community" ]; then
      USE_COMMUNITY_LIC=1
    fi
  fi

  echo
}

choose_location()
{
  if [ "$OPT_INSTALL_PATH" ]; then
    XPRESSDIR=$OPT_INSTALL_PATH
    return
  fi

  if [ "$INSTALL_TYPE" = "distrib_client" ]; then
    get_parameter XPRESSDIR "Where do you want to install the client?"

  elif [ "$INSTALL_TYPE" = "xpress_package" ]; then
    get_parameter XPRESSDIR "Where do you want to install the Xpress-MP?"

  elif [ "$INSTALL_TYPE" = "distrib_server" ]; then
    get_parameter XPRESSDIR "Where do you want to install the license server?"
  fi

  echo
}

get_licfile_location()
{
  LICPATH=

  if [ "$OPT_PATH_XPAUTH" ]; then
    LICPATH=$OPT_PATH_XPAUTH

    if [ -d "$LICPATH" ]; then
      LICPATH=$LICPATH/xpauth.xpr
    fi

    if [ ! -f "$LICPATH" ]; then
      failure "Could not find license file in path $LICPATH"
    fi
  else
    while [ ! "$LICPATH" ]; do
      get_parameter LICPATH "Please enter the location of your license file:"

      if [ -d "$LICPATH" ]; then
        LICPATH=$LICPATH/xpauth.xpr
      fi

      if [ ! -f "$LICPATH" ]; then
        check_continue "Could not find license file $LICPATH"
        LICPATH=
      fi
    done
  fi
}

check_license_file()
{
  if [ "$USE_COMMUNITY_LIC" ]; then
    CORRECT_LICENSE=1
  else

    CORRECT_LICENSE=
    LICPATH=

    R=y

    if [ ! "$OPT_PATH_XPAUTH" ]; then
      R=firsttime
      while [ -z "`echo $R | sed -n /^[YyNn]/p`" ]; do
        if [ "$R" != "firsttime" ]; then
          echo "Could not understand response, enter Y or N or quit"
          echo
        fi
        R=y
        get_parameter R "Have you received an xpauth.xpr license file from Xpress Support?"
      done
    fi

    # do they have the right kind of license file for this install?
    if echo $R | grep -i y > /dev/null; then
      get_licfile_location
      CORRECT_LICENSE=1
    else
      if [ "$INSTALL_TYPE" = "distrib_server" ]; then
        NEED_DISTRIB_LIC=1
      else
        NEED_PC_LIC=1
      fi
    fi

    # if they have the right license, ask if they want it copied into the installation dir
    if [ "$CORRECT_LICENSE" ]; then
      R=y
      if [ ! "$OPT_PATH_XPAUTH" ]; then
        get_parameter R "Do you want to copy your license file into $XPRESSDIR/bin?"
      fi
  
      if echo $R | grep -i y > /dev/null; then
        COPY_LICENSE=1
      elif echo $R | grep -i n > /dev/null; then
        COPY_LICENSE=
      fi

    # if they don't have the right license, help them apply for one
    elif [ "$NEED_DISTRIB_LIC" -o "$NEED_PC_LIC" ]; then
      if [ "$NEED_DISTRIB_LIC" ]; then
        $SOURCE/utils/lmhostid 2>>$SOURCE/error.log >hostid.log
      elif [ "$NEED_PC_LIC" ]; then
        $SOURCE/utils/xphostid 2>>$SOURCE/error.log  >hostid.log
      fi

      if [ -s hostid.log ]; then
        echo "To order a license file, please email support@fico.com,"
        echo "quoting the following:"
        cat hostid.log
      else
        echo "To order a license file, please follow the instructions at:"
        echo "  http://www.fico.com/xpresslicense"
      fi

      check_continue
    fi
    echo
  fi
}

check_include_in_bashrc()
{
  if [ "$INSTALL_TYPE" = "distrib_server" ]; then
    INCLUDE_IN_BASHRC=
  elif [ "$OPT_INCLUDE_IN_BASHRC" = "yes" ]; then
    INCLUDE_IN_BASHRC=1
  elif [ "$DISABLE_USER_PROMPT" ]; then
    INCLUDE_IN_BASHRC=
  else
    HAS_SET_INCLUDE_IN_BASHRC=
    while [ -z "$HAS_SET_INCLUDE_IN_BASHRC" ]; do
      R=y
      get_parameter R "Do you want to add Xpress installation paths to .bashrc file?"
      if echo $R | grep -i y > /dev/null; then
        INCLUDE_IN_BASHRC=1
        HAS_SET_INCLUDE_IN_BASHRC=1
      elif echo $R | grep -i n > /dev/null; then
        INCLUDE_IN_BASHRC=
        HAS_SET_INCLUDE_IN_BASHRC=1
      else
        echo "Could not understand response, enter Y or N or quit"
        echo
      fi
    done
  fi
}


check_permissions()
{
  if [ ! -d "$XPRESSDIR" ]; then
    mkdir -p $XPRESSDIR 2>>$SOURCE/error.log || failure "Can't create $XPRESSDIR: permission denied"
  else
    # just check we have write-access
    touch $XPRESSDIR 2>>$SOURCE/error.log || failure "Can't modify $XPRESSDIR: permission denied"
  fi
}

choose_kalis()
{
  if [ "$OPT_KALIS_SUPPORT" ]; then
    KALIS_INSTALL=$OPT_KALIS_SUPPORT
    if [ "$OPT_KALIS_SUPPORT" = "yes" ]; then
      echo "Xpress-Kalis constraints programming engine for Mosel will be installed"
    else
      echo "Skipping installation of Xpress-Kalis constraints programming engine for Mosel"
    fi
    return
  fi

  R=y
  S=y
  get_parameter R "Do you wish to install the Xpress-Kalis constraints programming engine for Mosel?"
  if echo $R | grep -i y > /dev/null; then
    #Display license and check for acceptance:
    less -E -m -Pm"Scroll using SPACE, ENTER or the arrow keys. Press q to quit." kalis_license.txt 2>/dev/null
    get_parameter S "Do you accept the terms of the license agreement?"
    if echo $S | grep -i y > /dev/null; then
      KALIS_INSTALL=yes
    elif echo $S | grep -i n > /dev/null; then
      KALIS_INSTALL=no
    fi
  elif echo $R | grep -i n > /dev/null; then
    KALIS_INSTALL=no
  fi
}

extract_tarfile()
{
  # move possible conflict files
  if [ "$INSTALL_TYPE" = "distrib_client" ]; then
    mkdir $XPRESSDIR/lib/backup 2>/dev/null
    mv $XPRESSDIR/lib/libxprl* $XPRESSDIR/lib/backup 2>/dev/null
  fi

  echo "Extracting package $PKGFILE..."

  # check if this command prints anything to standard error
  if [ "$INSTALL_TYPE" = "distrib_server" ]; then
    mkdir $XPRESSDIR/bin
    if [ "`( gzip -d -c < $PKGFILE | ( cd $XPRESSDIR; tar oxf - bin/runlmgr bin/xpserver bin/xplicstat bin/xphostid ) ) 2>&1 | tee -a $SOURCE/error.log`" ]; then
      failure "Errors while extracting the package - your download may be corrupted."
    fi
  else
    if [ "`( gzip -d -c < $PKGFILE | ( cd $XPRESSDIR; tar oxf - ) ) 2>&1 | tee -a $SOURCE/error.log`" ]; then
      failure "Errors while extracting the package - your download may be corrupted."
    fi
  fi

  # Now remove the Kalis files if not required:
  if [ "$KALIS_INSTALL" = "no" ]; then
    rm -f $XPRESSDIR/dso/kalis.dso 2>/dev/null
    rm -rf $XPRESSDIR/docs/kalis 2>/dev/null
    rm -rf $XPRESSDIR/examples/kalis 2>/dev/null
    rm -f $XPRESSDIR/readme_kalis.html 2>/dev/null
    rm -f $XPRESSDIR/kalis_license.txt 2>/dev/null
  fi
  
  # Now remove any old files that have moved to new locations
  rm -f $XPRESSDIR/do/dso/mosjvm.dso 2>/dev/null
  rm -f $XPRESSDIR/do/lib/mosjvm.jar 2>/dev/null

  echo "Package extracted successfully."
  echo
}

# If /usr/lib or /usr/lib64 already contains a libssh/libcrypto, delete the ones we bundle
remove_duplicate_bundled_libs()
{
  # libssh
  if [ `ls /usr/lib*/libssh.so.4 2&>/dev/null | wc -l` -ne 0 ]; then
    echo "Using system libssh"
    rm -f $XPRESSDIR/lib/libssh*
  fi
  # libcrypto
  if [ `ls /usr/lib*/libcrypto.so.1.0.0 2&>/dev/null | wc -l` -ne 0 ]; then
    echo "Using system libcrypto"
    rm -f $XPRESSDIR/lib/libcrypto*
  fi
}

generate_client_lic()
{
  # Find out what the server is
  SERVERNAME=
  if [ "$OPT_LICENSE_SERVER" ]; then
    SERVERNAME=$OPT_LICENSE_SERVER
  else
    get_parameter SERVERNAME "Enter the name of your license server:"
  fi

  if [ ! "$SERVERNAME" ]; then
    echo "When you know the name of your server, edit $XPRESSDIR/bin/xpauth.xpr"
    echo "and change server_name in \"use_server server=server_name\"."
    SERVERNAME=server_name
  fi

  # Add server name entered to log:
  echo "$SERVERNAME" >> $SOURCE/install.log

  # Check for prior existence of the server line:
  # Otherwise just write the file
  if [ ! "$LICPATH" ]; then
    LICPATH=$XPRESSDIR/bin/xpauth.xpr
  fi

  if grep -i use_server $LICPATH > /dev/null; then
    echo "use_server server=\"$SERVERNAME\"" > $XPRESSDIR/bin/xpauth.xpr
    sed $LICPATH -e /use_server/d >> $XPRESSDIR/bin/xpauth.xpr
  else
    echo "use_server server=\"$SERVERNAME\"" > $XPRESSDIR/bin/xpauth.xpr
  fi

  echo

  # Copy the altered version back:
  COPY_BACK=
  if [ ! "$DISABLE_USER_PROMPT" ]; then
    get_parameter COPY_BACK "Do you want to overwrite your original xpauth.xpr with the client xpauth.xpr? [y]"
  fi

  if [ ! "$COPY_BACK" ]; then
    cp $XPRESSDIR/bin/xpauth.xpr $LICPATH
  elif echo $COPY_BACK | grep -i y > /dev/null; then
    echo "Overwriting original xpauth.xpr."
    cp $XPRESSDIR/bin/xpauth.xpr $LICPATH
  elif echo $COPY_BACK | grep -i n > /dev/null; then
    echo "Leaving original xpauth.xpr unaltered."
  else
    echo "Unrecognised option, not copying over original."
  fi
}

customize_varscripts()
{
  if [ "$INSTALL_TYPE" = "distrib_client" ]; then
    generate_client_lic
    XPRESS_VAR=$XPRESSDIR/bin
    CORRECT_LICENSE=1

  elif [ "$CORRECT_LICENSE" ]; then
    if [ "$USE_COMMUNITY_LIC" ]; then
      # copy community license into directory
      cp $XPRESSDIR/bin/community-xpauth.xpr $XPRESSDIR/bin/xpauth.xpr
      XPRESS_VAR=$XPRESSDIR/bin
    elif [ "$COPY_LICENSE" ]; then
      # copy license file into new directory
      cp $LICPATH $XPRESSDIR/bin/xpauth.xpr
      chmod 644 $XPRESSDIR/bin/xpauth.xpr 2&>/dev/null
      XPRESS_VAR=$XPRESSDIR/bin
    else
      XPRESS_VAR=$LICPATH
    fi
  else
    # Set XPRESS_VAR to expected default location for when user copies license there
    XPRESS_VAR=$XPRESSDIR/bin
  fi

  cat > $XPRESSDIR/bin/xpvars.sh <<EOF
XPRESSDIR=$XPRESSDIR
XPRESS=$XPRESS_VAR
LD_LIBRARY_PATH=\${XPRESSDIR}/lib:\${LD_LIBRARY_PATH}
DYLD_LIBRARY_PATH=\${XPRESSDIR}/lib:\${DYLD_LIBRARY_PATH}
SHLIB_PATH=\${XPRESSDIR}/lib:\${SHLIB_PATH}
LIBPATH=\${XPRESSDIR}/lib:\${LIBPATH}

CLASSPATH=\${XPRESSDIR}/lib/xprs.jar:\${CLASSPATH}
CLASSPATH=\${XPRESSDIR}/lib/xprb.jar:\${CLASSPATH}
CLASSPATH=\${XPRESSDIR}/lib/xprm.jar:\${CLASSPATH}
PATH=\${XPRESSDIR}/bin:\${PATH}

if [ -f "${XPRESSDIR}/bin/xpvars.local.sh" ]; then
  . ${XPRESSDIR}/bin/xpvars.local.sh
fi

export LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH
export SHLIB_PATH
export LIBPATH
export CLASSPATH
export XPRESSDIR
export XPRESS
EOF

  cat > $XPRESSDIR/bin/xpvars.csh <<EOF
setenv XPRESSDIR $XPRESSDIR
setenv XPRESS $XPRESS_VAR

if ( \$?LD_LIBRARY_PATH ) then
  setenv LD_LIBRARY_PATH \${XPRESSDIR}/lib:\${LD_LIBRARY_PATH}
else
  setenv LD_LIBRARY_PATH \${XPRESSDIR}/lib
endif

if ( \$?DYLD_LIBRARY_PATH ) then
  setenv DYLD_LIBRARY_PATH \${XPRESSDIR}/lib:\${DYLD_LIBRARY_PATH}
else
  setenv DYLD_LIBRARY_PATH \${XPRESSDIR}/lib
endif

if ( \$?SHLIB_PATH ) then
  setenv SHLIB_PATH \${XPRESSDIR}/lib:\${SHLIB_PATH}
else
  setenv SHLIB_PATH \${XPRESSDIR}/lib
endif

if ( \$?LIBPATH ) then
  setenv LIBPATH \${XPRESSDIR}/lib:\${LIBPATH}
else
  setenv LIBPATH \${XPRESSDIR}/lib
endif

if ( \$?CLASSPATH ) then
  setenv CLASSPATH \${XPRESSDIR}/lib/xprs.jar:\${XPRESSDIR}/lib/xprm.jar:\${XPRESSDIR}/lib/xprb.jar:\${CLASSPATH}
else
  setenv CLASSPATH \${XPRESSDIR}/lib/xprs.jar:\${XPRESSDIR}/lib/xprm.jar:\${XPRESSDIR}/lib/xprb.jar
endif

set path=( \${XPRESSDIR}/bin \${path} )
EOF

}

install_varscripts() {
  # Now we've created the var scripts, add them to user profile if required
  if [ "$INCLUDE_IN_BASHRC" ]; then
    if [ -e ~/.bashrc ]; then
      cp ~/.bashrc bashrc.bak
    fi
    cat >> ~/.bashrc <<EOF

# Use FICO Xpress
if [ -z "\$XPRESSDIR" -o ! -d "\$XPRESSDIR" ]; then
  . $XPRESSDIR/bin/xpvars.sh
fi

EOF
  fi
}

start_lmgrd()
{
  echo "Starting the FICO Xpress license manager:"
  echo "$XPRESSDIR/bin/xpserver -d -xpress $XPRESS_VAR -logfile /var/tmp/xpress.log"
  $XPRESSDIR/bin/xpserver -d -xpress $XPRESS_VAR -logfile /var/tmp/xpress.log
}

generate_xprmsrv_key()
{
  OLDPWD=`pwd`
  cd $XPRESSDIR/bin
  LD_LIBRARY_PATH=$XPRESSDIR/lib:$LD_LIBRARY_PATH
  DYLD_LIBRARY_PATH=$XPRESSDIR/lib:$DYLD_LIRBARY_PATH
  SHLIB_PATH=$XPRESSDIR/lib:$SHLIB_PATH
  LIBPATH=$XPRESSDIR/lib:$LIBPATH
  export LD_LIBRARY_PATH DYLD_LIBRARY_PATH SHLIB_PATH LIBPATH
  ./xprmsrv -key new
  cd "$OLDPWD"
}

print_usage()
{
  echo "Usage: $SCRIPTNAME [-h] [-l community|static|floating-server|floating-client]
       [-a xpauth_file] [-d install_directory] [-k yes|no] [-s server_name]

  where:
    -h  show this help text
    -l  set the license type: static, floating-server or floating-client
    -a  path to license file or the directory containing xpauth.xpr
    -d  target installation directory
    -k  specify whether to install the FICO Xpress-Kalis constraints programming engine for Mosel: yes or no
    -s  license server name, if license type floating-client specified
    -p  automatically include xpvars.sh in ~/.bashrc file
"
  exit 0
}

#### start of script

SCRIPTNAME=$0
SOURCE=`dirname $SCRIPTNAME`
echo > $SOURCE/error.log

while getopts "hl:a:d:k:s:p" opt; do
  case $opt in
    h) print_usage
       ;;
    l) OPT_LICENSE_TYPE=$OPTARG
       if [ `echo "$OPT_LICENSE_TYPE" | egrep -c "^(community|static|floating-server|floating-client)$"` -ne 1 ]; then
         failure "Invalid value specified for argument -l. Expected \"community\", \"static\", \"floating-server\" or \"floating-client\""
       fi
       DISABLE_USER_PROMPT=yes
       ;;
    a) OPT_PATH_XPAUTH=$OPTARG
       DISABLE_USER_PROMPT=yes
       ;;
    d) OPT_INSTALL_PATH=$OPTARG
       DISABLE_USER_PROMPT=yes
       ;;
    k) OPT_KALIS_SUPPORT=$OPTARG
       if [ `echo "$OPT_KALIS_SUPPORT" | egrep -c "^(yes|no)$"` -ne 1 ]; then
         failure "Invalid value specified for argument -k. Expected \"yes\" or \"no\""
       fi
       DISABLE_USER_PROMPT=yes
       ;;
    s) OPT_LICENSE_SERVER=$OPTARG
       DISABLE_USER_PROMPT=yes
       ;;
    p) OPT_INCLUDE_IN_BASHRC=yes
       DISABLE_USER_PROMPT=yes
       ;;
    \?)
       echo "Error: could not parse command-line parameters."
       echo
       print_usage
       exit 1
       ;;
  esac
done

if [ ! "$XPRESSDIR" ]; then
  XPRESSDIR=/opt/xpressmp
fi

echo "FICO Xpress installation utility"
echo

choose_installation

choose_location

# Now check whether the user wishes to have Kalis as part of the install:
# Kalis only available on Linux x64, Mac x64 and Windows (InstallShield Win Installer).
KALIS_INSTALL=no
if [ "$INSTALL_TYPE" != "distrib_server" ]; then
  p=`basename $PKGFILE .tar.gz | cut -f 2- -d _`
  if echo $p | grep -i macos > /dev/null; then 
    choose_kalis
  elif echo $p | grep -i linux > /dev/null; then
    choose_kalis
  fi
fi

check_license_file
check_include_in_bashrc

check_permissions
extract_tarfile
remove_duplicate_bundled_libs
customize_varscripts
install_varscripts


if [ "$INSTALL_TYPE" = "distrib_server" -a "$CORRECT_LICENSE" ]; then
  start_lmgrd
fi
if [ "$INSTALL_TYPE" != "distrib_server" ]; then
  generate_xprmsrv_key
fi

# Assign non-relative paths to all Python modules if this is a MacOS install
packagename=`basename $PKGFILE .tar.gz | cut -f 2- -d _`
if [ $packagename = "macos_x86_64" ]; then
  for i in ${XPRESSDIR}/lib/xpress.*; do
    install_name_tool -change libxprs.dylib ${XPRESSDIR}/lib/libxprs.dylib $i
  done
fi

echo
echo "Installation complete!"
echo
echo "If you use a Bourne shell, set up your environment to use FICO Xpress by running:"
echo "  . $XPRESSDIR/bin/xpvars.sh"
if [ "$INCLUDE_IN_BASHRC" ]; then
  echo "(this will be done automatically when a new Bash shell is created)"
fi
echo "Or if you use a C shell, run:"
echo "  source $XPRESSDIR/bin/xpvars.csh"
echo


if [ "$NEED_PC_LIC" ]; then
  echo "When you have received your license file, set the XPRESS environment variable"
  echo "to point to it, e.g.:"
  echo "csh% setenv XPRESS /home/chris/licenses"
  echo "or:"
  echo "sh$ export XPRESS=/opt/xpressmp/bin"
  echo

elif [ "$NEED_DISTRIB_LIC" ]; then
  echo "When you have received your license file, start the license manager, e.g.:"
  echo "  xpserver -d -xpress /home/chris -logfile /var/tmp/xpress.log"
  echo
fi

echo "For more information about getting started with FICO Xpress please read"
echo "$XPRESSDIR/readme.html"
echo
