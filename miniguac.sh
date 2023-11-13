# shortened guac interface
# source this file to enable

function mguse {
	echo "mini interface for guac"
	echo "---"

    cat << EOF | column -t -s "|"
mguse | print this help page
mgvars | list miniguac environment variables
mgexit | unsets all miniguac functions
---
gini | guac init
gl | guac list --recipe \$RECIPE
ggen | guac generate --recipe \$RECIPE
grn | guac run --name \$NAME --recipe \$RECIPE
grt | guac run --these \$THESE --recipe \$RECIPE
ggrade | guac grade --name \$NAME --recipe \$RECIPE
gsum | guac summerize --these \$THESE --recipe \$RECIPE
guscore | guac update score --name \$NAME --recipe \$RECIPE
gustatus | guac update status --name \$NAME --recipe \$RECIPE
gins | guac inspect --name \$NAME --recipe \$RECIPE
gext | guac extract --these \$THESE --recipe \$RECIPE
gexp | guac export --these \$THESE --recipe \$RECIPE
EOF
	echo "---"
	echo "simply append flags to the end of any command to modify it e.g. 'gu --task report --score 10'"
}

function mgvars {
	echo "NAME: $NAME"
	echo "THESE: $THESE"
	echo "RECIPE: $RECIPE"
}

function mgexit {
	unset -f gini
	unset -f ggen
	unset -f grn
	unset -f grt
	unset -f ggrade
	unset -f gsum
	unset -f guscore
	unset -f gustatus
	unset -f gins
	unset -f gext
	unset -f gexp
}

function _miniguac_run_command {
 	echo "> $1"
	$1
}

function gini {
	comm="guac init"
	_miniguac_run_command "$comm"
}

function gl {
	comm="guac list --recipe $RECIPE"
	_miniguac_run_command "$comm"
}

function ggen {
	comm="guac generate --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function grn {
	comm="guac run --name $NAME --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function grt {
	comm="guac run --these $THESE --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function ggrade {
	comm="guac grade --name $NAME --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function gsum {
	comm="guac summerize --these $THESE --recipe $RECIPE"
	_miniguac_run_command "$comm"
}

function guscore {
	comm="guac update score --name $NAME --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function gustatus {
	comm="guac update status --name $NAME --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}


function gins {
	comm="guac inspect --name $NAME --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function gext {
	comm="guac extract --these $THESE --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function gexp {
	comm="guac export --these $THESE --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

function gs {
	comm="guac server --recipe $RECIPE $@"
	_miniguac_run_command "$comm"
}

mguse
