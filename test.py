import httpx

cookies = {
    "XSRF-TOKEN": "eyJpdiI6IklVMnJodTZXRTlWS2hHY3N2a1pITWc9PSIsInZhbHVlIjoiaXJXdmVwUnJWdHJwYU85aVRuOWRFbkhjR2Y1MDJ3THRkZWlrWVR6MEdxRjgvMSt5RXRqU1Fsei9sanBIQk9pSHpNbjhlZ1BnZDd0ZnZGZEJlelgvbjNvc2RxZE1oVEF0bWtxbHdaejBKQklCUDF4aElZZGVVUWIrU1Nzcms4WXQiLCJtYWMiOiJjZTNjZTUxYjJiMDEwNTNhNTQ0ZDBlM2EzNjIzMDJiM2RlZWY5MGEyMjNlNzA1NTYzMmRlZGRiMmI5NWU1MWI1IiwidGFnIjoiIn0%3D",
    "normans_session": "eyJpdiI6IlV6WDRHelo5QWNDWWQrVWx1dStRcWc9PSIsInZhbHVlIjoiMk1KNjdjaEtBMEpSdUxoYmVqSU82aUNWQ1p5ajQxaXZBRG9sc1o2VENHNHB0K20yNWZMRUhRUXlONWpTLzlKY0JXOWxFbnVkS29McnE3Z3ZiYm5JdmJCVnRzZDYrMTlCcHFKOWFObytYN3pjTUpzcEwvYXdWcTU5cTdpUCs3eCsiLCJtYWMiOiJhZThmNTBjZWNlNzBhMjRmMDY0NjI2NDAzMGUzNjIwM2U2YWE1MWI1NmVhNDhhZDUyYWYyNzJlMDE1N2I5ODA1IiwidGFnIjoiIn0%3D"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}

r = httpx.get("https://www.normans.mobi/events", headers=headers, cookies=cookies)

print(r.text)