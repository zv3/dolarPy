#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import requests

from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def chaco():
    try:
        soup = json.loads(
            requests.get('http://www.cambioschaco.com.py/api/branch_office/1/exchange', timeout=10).text)
        compra = soup['items'][0]['purchasePrice']
        venta =  soup['items'][0]['salePrice']
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def maxi():
    try:
        soup = BeautifulSoup(
            requests.get('http://www.maxicambios.com.py/', timeout=10).text, "html.parser")
        compra = soup.find_all(class_='lineas1')[0].contents[
            7].string.replace('.', '')
        venta = soup.find_all(class_='lineas1')[0].contents[
            5].string.replace('.', '')
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def alberdi():
    try:
        soup = json.loads(
            requests.get('http://www.cambiosalberdi.com/customscripts/ajax/getCotizaciones.php', timeout=10).text)
        compra =  soup['asuncion'][0]['compra'].replace('.','')
        venta = soup['asuncion'][0]['venta'].replace('.','')
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def bcp():
    try:
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/monedas', timeout=10,
                         headers={'user-agent': 'Mozilla/5.0'}).text, "html.parser")
        ref = soup.select(
            '#cotizacion-interbancaria > tbody > tr > td:nth-of-type(4)')[0].get_text()
        ref = ref.replace('.', '').replace(',', '.')
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante', timeout=10,
                         headers={'user-agent': 'Mozilla/5.0'}).text, "html.parser")
        compra_array = soup.find(
            class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(4)')
        venta_array = soup.find(
            class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(5)')
        posicion = len(compra_array) - 1
        compra = compra_array[posicion].get_text(
        ).replace('.', '').replace(',', '.')
        venta = venta_array[posicion].get_text().replace(
            '.', '').replace(',', '.')
    except requests.ConnectionError:
        compra, venta, ref = 0, 0, 0
    except:
        compra, venta, ref = 0, 0, 0

    return Decimal(compra), Decimal(venta), Decimal(ref)

def setgov():
    try:
        soup = BeautifulSoup(
            requests.get('http://www.set.gov.py/portal/PARAGUAY-SET', timeout=10).text, "html.parser")
        compra = soup.find_all(
            'span', style="font-family:arial,helvetica,sans-serif;").pop(0).select('span')[0].contents[
                     0].string.replace('.', '')[2::]
        venta = soup.find_all(
            'span', style="font-family:arial,helvetica,sans-serif;").pop(1).select('span')[0].contents[
                    0].string.replace('.', '')[2::]
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)

def interfisa(): 
    try:
        soup = BeautifulSoup(
            requests.get('https://www.interfisa.com.py', timeout=8).text, "html.parser")
        compra = soup.find_all(
            id="dolar_compra")[0].string.replace('.', '')
        venta = soup.find_all(
            id="dolar_venta")[0].string.replace('.', '')
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)

def create_json():
    mcompra, mventa = maxi()
    ccompra, cventa = chaco()
    acompra, aventa = alberdi()
    bcpcompra, bcpventa, bcpref = bcp()
    setcompra, setventa = setgov()
    intcompra, intventa = interfisa()
    respjson = {
        'dolarpy': {
            'cambiosalberdi': {
                'compra': acompra,
                'venta': aventa
            },
            'cambioschaco': {
                'compra': ccompra,
                'venta': cventa
            },
            'maxicambios': {
                'compra': mcompra,
                'venta': mventa
            },
            'bcp': {
                'compra': bcpcompra,
                'venta': bcpventa,
                'referencial_diario': bcpref
            },
            'set': {
                'compra': setcompra,
                'venta': setventa
            },
            'interfisa': {
                'compra' : intcompra,
                'venta'  : intventa
            }
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return json.dumps(respjson, indent=4, sort_keys=True, separators=(',', ': '), default=decimal_default)


def get_output():
    with open('dolar.json', 'r') as f:
        response = f.read()
    return response


def write_output():
    response = create_json()
    with open('dolar.json', 'w') as f:
        f.write(response)

write_output()
