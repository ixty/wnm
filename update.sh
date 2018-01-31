#!/bin/bash

SECONDS=0

source venv/bin/activate

# =========================================================================== #
# update all databases
# =========================================================================== #
./wnm/wnm_asnames.py    update                                      || exit 1
./wnm/wnm_bgp.py        update                                      || exit 1
./wnm/wnm_geo.py        update                                      || exit 1
./wnm/wnm_nics.py       update                                      || exit 1
./wnm/wnm_scd.py        update                                      || exit 1
./wnm/wnm_world.py      update                                      || exit 1

# peering db is different
source venv/bin/activate
echo '========================================'
echo '> updating PeeringDB                    '
echo '========================================'
peeringdb sync                                                      || exit 1
cp ~/.peeringdb/peeringdb.sqlite3 ./data-raw/ || cp ./peeringdb.sqlite3 ./data-raw/ || exit 1
echo

# =========================================================================== #
# merge all databases
# =========================================================================== #
./wnm/wnm_merge.py                                                  || exit 1

d=$SECONDS
echo "> all done :) ($(($d / 60))m $(($d % 60))s)"
