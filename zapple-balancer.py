'''
Zapple Balancer
2020 - Sandy Bay

Re-balances every hour based on manually fixed allocations
Defaults to limit orders which are cancelled if unfilled and recalculated for the new rebalance

'''
import math
import time
import pandas as pd
import numpy as np
import requests
import json
from apscheduler.schedulers.blocking import BlockingScheduler

# set username and password
# note developed without 2fa

username = ""
password = ""

# set weights

lastweights = {
    "AUR":0.5,
    "BTC":0.5, 
    } 

# globals
prices = {} # asset prices in btc
prices['BTC'] = 1.0
BTCUSD = 0.0
balances = {}
balancesbtc = {}
totalbtc = 0
diffs = {}
steps = {}
ticks = {}
minQtys = {}
ids={}

jwt = ''
authy = ''

def getAccess():
    global jwt, authy
    # connect
    response = requests.put(
        'https://zapple.io/auth/1/',
        headers = {"accept": "text/plain",'content-type': 'application/json'},
        json={
            "username": username,
            "password":password,
            "twoFactorAuthenticationCode": 0
            },
        
        )
    # print(response)
    # print(response.content)
    jwtS = json.loads(response.content)
    jwt = jwtS['jsonWebToken']
    # print(jwt)

    authy = "Bearer " + jwt
    print(authy)

def getPrices():
    global prices
    # get prices
    response3 = requests.get(
        'https://zapple.io/exchange/1/ticker',
        headers = {"accept": "text/plain",'content-type': 'application/json',"Authorization": authy}    
        )
    priceinfo = json.loads(response3.content)
    for price in priceinfo:
        instrument = price['instrument']
        instsplit = instrument.split("/")
        asset = instsplit[0]
        quote = instsplit[1]        
        p = float(price['price'])
        if quote == 'BTC':
            if asset in lastweights:
                prices[asset] = p
    print('Prices (BTC)')
    print(prices)

def getBalance():
    global balances, balancesbtc, totalbtc 
    totalbtc = 0
    # balances
    response2 = requests.get(
        'https://zapple.io/exchange/1/balances',
        headers = {"accept": "text/plain",'content-type': 'application/json',"Authorization": authy}    
        )
    # print(response2.content)
    bals = json.loads(response2.content)
    print(bals)
    for balance in bals:
        bal = balance["value"]
        asset = balance['currency']
        if asset in lastweights:
            balances[ asset ] = bal
            balancesbtc[ asset ] = bal * prices[asset]
            totalbtc = totalbtc + bal * prices[asset]
    # print(balances)
    print("Balances (BTC)")
    print(balancesbtc)

def getDiffs():
    global diffs
    # get difference
    for asset in lastweights:
        adjshare = totalbtc * lastweights[asset]
        currshare = balancesbtc[asset]
        diff = adjshare - currshare
        diffs [ asset ] = diff
    diffs = dict(sorted(diffs.items(), key=lambda x: x[1]))
    print('Adjustments (BTC)')
    print(diffs)

def cancelOrders():
    # cancel current orders
    print('Canceling open orders')
    # balances
    response4 = requests.get(
        'https://zapple.io/exchange/1/orders',
        headers = {"accept": "text/plain",'content-type': 'application/json',"Authorization": authy}    
        )
    # print(response2.content)
    orders = json.loads(response4.content)
    print(orders)
    for order in orders:
        orderId  = order['orderId']
        requests.delete(
            'https://zapple.io/exchange/1/orders/',
            headers = {"accept": "text/plain",'content-type': 'application/json',"Authorization": authy},
            json = {'orderId ':orderId }
            )


# def step_size_to_precision(ss):
#     return ss.find('1') - 1

# def format_value(val, step_size_str):
#     precision = step_size_to_precision(step_size_str)
#     if precision > 0:
#         return "{:0.0{}f}".format(val, precision)
#     return math.floor(int(val))

def format_value(val, precision):
    if precision > 0:
        return "{:0.0{}f}".format(val, precision)
    return math.floor(int(val))

def getSteps():
    global steps, ticks, minQtys
    # step sizes
    response5 = requests.get(
        'https://zapple.io/api/exchange/1/instruments',
        headers = {"accept": "text/plain",'content-type': 'application/json',"Authorization": authy}    
        )
    info = json.loads(response5.content)
    for dat in info:
        id = dat['id']
        quote = dat[-3:]
        asset = dat[0:-3]
        if quote == 'BTC' and asset in lastweights:
            ordmin = dat['orderMinimum']
            decimalPlaces = dat['decimalPlaces']
            priceDecimalPlaces = dat['priceDecimalPlaces']
            steps[asset] = decimalPlaces
            ticks[asset] = priceDecimalPlaces
            minQtys[asset] = ordmin
            ids[asset] = id
        
def placeOrders():
    # all go through btc
    # this can be smart routed later
    global diffs
    getSteps()
    
    # set sell orders
    for asset in diffs:
        diff = diffs[asset]
        if asset != 'BTC':
            thresh = minQtys[asset]
            if  diff <  -0.0001 : # threshold $ 1
                if asset != 'BTC' :
                    sym = asset + 'BTC'
                    amountf = 0-diff # amount in btc
                                          
                    amount = format_value ( amountf / prices[asset] , steps[asset] )
                    price = format_value ( prices [ asset ] + 0.05 * prices [ asset ], ticks[asset] )# adjust for fee
                    minNotion = float(amount) * float(price)
                    if minNotion > thresh:
                        diffs[asset] = diffs[asset] + amountf
                        diffs['BTC'] = diffs['BTC'] - amountf    
                        print('Setting sell order for {}, amount:{}, price:{}, thresh:{}'.format(asset,amount,price,thresh))

                        response = requests.post(
                            'https://zapple.io/exchange/1/orders/',
                            headers = {"accept": "text/plain",'content-type': 'application/json'},
                            json={
                                "instrumentId":ids[asset],
                                "quantityOrdered":float(amount),
                                "side": "Sell",
                                "limitPrice":float(price)
                                },
                            
                            )
                        # print(response)
                        # print(response.content)
                  
                    
                
    # set buy orders
    diffs = dict(sorted(diffs.items(), key=lambda x: x[1], reverse=True))

    for asset in diffs:
        diff = diffs[ asset ]
        if asset != 'BTC':
            thresh =  minQtys[ asset ] 
            if  diff >  0.0001 : # threshold $ 1
                if asset != 'BTC' :
                    sym = asset + 'BTC'
                    amountf = diff

                    amount = format_value ( amountf / prices[asset] , steps[asset] )
                    price = format_value ( prices [ asset ] - 0.05 * prices [ asset ] , ticks[asset] )# adjust for fee
                    minNotion = float(amount) * float(price)
                    if minNotion > thresh:
                        diffs[asset] = diffs[asset] - amountf
                        diffs['BTC'] = diffs['BTC'] + amountf 
                        print('Setting buy order for {}, amount:{}, price:{}, thresh:{}'.format(asset,amount,price,thresh))
                  
                        response = requests.post(
                            'https://zapple.io/exchange/1/orders/',
                            headers = {"accept": "text/plain",'content-type': 'application/json'},
                            json={
                                "instrumentId":ids[asset],
                                "quantityOrdered":float(amount),
                                "side": "Buy",
                                "limitPrice":float(price)
                                },
                            
                            )
                        # print(response)
                        # print(response.content)
                  
                    

    print ( 'Final differences' )
    print ( diffs )

def iteratey():
    getAccess()
    getPrices()
    getBalance()
    getDiffs()
    cancelOrders()
    placeOrders()    

iteratey()

scheduler = BlockingScheduler()
scheduler.add_job(iteratey, 'interval', hours=1)
scheduler.start()
