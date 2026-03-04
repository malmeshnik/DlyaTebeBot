import hmac, hashlib

bot_token = "8411892294:AAEtwp8ulAqI2KTDt11IQpPx8ph6QUcW-Pg"  # <-- вставте сюди
expected = "e6907c4fc8d0be302039e2fbd6c337cf04a84ffe34036667e84c703a845107d0"

base = (
    "auth_date=1772632199\n"
    "query_id=AAHTlDI6AAAAANOUMjqLJ5Ai\n"
    'user={{"id":976393427,"first_name":"Андрій","last_name":"",'
    '"username":"malteshn","language_code":"en","is_premium":true,'
    '"allows_write_to_pm":true,"photo_url":"https:{slash}t.me{slash}i{slash}userpic'
    '{slash}320{slash}4gb7aaozfDNrgWpoDzZxMKe0iR3yz5AOXXHZ0t74k2g.svg"}}'
)

secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

for slash in ["//", "\\/\\/", "\\/", "\\/"]:
    s = base.format(slash=slash)
    result = hmac.new(secret_key, s.encode(), hashlib.sha256).hexdigest()
    print(f"slash={repr(slash):10} match={result == expected} hash={result[:16]}...")