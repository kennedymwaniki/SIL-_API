import requests

access_token = "ya29.a0AeXRPp56IihZiXkPWDylEEwsAOuZIe2C0PBUvTF_2qOyxuOWli-2-fRMl2l6J8-taGu-IqSHYO9BXvZPYuFJmLwIWtilwYTTHOKKapUHsz4ns_ePoEjc5usSyZ_TbpPQY8zTqvl4kwjmmloPi4cy-EsijbZ1N9NWSW51WWmI6gaCgYKAaISARISFQHGX2MiGe0H_bLgTHd3Jyyv8n2yJg0177"

response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}")
print(response.json()) #if invalidis the response {"error": "invalid_token"} need to refresh it
print(response.status_code)

# test casefor how access and refresh token

# kennedymk128@gmail.com
#  the acces and refresh token include
# {
#   "access_token": "ya29.a0AeXRPp6E-1G2Cel666dkWRCAIV2gViLMYAZkT65jNkHyRF_VRuonMiIRHsnfkKRgJX0_9Wz3SwkvSlZJSH6FQo2xGQtVwrB-EN7vPgBqUbXx6W4oUCvrumqS5_CClzT8OTLdNulXE1uG4h_B760mo78tajz72_5Ts5SujFZWaCgYKAcISARMSFQHGX2Mi4YpmZdrL8fEFBc-vbg51QA0175",
#   "refresh_token": "1//03i1yK_TQFnPgCgYIARAAGAMSNwF-L9IrKfZdId06HTmLHQmnBE9E7Ythcti4ms0wYTQBWam5aY9w5v4rgKzl97Dcp_LKzLNvuWc",
#   "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjgyMWYzYmM2NmYwNzUxZjc4NDA2MDY3OTliMWFkZjllOWZiNjBkZmIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0NjE2NjY3MjY2NzgtNG5lN3ZpZXBoZzNiOHFrb3RjMWQ1YmcwMWk5ZmgzbjguYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0NjE2NjY3MjY2NzgtNG5lN3ZpZXBoZzNiOHFrb3RjMWQ1YmcwMWk5ZmgzbjguYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTc4NDUwMzc3NzQ4NTEzMTY5MDkiLCJlbWFpbCI6Imtlbm5lZHltazEyOEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6IlBDZXUwMFVueFpITVVJQlEwT2t3LVEiLCJuYW1lIjoiS2VubmVkeSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMXzdhb01YUmFPMWVLN0Q5akFsV1BlVmhLNG5RQWp3RVBfVFdRNlFvOENuZ29pdXc9czk2LWMiLCJnaXZlbl9uYW1lIjoiS2VubmVkeSIsImlhdCI6MTc0MzA5NzM2MSwiZXhwIjoxNzQzMTAwOTYxfQ.TIV4Z5ocRewVUm6u4FVlcmpdu_aUViWelWAweK9ZgZjRVCCVKeeAWRPKHVV6htjn-52c-UUaI6G-ug4fwqNUTf_n0ILE70HFwHUVsgQ47sHvIFucfyHi4zI8yp8vohFbZKHPlXZLjYDk9TWdNQ7xJva9tz-vE-DilNnCW5CKzZ_x4B2mQ8_upaW0qza0ZhOxPLowwkGfQh9EO-Df-hKh7UjgSQ8TS3a3XCp_68Tuj1aOHAANSeyYK_iNJYh3uN5gjV__eOAyMyiDNDaI7cBFwuDOQHc1J_t125atypc0WVra4M58nfJCL-Gah64yUtSZ_Y0n2h1Ag2OxYDWP0L2HPg",
#   "user_info": {
#     "sub": "117845037774851316909",
#     "name": "Kennedy",
#     "given_name": "Kennedy",
#     "picture": "https://lh3.googleusercontent.com/a/ACg8ocL_7aoMXRaO1eK7D9jAlWPeVhK4nQAjwEP_TWQ6Qo8Cngoiuw=s96-c",
#     "email": "kennedymk128@gmail.com",
#     "email_verified": true
#   }
# }