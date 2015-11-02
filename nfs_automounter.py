#!/usr/bin/env python3

# Distributed under MIT license 
# Copyright (c) 2013 Ville Walveranta 
# http://my.galagzee.com
# Copyright (C) 2015 David Grant
# http://www.davidgrant.ca

import configparser
import os
import subprocess
import sys

ROOT = os.path.split(os.path.abspath(__file__))[0]

# Absolute path to the configuration file 
# (if empty the default is
# 'nfs_automount.conf' in the script's directory)
CONFIG_FILE = '/etc/nfs_automount.conf'

###############################################################################


#PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/sbin:/usr/sbin:/usr/bin:/root/bin
#export PATH

# -- DATESTAMP AT RUNTIME --

DATESTAMP = subprocess.check_output(['date', '--rfc-3339=seconds']).decode()

class Mount(object):
    def __init__(self, rw, host, share, mountpoint, testfile=None):
        self.rw = rw
        self.host = host
        self.share = share
        self.mountpoint = mountpoint
        self.testfile = testfile

    def check_mounted(self):
        mounts = open('/proc/mounts').read()
        for mount in mounts.split('\n'):
            if mount.split(' ')[1] == self.mountpoint:
                return True

    def check_remote_nfs(self):
        with open(os.devnull, "w") as f:
            return subprocess.Popen(['rpcinfo', '-t', self.host, 'nfs'], stdout=f) == 0

    def __str__(self):
        return "rw=%s %s %s %s %s" % (self.rw, self.host, self.share, self.mountpoint, self.testfile if self.testfile != None else "")


class Config(object):
    def __init__(self):
        self.sec = 'global'
        if CONFIG_FILE == '':
            config_file = os.path.join(ROOT, 'nfs_automount.conf')
        else:
            config_file = CONFIG_FILE

        if os.path.isfile(config_file):
            self.config = configparser.ConfigParser()
            self.config.read_string('[%s]\n' % (self.sec,) + open(CONFIG).read())

        # Parse delimiter 
        delimiter = self.config[self.sec]['DELIMITER'].strip('"')

        # Parse mounts
        self.mounts = []
        mounts = self.config[self.sec]['MOUNTS']
        mounts = mounts.strip(' \"()')
        mounts = mounts.split()
        mounts = [mount.strip('"') for mount in mounts]
        mounts = [mount for mount in mounts if mount.find(delimiter) != -1]

        for mount in mounts:
            mount = mount.split(delimiter)
            if mount[0] == 'rw':
                rw = True
            elif mount[0] == 'ro':
                rw = False
            else:
                raise Exception('must be one of "rw" or "ro"')
            if len(mount) > 4:
                testfile = mount[4]
            else:
                testfile = None
            mount = Mount(rw, mount[1], mount[2], mount[3], testfile=testfile)
            self.mounts.append(mount)

        # Parse mount options
        mountopts = self.config[self.sec]['MOUNTOPTS']
        print(mountopts)



# -- IMPORT CONFIGURATION --

#if [ -z ${CONFIG_FILE} ] ; then
#  SCRIPT_PATH="`dirname \"$0\"`"
#  SCRIPT_PATH="`( cd \"$SCRIPT_PATH\" && pwd )`"
#  CONFIG=${SCRIPT_PATH}/nfs_automount.conf
#else
#  CONFIG=${CONFIG_FILE}
#fi

if CONFIG_FILE == '':
    CONFIG = os.path.join(ROOT, 'nfs_automount.conf')
else:
    CONFIG = CONFIG_FILE

config = Config()

#if [ -f ${CONFIG} ] ; then
#  source ${CONFIG}
#else
#  echo "nfs_automount [${DATESTAMP}]: [CRIT] Configuration file (${CONFIG}) missing; cannot continue!"
#  exit 1
#fi


#counter=0
#declare -a MOUNTDATA
#for MOUNT in ${MOUNTS[@]}; do
#  MOUNTDATA[((counter++))]=${MOUNT}
#done


# -- LOGGING --

#function log {

#  if [ ! -z "$1" ] ; then 
#    log_msg="$1"
#  else
#    log_msg="[WARN] Parameter missing (log)!"
#  fi

#  TAG=${log_msg:0:6}

#  if [ ${TAG} = "[CRIT]" ] || [ ${TAG} = "[NOTE]" ] ; then 
#    critical=true
#  else
#    critical=false
#  fi

#  DATESTAMP=`date --rfc-3339=seconds`

#  if [ "${DEBUGLOG}" = "true" ] || [ "${critical}" = "true" ] ; then
#    message=`echo "nfs_automount [${DATESTAMP}]: ${log_msg}"`

#    if [ "${LOGTYPE}" = "log" ] && [ ! -z ${LOGFILEPATH} ]; then
#      _output_type="echo"
#      if [ -f ${LOGFILEPATH} ] ; then
#        _output_type="log"
#      else
#      	 touch ${LOGFILEPATH} > /dev/null 2>&1
#         if [ -f ${LOGFILEPATH} ] ; then
#           _output_type="log"
#         fi
#      fi
#      if [ "${_output_type}" = "log" ] ; then
#        echo ${message} >> ${LOGFILEPATH}
#      else
#        echo ${message}
#      fi
#    else
#      echo ${message}
#    fi
#  fi
    
#  if [ ${TAG} = "[CRIT]" ] ; then
#    logger_msg=`echo "nfs_automount: ${log_msg}"`
#    logger ${logger_msg}
#  fi
#}


# -- CHECK & SET COMMAND LOCATIONS --

#function check_command {
#  CMD=`which $1` > /dev/null 2>&1
#  if [ $? -ne 0 ] ; then
#     log "[CRIT] Command $1 not found. Cannot continue."
#     if [ "$1" = "showmount" ] ; then
#       log "[INFO] Install nfs-common (Debian/Ubuntu), or nfs-utils (RedHat/CentOS) first!"
#     fi
#     exit 1
#  fi
#  _RET=${CMD}
#  return 0
#}


#check_command showmount; showmountcmd=${_RET}
#check_command mountpoint; mountpointcmd=${_RET}
#check_command rpcinfo; rpcinfocmd=${_RET}
#check_command grep; grepcmd=${_RET}
#check_command mount; mountcmd=${_RET}
#check_command umount; umountcmd=${_RET}
#check_command touch; touchcmd=${_RET}
#check_command rm; rmcmd=${_RET}
#check_command awk; awkcmd=${_RET}

def check_command(command):
    cmd = ['which', command]
    with open(os.devnull, "w") as f:
        ret = subprocess.call(cmd, stdout=f)
    if ret != 0:
        print("Command ", command, "not found. Cannot continue")
        sys.exit(1)

CMDS = ['showmount', 'mountpoint', 'rpcinfo', 'grep', 'mount', 'umount', 'touch', 'rm', 'awk']
for cmd in CMDS:
    check_command(cmd)


# -- OPERATIONS --

#function get_mount_dataset {
#  if [ ! -z "$1" ] ; then 
#    _mountdataset="$1"
#  else
#    log "[CRIT] Parameter missing (get_mount_dataset); process aborted!"
#    exit 1
#  fi
  
#  if [ -z ${DELIMITER} ] ; then
#    DELIMITER="|"
#  fi
  
#  _RET=(`echo ${_mountdataset//$DELIMITER/ }`)
#  if [ ! -z ${_RET[4]} ] ; then
#    _RET[4]=${_RET[3]}/${_RET[4]}
#  fi

  # import and set rw/ro
#  if [ ${_RET[0]} = "rw" ]; then
#    _RET[0]="-o rw,${MOUNTOPTS}"
#    _RET[5]="rw"
#  else
#    _RET[0]="-o ro,${MOUNTOPTS}"
#    _RET[5]="ro"
#  fi
#}

#function check_mounted {
#  if [ ! -z "$1" ] ; then
#    _localmountpoint="$1" 
#  else
#    log "[CRIT] Parameter missing (check_mounted); process aborted!"
#    exit 1
#  fi

#  if ${grepcmd} -qsE "^[^ ]+ ${_localmountpoint}" /proc/mounts; then
#    _RET=true
#  else
#    _RET=false
#  fi
#}

#function check_stale {
#  if [ ! -z "$1" ] ; then 
#    _localmountpoint="$1"
#  else
#    log "[CRIT] Parameter missing (check_stale); process aborted!"
#    exit 1
#  fi

#  if [ ! -d "${_localmountpoint}" ] ; then
#    _RET=true
#  else
#    _RET=false
#  fi
#}

#function test_remotecheckfile {
#  if [ ! -z "$1" ] ; then 
#    _remotecheckfile="$1"
#  else
#    _remotecheckfile=""
#  fi

#  if [ "${_remotecheckfile}" != "" ] ; then
#    if [ -f ${_remotecheckfile} ] ; then
#      _RET=true
#    else
#      _RET=false
#    fi
#  else
#    _RET=true
#  fi
#}

#function check_remotenfs {
#  if [ ! -z "$1" ] ; then 
#    _remotesystem="$1"
#  else
#    log "[CRIT] Parameter missing (check_remotenfs); process aborted!"
#    exit 1
#  fi

#  read -t1 < <(${rpcinfocmd} -t ${_remotesystem} nfs 2>&-)
#  if [ $? -eq 0 ]; then
#    _RET=true
#  else
#    _RET=false
#  fi
#}

#function check_remoteshare {
#  if [ ! -z "$1" ] && [ ! -z $2 ] ; then 
#    _remotesystem="$1"
#    _remoteshare="$2"
#  else
#    log "[CRIT] Parameter(s) missing (check_remoteshare); process aborted!"
#    exit 1
#  fi

#  remotesharecheck=`${showmountcmd} -e ${_remotesystem} | ${awkcmd} '{print $1}' | ${grepcmd} "${_remoteshare}"`
#  if [ "${remotesharecheck}" != "" ] ; then
#    _RET=true
#  else
#    _RET=false
#  fi
#}

#function valid_for_mount {
#  if [ ! -z "$1" ] ; then 
#    _localmountpoint="$1"
#  else
#    log "[CRIT] Parameter missing (valid_for_mount); process aborted!"
#    exit 1
#  fi

#  if [ -d "${_localmountpoint}" ] ; then
#    if ! ${mountpointcmd} -q "${_localmountpoint}" ; then
#      _RET=true
#    else
#      _RET=false
#    fi
#  else
#    _RET=false
#  fi
#}

#function test_rw {
#  if [ ! -z "$1" ] ; then 
#    _rw_testfile="$1"
#  else
#    _rw_testfile="nfs_automount_rw_test.Kk6MC2CkHoinbSE3CYqv"
#  fi

#  ${touchcmd} ${_rw_testfile} > /dev/null 2>&1
#  if [ -f ${_rw_testfile} ] ; then
#    ${rmcmd} -f ${_rw_testfile}
#    _RET=true
#  else
#    _RET=false
#  fi
#}

#function nfs_umount {
#  if [ ! -z "$1" ] ; then 
#    _localmountpoint="$1"
#  else
#    log "[CRIT] Parameter missing (nfs_umount); process aborted!"
#    exit 1
#  fi

#  check_mounted "${_localmountpoint}"
#  if ${_RET} ; then
  
#    ${umountcmd} -f -l "${_localmountpoint}"
#    check_mounted "${_localmountpoint}"
#    if ${_RET} ; then
#      _RET=false
#    else
#      _RET=true
#    fi
  
#  else
#    _RET=true
#  fi
  
#}

#function nfs_mount {
#  if [ ! -z "$1" ] && [ ! -z "$2" ] && [ ! -z "$3" ] && [ ! -z "$4" ] ; then 
#    _mountopts="$1"
#    _remotesystem="$2"
#    _remoteshare="$3"
#    _localmountpoint="$4"
#  else
#    log "[CRIT] Parameter(s) missing (nfs_mount); process aborted!"
#    exit 1
#  fi

  # Make sure remote NFS service is available
#  check_remotenfs ${_remotesystem} 
#  if ${_RET} ; then

    # Make sure the remote NFS share is available
#    check_remoteshare ${_remotesystem} ${_remoteshare}
#    if ${_RET} ; then

      # Make sure the local mountpoint exists and is free
#      valid_for_mount ${_localmountpoint}
#      if ${_RET} ; then

#        log "[INFO] Attempting mount: ${mountcmd} ${_mountopts} ${_remotesystem}:${_remoteshare} ${_localmountpoint}"
#        ${mountcmd} ${_mountopts} ${_remotesystem}:${_remoteshare} ${_localmountpoint}
#        if [ $? -ne 0 ] ; then
#          log "[CRIT] Unable to mount share '${_remoteshare}'!"
#        else
#          log "[INFO] Share '${_remoteshare}' mounted from '${_remotesystem}' at '${_localmountpoint}'."
#        fi

#      else
#        log "[CRIT] Local mount point '${_localmountpoint}' missing or already in use!"
#      fi
    
#    else
#      log "[CRIT] Remote share '${_remoteshare}' unavailable!"
#    fi
  
#  else
#    log "[CRIT] Remote NFS service unavailable at '${_remotesystem}'!"
#  fi
#}


#function nfs_remount {
#  if [ ! -z "$1" ] && [ ! -z "$2" ] && [ ! -z "$3" ] && [ ! -z "$4" ] ; then 
#    _mountopts="$1"
#    _remotesystem="$2"
#    _remoteshare="$3"
#    _localmountpoint="$4"
#  else
#    log "[CRIT] Parameter(s) missing (nfs_remount); process aborted!"
#    exit 1
#  fi

#  nfs_umount ${_localmountpoint}
#  if ${_RET} ; then
#    log "[INFO] Unmounted '${_localmountpoint}'. Proceeding with remount."
#    nfs_mount "${_mountopts}" "${_remotesystem}" "${_remoteshare}" "${_localmountpoint}"
#  else
#    log "[CRIT] Could not unmount '${_localmountpoint}'. Cannot proceed with remount!"
#  fi
#}


# -- LOGIC --

#log "[NOTE] Monitoring started."

#while : ; do

for i in range(1):

#  if ! ${DEBUGLOG} ; then
#    log "[NOTE] Checking shares. Debug logging disabled." 
#  fi

#  mountscnt=${#MOUNTDATA[@]}
#  for (( i=0; i<${mountscnt}; i++)); do
    for mount in config.mounts:

#    get_mount_dataset ${MOUNTDATA[$i]}

#	((datasetno=${i} + 1))

#    if [ ${#_RET[@]} -lt 5 ] ; then
#      log "[CRIT] Incomplete mount dataset ${datasetno} in '${CONFIG}'. Skipping!"

#      if [ ${#_RET[@]} -eq 1 ] ; then
#        log "[NOTE] Only one parameter in dataset ${datasetno} in '${CONFIG}'. Bad delimiter ('${DELIMITER}')?"
#      fi

#      continue
#    fi

#    NFSMOUNTOPTS=${_RET[0]}
#    REMOTESYSTEM=${_RET[1]}
#    REMOTESHARE=${_RET[2]}
#    LOCALMOUNTPOINT=${_RET[3]}
#    REMOTECHECKFILE=${_RET[4]}
#    READWRITE=${_RET[5]}

#    check_remotenfs ${REMOTESYSTEM}
#    if ${_RET} ; then
#      log "[INFO] (dataset ${datasetno}) Remote server/NFS service at '${REMOTESYSTEM}' available."

#      check_mounted ${LOCALMOUNTPOINT}

#      if ${_RET} ; then
#        log "[INFO] (dataset ${datasetno}) Local mount point '${LOCALMOUNTPOINT}' active."
        if mount.check_mounted():
            print('Local mount point %s is active' % (mount.mountpoint,))

#        check_stale ${LOCALMOUNTPOINT}
#        if ! ${_RET} ; then
#          log "[INFO] (dataset ${datasetno}) Local mount point '${LOCALMOUNTPOINT}' not stale."

#          if [ ! -z ${REMOTECHECKFILE} ] ; then
#            test_remotecheckfile ${REMOTECHECKFILE}
#            if ${_RET} ; then
#              log "[INFO] (dataset ${datasetno}) Remote test file '${REMOTECHECKFILE}' is reachable via local the mount point '${LOCALMOUNTPOINT}'."
#            else
#              log "[CRIT] (dataset ${datasetno}) Remote test file '${REMOTECHECKFILE}' could not be reached via the mount point '${LOCALMOUNTPOINT}'. This may indicate a remote system problem!"
#            fi
#          else
#            log "[NOTE] (dataset ${datasetno}) Remote test file not defined. Skipping remote test file check for this dataset."
#          fi

          # RO/RW PROCESSING  
#          TESTFILE="${LOCALMOUNTPOINT}"/"${RW_TESTFILE}"
#          test_rw ${TESTFILE}
#          if ${_RET} ; then
#            log "[INFO] (dataset ${datasetno}) Mount point '${LOCALMOUNTPOINT}' is writable."
            
#            if [ "${READWRITE}" = "ro" ]; then
#              log "[INFO] (dataset ${datasetno}) Read Only mount has been specified. Attempting remount." 
#              nfs_remount "${NFSMOUNTOPTS}" "${REMOTESYSTEM}" "${REMOTESHARE}" "${LOCALMOUNTPOINT}"
#            fi

#          else
#            log "[INFO] (dataset ${datasetno}) Mount point '${LOCALMOUNTPOINT}' is not writable."
            
#            if [ "${READWRITE}" = "rw" ]; then
#              log "[INFO] (dataset ${datasetno}) Read/Write mount has been specified. Attempting remount." 
#              nfs_remount "${NFSMOUNTOPTS}" "${REMOTESYSTEM}" "${REMOTESHARE}" "${LOCALMOUNTPOINT}"
#            fi

#          fi
  
#        else
          #STALE PROCESSING
#          log "[CRIT] (dataset ${datasetno}) Remote NFS share '${REMOTESYSTEM}:${REMOTESHARE}' is stale; attempting remount."
          
#          nfs_remount "${NFSMOUNTOPTS}" "${REMOTESYSTEM}" "${REMOTESHARE}" "${LOCALMOUNTPOINT}"
    
#        fi


        #UNMOUNTED PROCESSING
#        log "[CRIT] (dataset ${datasetno}) Remote NFS share '${REMOTESYSTEM}:${REMOTESHARE}' is unmounted; attempting mount."

        else:
            print('Remote NFS share %s:%s is unmounted; attempted to mount' % (mount.host, mount.share))
            # Need to be a try-to-mount in here

#        nfs_mount "${NFSMOUNTOPTS}" "${REMOTESYSTEM}" "${REMOTESHARE}" "${LOCALMOUNTPOINT}"
  
#      fi
    
#    else
      #UNREACHABLE SERVER/NFS SERVICE PROCESSING
#      log "[CRIT] (dataset ${datasetno}) Remote server/NFS service at '${REMOTESYSTEM}' unreachable; confirming unmounted status of share '$REMOTESHARE'."
      
#      nfs_umount "${LOCALMOUNTPOINT}"
#      if ${_RET} ; then
#        log "[INFO] (dataset ${datasetno}) Remote server '${REMOTESYSTEM}' or its NFS service is unreachable. Share '${REMOTESHARE}' has been confirmed unmounted!"
#      else
#        log "[CRIT] (dataset ${datasetno}) Remote server '${REMOTESYSTEM}' or its NFS service is unreachable. Share '${REMOTESHARE}' could not be unmounted!"
#      fi
  
#    fi

#  done

  # Break here for cron style run
#  [[ "${RUNTYPE}" = "service" ]] || break
  
#  log "[INFO] Sleeping for ${INTERVAL} seconds."
#  sleep $INTERVAL

#done
