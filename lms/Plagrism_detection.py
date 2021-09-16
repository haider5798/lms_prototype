import requests

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/93.0.4577.63 Mobile Safari/537.36 Edg/93.0.961.38',
    'Accept': 'application/json',
    'Referer': 'https://www.grammarly.com/plagiarism-checker?q=plagiarism&utm_source=google&utm_medium=cpc&utm_'
               'campaign=11903460924&utm_content=487967677567&utm_term=avoid%20plagiarism%20online&matchtype='
               'b&placement=&network=g&gclid=CjwKCAjwyvaJBhBpEiwA8d38vNRCx4B40BeSTW5NJQaoCVdG_34D8kvu5DUMMT8N3WcNa'
               '1FBnlOGTRoCdS0QAvD_BwE&gclsrc=aw.ds',
    'Connection': 'keep-alive',
    'x-csrf-token': 'AABJqc0MaVJVZlb+tHtdfIR8qADhFcUS7sKaOA'

}
api_url = 'https://capi.grammarly.com/api/check'

text_data = "Notwithstanding anything contained in paragraph (b) of clause (3), within a period of two years" \
            " from the commencing day, the appropriate Legislature shall bring the laws specified in 18[Part II " \
            "of the First Schedule] 18 into conformity with the rights conferred by this"

response = requests.post(api_url, data=text_data, headers=headers)
print(response)
data = response.json()
print(data)
