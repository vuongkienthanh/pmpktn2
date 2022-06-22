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

### Download python source code
Download **python3.10** at https://www.python.org/downloads/

### Install poetry
Open power shell
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```
`cd` to this project folder
```sh
poetry env use python3.10
poetry install --no-dev
```

### Run app
```sh
cd src && poetry run python main.py
```

### Shortcut to start app
Run Directly or Create shortcut to Desktop from `start_app\windows_cmd.bat` or `start_app\windows_no_cmd.vbs`

</details>

<details> <summary>Mac OS</summary>

### Download python source code
Download **python3.10** at https://www.python.org/downloads/

### Install poetry
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```
`cd` to this project folder
```sh
poetry env use python3.10
poetry install --no-dev
```

### Run app
```sh
cd src && poetry run python main.py
```

### Shortcut to start app
Run Directly or Create shortcut to Desktop from `start_app/macos.sh`  
You may need to make it executable with `chmod +x macos.sh`

</details>

<details> <summary>Linux (Ubuntu-based)</summary>

### Download python source code
As of writing, Ubuntu doesn't have its own python3.10. You should download it directly from https://www.python.org/downloads/

### Build python from source
`cd` to extracted folder

```sh
./configure --enable-loadable-sqlite-extensions --enable-optimizations
make
sudo make altinstall
```

### Install dependencies for wxpython
```sh
sudo apt install -y libgtk-3-0 libgtk-3-bin libgtk-3-common libgtk-3-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-0 libgstreamer-plugins-base1.0-dev freeglut3 freeglut3-dev python3.8-full python3.8-venv python3.8-dev libsqlite3-dev
```
Contact me if it's not working!

### Install poetry
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```
`cd` to this project folder
```sh
poetry env use python3.10
poetry install --no-dev
```

### Run app
```sh
cd src && poetry run python main.py
```

### Shortcut to start app
Run Directly or Create shortcut to Desktop from `start_app/linux.sh`  
You may need to make it executable with `chmod +x linux.sh`

</details>