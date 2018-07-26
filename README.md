# blinktrade-cli
blinktrade-cli is a command line program, that allows you to interact with any blinktrade powered exchange.

# Setup
First thing you need is to create an account with any blinktrade powered exchange.
Here is a list of all blinktrade powered exchanges

Country | Broker ID | Exchange
--- | --- | ---
Brazil | 11 | [BitCambio](https://bitcambio.com.br) 
Chile | 9 | [ChileBit](https://chilebit.net)
Pakistan | 8 | [UrduBit](https://urdubit.com)
Vietnam | 3 | [VBTC](https://vbtc.vn)
Venezuela | 1 | [SurBitcoin](https://surbitcoin.com)
Testnet environment | 5 | [Testnet](https://testnet.blinktrade.com)

# How to 
1. step 1
Create an API Key with the permissions you wish. 

2. step 2 
Set the BLINKTRADE_API_KEY and BLINKTRADE_API_SECRET environment variables 
```
$ export BLINKTRADE_API_KEY=gWFfWvD5UEOBDkGyI6ST7hoGPEMudJBBwn3Hv1rvBGQ
$ export BLINKTRADE_API_SECRET=2LHLQoj0hNg9xcGQNRBMLtYCDTxqZhAdA2RTsKbHD2s
$ export BLINKTRADE_API_BROKER_ID=11
```

3. download & install blinktrade-cli 
```
$ git clone https://github.com/blinktrade/blinktrade-cli 
$ cd blinktrade-cli
$ python setup.py install 
```

4. Run it
```
blinktrade-cli
```

# Examples
- Get the list of all your withdrawals 
```
$ blinktrade-cli  list_withdrawals 
```

- Get the list of all your deposits
```
blinktrade-cli.py  list_deposits 
```


