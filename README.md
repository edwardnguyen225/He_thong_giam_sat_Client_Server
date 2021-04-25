# Hệ thống giám sát Client Server

Đây là dự án hệ thống giám sát Client Server, bài tập lớn 1, môn Mạng máy tính

## Installation

Cài đặt python 3.9 [tại đây](https://www.python.org/downloads/). Sau đó, sử dụng package manager [pip](https://pip.pypa.io/en/stable/) để cài đặt những package cần thiết.

```bash
pip install psutil
```

## Usage

```python
python client.py -register
python client.py -monitor-system

python server.py -listen
python server.py -list-all-devices
python server.py -create-report <device's id>
```

## Author

- [edwardnguyen225](https://github.com/edwardnguyen2255)
- [tienmanh294](https://github.com/tienmanh294)
