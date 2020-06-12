# Zapple-Balancer 
Portfolio re-balancer for zapple. Herein I provide a script to automate digital asset portfolio re-balance at user specified intervals (defaults to every hour). Note this is long only spot portfolio.

# How to setup my balancer ?

Steps to get started:

1. [Download and install python framework](https://www.python.org/downloads/)
2. [Set up a Zapple account](https://zapple.com)
3. Fund your Zapple account with BTC
5. Download this zapple balancer script
6. Edit username and password in zapple-balancer.py
7. Edit your configuration:

```python
lastweights = {  "BTC":0.5,   "AUR":0.5 }
```
Install dependencies (in command window):

```
pip install  math
pip install  time
pip install  pandas 
pip install  numpy 
pip install  requests
pip install  json
pip install  apscheduler
```
Run the script (it will automatically re-balance for you every hour):

```
python zapple-balancer.py
```

# Karma Jar
BTC - 112eMCQJUkUz7kvxDSFCGf1nnFJZ61CE4W

LTC - LR3BfiS77dZcp3KrEkfbXJS7U2vBoMFS7A

ZEC - t1bQpcWAuSg3CkBs29kegBPXvSRSaHqhy2b

XLM - GAHK7EEG2WWHVKDNT4CEQFZGKF2LGDSW2IVM4S5DP42RBW3K6BTODB4A Memo: 1015040538

Nano - nano_1ca5fxd7uk3t61ghjnfd59icxg4ohmbusjthb7supxh3ufef1sykmq77awzh

XRP - rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh Tag: 103535357

EOS - binancecleos Memo: 103117718

# Recommended links
Getting started - [Coinbase](https://www.coinbase.com/join/bradle_6r)

Portfolio balance - [Binance](https://www.binance.com/en/register?ref=LTUMGDDC)

Futures trading - [Deribit](https://www.deribit.com/reg-8106.6912)

Cold wallet - [Atomic](https://atomicWallet.io?kid=12GR52)
