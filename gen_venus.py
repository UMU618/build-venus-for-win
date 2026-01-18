#!/usr/bin/env python3
import os
import sys
import argparse

def validate_param(value, valid_values, param_name):
    if value not in valid_values:
        raise ValueError(f'Invalid {param_name}: "{value}". Valid values are: {', '.join(valid_values)}')
    return value

# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate Venus build with Meson')
parser.add_argument('-p', '--platform', choices=['arm', 'arm64', 'arm64ec', 'x64', 'x86'], help='Target platform')
parser.add_argument('-c', '--configuration', choices=['debug', 'release'], help='Build configuration')
parser.add_argument('--vcrt', choices=['md', 'mt'], help='VCRT type')
args = parser.parse_args()

# Set default values if not provided
input_platform = args.platform
input_configuration = args.configuration or 'release'
input_vcrt = args.vcrt or 'mt'

# Import check_dev_shell.py directly
sys.path.append(os.path.dirname(__file__))
try:
    import check_dev_shell
except Exception as e:
    print(f'Error importing check_dev_shell.py: {e}', file=sys.stderr)
    sys.exit(1)

# Get environment variables checked by check_dev_shell.py
target_arch = os.environ.get('VSCMD_ARG_TGT_ARCH')
host_arch = os.environ.get('VSCMD_ARG_HOST_ARCH')
vc_dir = os.environ.get('VCINSTALLDIR')
vs_dir = os.environ.get('VSINSTALLDIR')

# If input_platform is not provided, use the target architecture from environment
if not input_platform:
    input_platform = target_arch

# Validate parameters (Python's argparse already does this, but we'll double-check)
valid_platforms = ['arm', 'arm64', 'arm64ec', 'x64', 'x86']
valid_configurations = ['debug', 'release']
valid_vcrt = ['md', 'mt']

input_platform = validate_param(input_platform, valid_platforms, "platform")
input_configuration = validate_param(input_configuration, valid_configurations, "configuration")
input_vcrt = validate_param(input_vcrt, valid_vcrt, "vcrt")

# Determine detected target architecture
if input_platform == 'arm64ec':
    detected_target_arch = 'arm64'
else:
    detected_target_arch = input_platform

# Print target settings
print('  Target Settings')
print(f'    Platform     : {input_platform}')
print(f'    Architecture : {detected_target_arch}')
print(f'    Configuration: {input_configuration}')
print(f'    VCRT         : {input_vcrt}')
print()

# Print environment
print('  Environment')
print(f'    VCINSTALLDIR       : {vc_dir}')
print(f'    VSCMD_ARG_HOST_ARCH: {host_arch}')
print(f'    VSCMD_ARG_TGT_ARCH : {target_arch}')
print()

# Check if detected target architecture matches current environment
if detected_target_arch != target_arch:
    print(f'Error: Detected target architecture \'{detected_target_arch}\' does not match current environment\'s target architecture \'{target_arch}\'')
    print(f'Please launch Developer PowerShell for VS with parameter: -DevCmdArguments \'-arch={detected_target_arch} ...\'')
    sys.exit(1)

# Determine if cross-file is needed
cross_file = ''
if detected_target_arch != host_arch:
    cross_file = os.path.join(os.path.dirname(__file__), f'build-{input_platform}.txt')

# Set minimum Windows version
min_win_ver = ''
if detected_target_arch == 'x86':
    min_win_ver = '7'

# Set compilation flags
c_args='/Zi /FS /WX- /wd4189'
cpp_args='/Zi /FS /WX- /wd4189'
c_link_args='/DEBUG'
cpp_link_args='/DEBUG'
c_flags = ''
ld_flags = ''
if input_platform == 'arm64ec':
    c_flags = '/arm64EC -D_AMD64_ -D_ARM64EC_'
    ld_flags = '/arm64EC /MACHINE:ARM64EC'
if c_flags:
    c_args += ' ' + c_flags
    cpp_args += ' ' + c_flags
if ld_flags:
    c_link_args += ' ' + ld_flags
    cpp_link_args += ' ' + ld_flags

# Determine if debug is disabled
no_debug = 'false'
if input_configuration == 'release':
    no_debug = 'true'

# Build meson arguments
script_dir = os.path.dirname(__file__)
meson_args = [
    os.path.join(script_dir, f'build/vv_{input_platform}_{input_configuration}'),
    '.',
    '--backend=vs',
    '--default-library=static',
    f'--prefix={os.path.join(script_dir, f'build/out_vv_{input_platform}_{input_configuration}')}',
    f'-Dbuildtype={input_configuration}',
    f'-Db_ndebug={no_debug}',
    f'-Db_vscrt={input_vcrt}',
    f'-Dc_args={c_args}',
    f'-Dcpp_args={cpp_args}',
    f'-Dc_link_args={c_link_args}',
    f'-Dcpp_link_args={cpp_link_args}',
    '-Degl=disabled',
    '-Dllvm=disabled',
    '-Dplatforms=windows',
    '-Dvideo-codecs=',
    '-Dgallium-drivers=',
    '-Dvulkan-drivers=virtio',
    '-Dwerror=false',
    '-Dzlib=disabled'
]

# Add cross-file if needed
if cross_file:
    meson_args.append(f"--cross-file={cross_file}")

# Add minimum Windows version if needed
if min_win_ver:
    meson_args.append(f"-Dmin-windows-version={min_win_ver}")

# Print meson arguments
print("  Meson arguments")
for arg in meson_args:
    print(f"    {arg}")
print()

# Function to quote arguments containing spaces
def quote_arg(arg):
    return f'\'{arg}\'' if ' ' in arg else arg

# Print meson setup command
print('meson command:')
print(f'cd {os.getcwd()}')
quoted_args = [quote_arg(arg) for arg in meson_args]
print(f'meson setup {' '.join(quoted_args)}')
print()
