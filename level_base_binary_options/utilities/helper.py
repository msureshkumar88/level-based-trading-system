import hashlib
import requests
import csv


class Helper:
    @classmethod
    def password_encrypt(cls, password):
        h = hashlib.new('ripemd160')
        h.update(password.encode('utf-8'))
        return h.hexdigest()

    @classmethod
    def get_fx_feed_url(cls):
        return 'https://webrates.truefx.com/rates/connect.html?f=csv'

    @classmethod
    def fx_request_url(cls, pair):
        return Helper.get_fx_feed_url() + "&c=" + pair

    @classmethod
    def get_current_price(cls, currency):
        # check this function to get the value from database
        with requests.Session() as s:
            download = s.get(Helper.fx_request_url(currency))

            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for row in my_list:
                if len(row) != 0:
                    bid = float(row[2] + row[3])
                    offer = float(row[4] + row[5])
                    mid_price = (bid + offer) / 2
                    return "%.5f" % mid_price
