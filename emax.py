#https://github.com/man-c/pycoingecko
import os
from pycoingecko import CoinGeckoAPI
last_value = None

file = "/tmp/emax_price.txt"

# get quote
cg = CoinGeckoAPI()
quote = cg.get_price(ids='EthereumMax', vs_currencies='usd')
price = quote['ethereummax']['usd']

os.system("aws s3 cp s3://voll-bucket-test/emax_price.txt %s" % file)
f = open(file, "r")
last_value = float(f.read())
f.close()


if last_value:
	change = int(((price - last_value)/last_value * 100))
else:
	change = 0

access_token = os.getenv('access_token')
secret_token = os.getenv('secret_token')

# formatting
url = "https://api.voicemonkey.io/trigger?access_token={access_token}&secret_token={secret_token}&monkey=max-monkey&announcement=EMAX%20Boosted%20{delta}%20Percent%20Today&voice=Salli".format(delta = change, access_token = access_token, secret_token = secret_token)
request = "curl -X POST -H 'Content-type: application/json' --data '{}' '%s'" % url

print("EMAX changed: %s" % change)

# # Launch da rockets?
if change > 10:
	f = open(file, "w")
	f.write(str(price))
	f.close()
	os.system("aws s3 cp %s s3://voll-bucket-test/emax_price.txt" % file)
	# check return code on request to catch issues
	os.system(request)

