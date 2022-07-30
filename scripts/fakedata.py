#!/usr/bin/env python3

'''
Usage: $0 <outfile.zip> [<level>]

Generate 10^<level> amount of data and store in outfile.zip.
'''

import sys
import string
import json
import zipfile
from random import choice, randint, normalvariate, choices, uniform

import faker


class AttrDict(dict):
    def __getattr__(self, k):
        return self[k]


def randomize(s):
    if len(s) == 1:
        if s == 'x': s = string.ascii_lowercase
        elif s == 'X': s = string.ascii_uppercase
        elif s == '0': s = string.digits
        return choice(s)

    return ''.join(randomize(c) for c in s)

def descs(s):
    return list(x.capitalize() for x in s.split())

def between(a, b, round=2):
    r = normalvariate((a+b)/2, (b-a)/5)
    r = max(a, r)
    r = min(b, r)
    return __builtins__.round(r, round)

class RandomDict(dict):
    def __getitem__(self, k):
        return choice(self.get(k))

def random_increasing(n):
    id = 1000
    while True:
        id += randint(1, n)
        yield id

class FakeBusiness:
    desc_words = RandomDict(
        opmode=descs('automatic manual mechanical electric power super mega ultra handmade vintage mini '),
        material=descs('steel lead leather iron stone pewter silver gold bronze ivory'),
        color=descs('blue yellow green mauve puce azure pearl white gold orange amber red mahogany magenta purple'),
        food=descs('carrot peanut steak fajita tuna lettuce hamburger barbecue garlic candy apple melon cherry coffee bread spice chocolate mushroom cereal egg butter coconut potato onion cabbage cashew soybean lobster salad sandwich pie pizza'),
        utensil=descs('knife bowl cup tongs spatula strainer scale pan crusher scoop'),
        gadget=descs('widget blender mixer crockpot timer toaster'),
        computer_adj=descs("wireless bluetooth network cellular women's"),
        computer=descs('laptop keyboard monitor modem printer webcam router'),
    )

    desc_templs = [
        '{opmode} {food} {utensil}',
        '{utensil}',
        '{color} {utensil}',
        '{material} {utensil}',
        '{opmode} {gadget} ({color})',
        '{opmode} {gadget}',
        '{computer_adj} {computer}',
    ]

    def __init__(self, level=1):
        self._level = level
        self.level = int(level)
        self.skuprefixes = [randomize('XX') for i in range(2**self.level)]
        self.uniqskus = {}

        self.faker = faker.Faker([
            'en_US', 'ja_JP', 'uk_UA', 'ar_EG', 'pt_BR', 'fa_IR', 'zh_CN',
#            'es_MX', 'he_IL', #'bn_IN',
        ])

        self.customerid = random_increasing(2**self.level)

        nproducts, ncustomers, norders = 1, 2, 3
        if self.level > 0:
            nproducts = int(1*10**level)
            ncustomers = int(5*10**level)
            norders = int(10*10**level)

        self.products=[self.product() for i in range(nproducts)]
        self.customers=[self.customer() for i in range(ncustomers)]
        self.orders=[self.order(maxitems=2**self.level) for i in range(norders)]

    def description(self):
        return choice(self.desc_templs).format_map(self.desc_words).strip()

    def sku(self):
        r = choice(self.skuprefixes)+randomize('0'*(self.level+1))
        if r in self.uniqskus:
            return self.sku()
        self.uniqskus[r] = 'taken'
        return r

    def product(self):
        sz = randint(1, self.level)
        baseprice = between(5**(sz-1), 2**(sz+1), round=0)
        baseprice += choice([.0, .50, .90, .95, .99])
        return AttrDict(sku=self.sku(),
                desc=self.description(),
                baseprice=baseprice,
                weight_kg=between(4**sz, 2**(sz+1), round=1),
                dims_cm=sorted([between(1.5, 25, round=1) for i in range(3)], reverse=True),
                )

    def customer(self):
        locale = choice(self.faker.locales)
        fake = self.faker[locale]
        tz = fake.pytimezone()
        dob = fake.date_of_birth(minimum_age=17, maximum_age=72)
        geo = fake.local_latlng(country_code=locale.split('_')[1])
        privacy_conscious = uniform(0,1) < 0.2
        return AttrDict(customerid=next(self.customerid),
             name=fake.name(),
             address=fake.address(),
             birthdate=str(dob) if not privacy_conscious else None,
             phone=fake.phone_number(),
             timezone=fake.timezone(),
             geo=dict(lat=geo[0], long=geo[1]),
             locale=locale)

    def order(self, maxitems=3):
        locale = choice(self.faker.locales)
        fake = self.faker[locale]
        dt = fake.date_time_this_year()
        c = choice(self.customers)
        items = []
        for p in choices(self.products, k=randint(1, maxitems)):
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


def write_jsonl(fp, d):
    fp.write(json.dumps(d).encode()+b'\n')


def main(outfn, level=1):
    level = float(level)
    fake = FakeBusiness(level)

    with zipfile.ZipFile(outfn, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        with zf.open('products.jsonl', mode='w') as fp:
            for x in fake.products:
                write_jsonl(fp, x)

        with zf.open('customers.jsonl', mode='w') as fp:
            for x in fake.customers:
                write_jsonl(fp, x)

        with zf.open('orders.jsonl', mode='w') as fp:
            for x in fake.orders:
                write_jsonl(fp, x)


if __name__ == '__main__':
    main(*sys.argv[1:])
