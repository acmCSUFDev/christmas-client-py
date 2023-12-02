# SPDX-License-Identifier: GPL-3.0-or-later

all: build_proto
	poetry build
	
build_proto:
	wget -O christmas.proto https://raw.githubusercontent.com/acmCSUFDev/christmasd/main/christmas.proto
	protoc -I=. --python_out=libacmchristmas ./christmas.proto