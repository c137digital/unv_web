rm -rf ./venv

python3 -m venv ./venv

. activate.sh

pip install --upgrade pip
pip install wheel
pip install -e .[dev]
