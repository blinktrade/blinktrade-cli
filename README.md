# blinktrade-cli
blinktrade-cli is a command line program, that allows you to interact with any blinktrade powered exchange.

# Setup
First thing you need is to create an account with any blinktrade powered exchange.
Here is a list of all blinktrade powered exchanges

Brazil - https://bitcambio.com.br
Chile - https://chilebit.net 
Pakistan - https://urdubit.com
Vietnam - https://vbtc.vn 
Venezuela - https://surbitcoin.com 
Testnet environment - https://testnet.blinktrade.com

# How to 
- step 1
Create an API Key with the permissions you wish. 

- step 2 
Set the BLINKTRADE_API_KEY and BLINKTRADE_API_SECRET environment variables 

- step 3 
Run it

# Examples
- Get the list of all your withdrawals 
```
blinktrade-cli.py  list_withdrawals 
```

- Get the list of all your deposits
```
blinktrade-cli.py  list_deposits 
```

TODO
