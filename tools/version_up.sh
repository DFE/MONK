#!/bin/bash

usage()
{
cat >&2 <<EOF

Replace all version strings in the monk_tf project

Usage: $0 [version | -h ]
with arguments:
    version               a version string, e.g. 0.17.3
    -h/--help             this help
    -d/--debug            debug output

EOF
}

while [ "$#" -gt 0 ]
do
    case $1 in
        -h|--help) usage; exit 10;;
        -d|--debug) set -x;;
        *) IN_VERSION=$1;;
    esac
    shift
done

if [ -z "$IN_VERSION" ]; then
    echo "need a version string"
    usage
    exit 1
fi

VPARTS=(${IN_VERSION//./ })

if (("${#VPARTS[@]}" < "3")); then
    echo "version string should have three parts, separated by dots: INT.INT.INT"
    usage
    exit 2
fi

REPOPATH="`git rev-parse --show-toplevel`"

if [ -z "${REPOPATH}" ]; then
    echo "something went wrong. Can't find the git root"
    exit 3
fi

VERSION="${VPARTS[0]}.${VPARTS[1]}"
RELEASE="${IN_VERSION}"

set -x
sed -i "s/^version.*$/version = '${VERSION}'/" ${REPOPATH}/doc/conf.py
sed -i "s/^release.*$/release = '${RELEASE}'/" ${REPOPATH}/doc/conf.py
sed -i "s/__version__.*$/__version__ = '${RELEASE}'/" ${REPOPATH}/monk_tf/__init__.py
