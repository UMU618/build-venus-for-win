import os
import sys

ERR_NOT_IN_DEV_SHELL = 'Please run me through "Developer PowerShell for VS [version]".'

# Check if required environment variables exist
env_vars = ['VSINSTALLDIR', 'VCINSTALLDIR', 'VSCMD_ARG_HOST_ARCH', 'VSCMD_ARG_TGT_ARCH']
for var in env_vars:
    if var not in os.environ:
        print(ERR_NOT_IN_DEV_SHELL, file=sys.stderr)
        sys.exit(1)

# Check if VSINSTALLDIR points to an existing directory
vs_dir = os.environ['VSINSTALLDIR']
if not os.path.isdir(vs_dir):
    print(f'The environment variable \'VSINSTALLDIR\' is set (value: {vs_dir}), but the folder it points to does not exist.', file=sys.stderr)
    sys.exit(1)

# Check if VCINSTALLDIR points to an existing directory
vc_dir = os.environ['VCINSTALLDIR']
if not os.path.isdir(vc_dir):
    print(f'The environment variable \'VCINSTALLDIR\' is set (value: {vc_dir}), but the folder it points to does not exist.', file=sys.stderr)
    sys.exit(1)

# Check if architectures are valid
valid_archs = ['arm', 'arm64', 'x64', 'x86']
host_arch = os.environ['VSCMD_ARG_HOST_ARCH']
if host_arch not in valid_archs:
    print(f'VSCMD_ARG_HOST_ARCH({host_arch}) is invalid!', file=sys.stderr)
    sys.exit(1)

target_arch = os.environ['VSCMD_ARG_TGT_ARCH']
if target_arch not in valid_archs:
    print(f'VSCMD_ARG_TGT_ARCH({target_arch}) is invalid!', file=sys.stderr)
    sys.exit(1)
