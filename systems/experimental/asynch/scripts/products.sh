#!/bin/bash

#         __________________________
#         |____C_O_P_Y_R_I_G_H_T___|
#         |                        |
#         |  (c) NIWA, 2008-2010   |
#         | Contact: Hilary Oliver |
#         |  h.oliver@niwa.co.nz   |
#         |    +64-4-386 0461      |
#         |________________________|


# run length 10 minutes

# trap errors so that we need not check the success of basic operations.
set -e; trap 'cylc task-failed "error trapped"' ERR

# START MESSAGE
cylc task-started || exit 1

# check environment
check-env.sh || exit 1

# check prerequisites
ONE=$CYLC_TMPDIR/pass-${ASYNCID}.nc
for PRE in $ONE; do
    if [[ ! -f $PRE ]]; then
        # FAILURE MESSAGE
        cylc task-failed "file not found: $PRE"
        exit 1
    fi
done

# EXECUTE THE TASK ...
sleep 10

# create task outputs
touch $CYLC_TMPDIR/products-${ASYNCID}.nc
cylc task-message "products $ASYNCID ready"

# SUCCESS MESSAGE
cylc task-finished
