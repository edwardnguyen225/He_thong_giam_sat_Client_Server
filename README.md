# Hệ thống giám sát Client Server

Đây là dự án hệ thống giám sát Client Server, bài tập lớn 1, môn Mạng máy tính

## Installation

Cài đặt python 3.9 [tại đây](https://www.python.org/downloads/). Sau đó, sử dụng package manager [pip](https://pip.pypa.io/en/stable/) để cài pipenv nhằm để dễ cài đặt những dependency khác

```bash
pip install pipenv

# Install dependencies
pipenv install
```

## Usage

```python
# Sử dụng cmd cho Client
python client.py -register
python client.py -monitor-system
```

```python
# Sử dụng cmd cho Server
python server.py -listen
python server.py -list-all-devices
python server.py -create-report <device's id>
python server.py -change-report-time <device's id> <time in seconds>
```

## Author

- [Nguyễn Trí Nhân](https://github.com/edwardnguyen2255)
- [Đặng Tiến Mạnh](https://github.com/tienmanh294)
- [Phan Minh Dũng](https://github.com/Mrwizard3011)
