import httpx

url = "https://api.nbrb.by/exrates/rates"
params = {"periodicity": 0}

r = httpx.get(url, params=params)

print(r)
print(r.url)
print(r.status_code)
print(r.text)
print(r.json())
