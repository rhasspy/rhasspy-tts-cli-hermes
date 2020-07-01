#!/usr/bin/env bash
set -e

# Directory of *this* script
this_dir="$( cd "$( dirname "$0" )" && pwd )"
src_dir="$(realpath "${this_dir}/..")"

download="${src_dir}/download"
mkdir -p "${download}"

# -----------------------------------------------------------------------------

for docker_arch in amd64 armv7 arm64 armv6; do
    nanotts="nanotts-20200520_${docker_arch}.tar.gz"
    if [[ ! -s "${download}/${nanotts}" ]]; then
        wget -O "${download}/${nanotts}" "https://github.com/synesthesiam/prebuilt-apps/releases/download/v1.0/${nanotts}"
    fi
done
