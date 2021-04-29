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
Bắt buộc Server phải được khởi động trước khi client.py được sử dụng

```bash
# Sử dụng cmd cho Server
# Khởi động Server
python server.py -listen

# Liệt kê mọi Client
python server.py -list-all-clients

# Xuất báo cáo Client ra file csv
python server.py -export-report <client's id>

# Input id for specific Client
python server.py -change-report-time <client's id> <time in seconds>
# If want to send new recurring time to all Client, input as below
python server.py -change-report-time -all <time in seconds>
```

```bash
# Sử dụng cmd cho Client
# Đăng ký mới
python client.py -register <server's id>

# Khởi động Client
python client.py -start
```
## Author

- [Nguyễn Trí Nhân](https://github.com/edwardnguyen2255)
- [Đặng Tiến Mạnh](https://github.com/tienmanh294)
- [Phan Minh Dũng](https://github.com/Mrwizard3011)
