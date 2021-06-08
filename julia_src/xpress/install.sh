#!/bin/sh

failure()
{
	echo $1 1>&2
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
    else
      plat="Unknown platform ($p)"
    fi

    if [ $numbertgz -gt 1 ]; then 
      echo "$i) $pkg for $plat"
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
  while [ ! "$license_method" ]; do 
    Q=
    get_parameter Q "Do you want to use [s]tatic (node-locked or dongle-locked) or [f]loating licensing?"

    if echo $Q | grep -i s > /dev/null; then
      license_method=static 
    elif echo $Q | grep -i f > /dev/null; then
      license_method=distributed 
    elif echo $Q | grep -i q > /dev/null; then
      exit 1
    else
      echo "Could not understand response, enter S or D or quit"
      echo
    fi
  done

  #Add license method entered to log:
  echo "$license_method" >> $SOURCE/install.log

  echo

  if [ $license_method = "distributed" ]; then
    INSTALL_TYPE=
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

    #Add distributed install type to log:
    echo "$INSTALL_TYPE" >> $SOURCE/install.log

  else
    INSTALL_TYPE=xpress_package
  fi

  echo
}

choose_location()
{
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
  while [ ! "$LICPATH" ]; do
    get_parameter LICPATH "Please enter the location of your license file:"

    if [ -d "$LICPATH" ]; then
      LICPATH=$LICPATH/xpauth.xpr
    fi

    if [ ! -f "$LICPATH" ]; then
      check_continue "Could not find $LICPATH."
      LICPATH=
    fi
  done
}

check_license_file()
{
  CORRECT_LICENSE=
  LICPATH=

  R=y
  
  get_parameter R "Have you received an xpauth.xpr license file from Xpress Support?"

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
    get_parameter R "Do you want to copy your license file into $XPRESSDIR/bin?"
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
    if [ "`( gzip -d -c < $PKGFILE | ( cd $XPRESSDIR; tar xf - bin/runlmgr bin/xpserver bin/xplicstat bin/xphostid ) ) 2>&1 | tee -a $SOURCE/error.log`" ]; then
      failure "Errors while extracting the package - your download may be corrupted."
    fi
  else
    if [ "`( gzip -d -c < $PKGFILE | ( cd $XPRESSDIR; tar xf - ) ) 2>&1 | tee -a $SOURCE/error.log`" ]; then
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

  echo "Package extracted successfully."
  echo
}

# unused
copy_files()
{
  cp -rf $SOURCE/xpressmp/* $XPRESSDIR
}

generate_client_lic()
{
  # find out what the server is
  SERVERNAME=
  get_parameter SERVERNAME "Enter the name of your license server:"
  if [ ! "$SERVERNAME" ]; then
    echo "When you know the name of your server, edit $XPRESSDIR/bin/xpauth.xpr"
    echo "and change server_name in \"use_server server=server_name\"."
    SERVERNAME=server_name
  fi

  #Add server name entered to log:
  echo "$SERVERNAME" >> $SOURCE/install.log

  #Check for prior existence of the server line:
  #Otherwise just write the file
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
  
  #Copy the altered version back:
  COPY_BACK=
  get_parameter COPY_BACK "Do you want to overwrite your original xpauth.xpr with the client xpauth.xpr? [y]"
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
    if [ "$COPY_LICENSE" ]; then
      # copy license file into new directory
      cp $LICPATH $XPRESSDIR/bin/xpauth.xpr
      XPRESS_VAR=$XPRESSDIR/bin
    else
      XPRESS_VAR=$LICPATH
    fi
  fi

  cat > $XPRESSDIR/bin/xpvars.sh <<EOF
XPRESSDIR=$XPRESSDIR
XPRESS=$XPRESS_VAR
LD_LIBRARY_PATH=\${XPRESSDIR}/lib:\${LD_LIBRARY_PATH}
DYLD_LIBRARY_PATH=\${XPRESSDIR}/lib:\${DYLD_LIBRARY_PATH}
SHLIB_PATH=\${XPRESSDIR}/lib:\${SHLIB_PATH}
LIBPATH=\${XPRESSDIR}/lib:\${LIBPATH}
PYTHONPATH=\${XPRESSDIR}/lib:\${PYTHONPATH}

CLASSPATH=\${XPRESSDIR}/lib/xprs.jar:\${CLASSPATH}
CLASSPATH=\${XPRESSDIR}/lib/xprb.jar:\${CLASSPATH}
CLASSPATH=\${XPRESSDIR}/lib/xprm.jar:\${CLASSPATH}
PATH=\${XPRESSDIR}/bin:\${PATH}

export LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH
export SHLIB_PATH
export LIBPATH
export PYTHONPATH
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
  cd $OLDPWD
}

#### start of script

SCRIPTNAME=$0
SOURCE=`dirname $SCRIPTNAME`
echo > $SOURCE/error.log

if [ ! "$XPRESSDIR" ]; then
  XPRESSDIR=/opt/xpressmp
fi

echo "FICO Xpress installation utility"
echo

choose_installation
choose_location

# Now check whether the user wishes to have Kalis as part of the install:
# Kalis only available on Linux x86, Linux x64, Solaris x64 and Windows (InstallShield Win Installer).
KALIS_INSTALL=no
if [ "$INSTALL_TYPE" != "distrib_server" ]; then
  p=`basename $PKGFILE .tar.gz | cut -f 2- -d _`
  if echo $p | grep -i sun_x86; then 
    choose_kalis
  elif echo $p | grep -i linux > /dev/null; then
    choose_kalis
  fi
fi

check_license_file

check_permissions
extract_tarfile
customize_varscripts

if [ "$INSTALL_TYPE" = "distrib_server" -a "$CORRECT_LICENSE" ]; then
  start_lmgrd
fi
if [ "$INSTALL_TYPE" != "distrib_server" ]; then
  generate_xprmsrv_key
fi

echo
echo "Installation complete!"
echo
echo "If you use a Bourne shell, set up your environment to use FICO Xpress by running:"
echo "  . $XPRESSDIR/bin/xpvars.sh"
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
