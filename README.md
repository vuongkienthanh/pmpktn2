# Phần mềm phòng mạch tư
- Tác giả: BS Vương Kiến Thanh  
- Email: thanhstardust@outlook.com

## Chức năng:
- Quản lý bệnh nhân và các lượt khám
- Quản lý kho thuốc
- In toa thuốc
- Dùng database SQLite

## Cài đặt:
<details> <summary>Windows</summary>

### Install `python`
Download **python3.10** at https://www.python.org/downloads/ and install it

### Install `poetry`
Open power shell
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```

### Download this repo
Initialize the poetry env
```sh
poetry env use python3.10
poetry install --no-dev
```
Start app
```sh
cd src && poetry run python main.py
```

### Shortcut to start app
Run Directly or Create shortcut to Desktop from `start_app\windows_cmd.bat` or `start_app\windows_no_cmd.vbs`
</details>

<details> <summary>Mac OS</summary>

### Install `python`
Download **python3.10** at https://www.python.org/downloads/ and install it

### Install `poetry`
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```

### Download this repo
Initialize the poetry env
```sh
poetry env use python3.10
poetry install --no-dev
```
Start app
```sh
cd src && poetry run python main.py
```

### Shortcut to start app
Run Directly or Create shortcut to Desktop from `start_app/macos.sh`  
You may need to make it executable with `chmod +x macos.sh`
</details>

<details> <summary>Linux (Ubuntu, Debian based)</summary>

### Download source code and build `python`
As of writing, there is no available python3.10 executable.  
You have to compile it yourself.  
Download **python3.10** source code at https://www.python.org/downloads/

Install dependencies
```sh
sudo apt install -y build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev python3-venv\
      libgtk-3-0 libgtk-3-bin libgtk-3-common libgtk-3-dev \
      libgstreamer1.0-dev libgstreamer-plugins-base1.0-0 \
      libgstreamer-plugins-base1.0-dev freeglut3 freeglut3-dev
```
Extract the downloaded source code and run
```sh
./configure --enable-loadable-sqlite-extensions --enable-optimizations
make
sudo make altinstall
```

### Install `poetry`
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```

### Download this repo
Initialize the poetry env
```sh
poetry env use python3.10
poetry install --no-dev
```
Start app
```sh
cd src && poetry run python main.py
```

### Shortcut to start app
Run Directly or Create shortcut to Desktop from `start_app/linux.sh`  
You may need to make it executable with `chmod +x linux.sh`
</details>
