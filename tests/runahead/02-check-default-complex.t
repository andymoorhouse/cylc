#!/bin/bash
# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2019 NIWA & British Crown (Met Office) & Contributors.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
# Test default runahead limit behaviour is still the same
. $(dirname $0)/test_header
#-------------------------------------------------------------------------------
set_test_number 5
#-------------------------------------------------------------------------------
install_suite $TEST_NAME_BASE default-complex
#-------------------------------------------------------------------------------
TEST_NAME=$TEST_NAME_BASE-validate
run_ok $TEST_NAME cylc validate -v $SUITE_NAME
#-------------------------------------------------------------------------------
TEST_NAME=$TEST_NAME_BASE-run
run_fail $TEST_NAME cylc run --debug --no-detach $SUITE_NAME
#-------------------------------------------------------------------------------
if ! which sqlite3 > /dev/null; then
    skip 2 "sqlite3 not installed?"
else
    TEST_NAME=$TEST_NAME_BASE-max-cycle
    DB="$(cylc get-global-config --print-run-dir)/${SUITE_NAME}/log/db"
    run_ok $TEST_NAME sqlite3 $DB "select max(cycle) from task_states"
    cmp_ok "$TEST_NAME.stdout" <<'__OUT__'
20100102T0500Z
__OUT__
fi
#-------------------------------------------------------------------------------
TEST_NAME=$TEST_NAME_BASE-check-timeout
LOG=$(cylc get-global-config --print-run-dir)/$SUITE_NAME/log/suite/log
grep_ok 'suite timed out after' $LOG
#-------------------------------------------------------------------------------
purge_suite $SUITE_NAME
