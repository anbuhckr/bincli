# bincli

[![GitHub issues](https://img.shields.io/github/issues/anbuhckr/bincli)](https://github.com/anbuhckr/bincli/issues)
[![GitHub forks](https://img.shields.io/github/forks/anbuhckr/bincli)](https://github.com/anbuhckr/bincli/network)
[![GitHub stars](https://img.shields.io/github/stars/anbuhckr/bincli)](https://github.com/anbuhckr/bincli/stargazers)
[![GitHub license](https://img.shields.io/github/license/anbuhckr/bincli)](./LICENSE)
![PyPI - Python Version](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue)

Binance Client

## Table of Contents

* [Installation](#installation)
* [CLI](#CLI)
* [Getting Started](#getting-started)


## Installation

To install bincli, simply:

```
$ python3 -m pip install -U git+https://github.com/anbuhckr/bincli.git
```

or from source:

```
$ python3 setup.py install
```

## CLI

Set api key & secret:

```
$ python3 -m bincli api "your_api_key" "your_api_sec"
```

Usage:

```
# python3 -m bincli run symbol levrage margin side
$ python3 -m bincli run BTCUSDT 50 2 long
```

## Getting Started

``` python
#! /usr/bin/env python3

from bincli import BinanceClient

key = ''
sec = ''
binbot = BinanceClient(key, sec, maxtx=10, debug=False)
binbot.run('BTCUSDT', 50, 2, 'long')
```
