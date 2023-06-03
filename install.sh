
set -e
#
PYTHON=`which python3.8`
#
#### AVOCADO
##
### download avocado
#pushd ~
#rm -rf avocado/
##git clone git@github.com:avocado-framework/avocado.git
#git clone https://github.com/avocado-framework/avocado.git
#
### install
#cd avocado
#$PYTHON setup.py install --user
#
##
### enable plugins
#$PYTHON setup.py plugin --install=varianter_yaml_to_mux --user
#
##
### add configuration
#mkdir -p ~/.config
#mkdir -p ~/.config/avocado
#cat > ~/.config/avocado/avocado.conf <<EOF
## requries tasks to be run in order
#[run]
#max_parallel_tasks: 1
#EOF
##
#
##
## modify avocado executable to use correct python version
## replace python_src with python version >3.7
##python_src="\/s\/chopin\/k\/grad\/wscarbro\/.local\/bin\/python"
#sed "s/\/bin\/python3/\/bin\/python3.8/g" ~/.local/bin/avocado -i
#
#
### GUAC
## link
#popd
rm ~/.local/bin/guac
ln -s $PWD/src/guac ~/.local/bin/guac
#
# set guac shebang to $PYTHON

# this should be done with requirements file
$PYTHON -m pip install colorama --user
$PYTHON -m pip install numpy --user



