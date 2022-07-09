#!/usr/bin/env python3

import sys
import string
import json
import zipfile
from random import choice, randint, shuffle, normalvariate, choices, uniform

import faker

class AttrDict(dict):
    def __getattr__(self, k):
        return self[k]


faker = faker.Faker([
        'en_US',
        'ja_JP',
        'es_MX',
        'zh_CN',
        'ru_RU',
        'pt_BR',
#        'bn_IN',
        'ar_EG',
        'fa_IR',
        'he_IL',
        'uk_UA',
        ])


def customer():
        locale = choice(faker.locales)
        fake = faker[locale]
        tz = fake.pytimezone()
        dob = fake.date_of_birth(minimum_age=17, maximum_age=72)
        geo = fake.local_latlng(country_code=locale.split('_')[1])
        privacy_conscious = uniform(0,1) < 0.2
        return AttrDict(customerid=randint(1000, 99999),
             name=fake.name(),
             address=fake.address(),
             birthdate=str(dob) if not privacy_conscious else None,
             phone=fake.phone_number(),
             timezone=fake.timezone(),
             geo=dict(lat=geo[0], long=geo[1]),
             locale=locale)


def randomize(s):
    if len(s) == 1:
        if s == 'x': s = string.ascii_lowercase
        elif s == 'X': s = string.ascii_uppercase
        elif s == '0': s = string.digits
        return choice(s)

    return ''.join(randomize(c) for c in s)


def product():
    sz = randint(1, 10)
    return AttrDict(sku=randomize('XXX0000'),
            desc='',
            weight_kg=round(normalvariate(sz*2, sz/5), 1),
            dims_cm=sorted([round(normalvariate(sz, sz/3),1) for i in range(3)], reverse=True),
            baseprice=round(normalvariate(sz*100, sz*20), 2)
            )


def order():
    locale = choice(faker.locales)
    fake = faker[locale]
    dt = fake.date_time_this_year()
    c = choice(customers)
    items = []
    for p in choices(products, k=randint(1, 4)):
        items.append(AttrDict(
            sku=p.sku,
            qty=randint(1, 5),
            price=round(uniform(.9, 1.1)*p.baseprice, 2),
        ))

    return AttrDict(orderid=f'{randint(1000, 99999):06d}',
                customerid=c['customerid'],
                timestamp=dt.isoformat(),
                amount_paid=sum(x.price*x.qty for x in items),
                items=items
                )

products=[product() for i in range(10)]
customers=[customer() for i in range(500)]
orders=[order() for i in range(100)]

def write_jsonl(fp, d):
    fp.write(json.dumps(d).encode()+b'\n')

with zipfile.ZipFile(sys.argv[1], mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
    with zf.open('products.jsonl', mode='w') as fp:
        for x in products:
            write_jsonl(fp, x)

    with zf.open('customers.jsonl', mode='w') as fp:
        for x in customers:
            write_jsonl(fp, x)

    with zf.open('orders.jsonl', mode='w') as fp:
        for x in orders:
            write_jsonl(fp, x)
