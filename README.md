# ebk-client - an eBay Kleinanzeigen API client
ebk-client is a small library to use the eBay Kleinanzeigen/Classifieds API.  

## Usage
Besides the normal user account which can be registered at [ebay-kleinanzeigen.de](https://www.ebay-kleinanzeigen.de), a special partner eBay partner account is required to use the eBay Kleinanzeigen/Classifieds API.  
The smartphone apps (e.g. for Android) must include also some static/hardcoded partner account as it is using the same API (further information on this can be found [here](https://euer.krebsco.de/finding-the-ebay-kleinanzeigen-application-password.html)).

### Code example:
```python
api = EbkClient('app-username', 'app-password', 'ebay-user-name', 'ebay-user-password')
my_ads = api.get_my_ads()
```

## Documentation
No ebk-client doc available yet.  
The official documentation of the eBay Kleinanzeigen/Classifieds API is unfortunately not anymore available. An older copy - retrieved over the [Internet Archive](https://web.archive.org/) - can be found in the [docs folder](docs): entry point is docs/pages/home.html.

## Requirements
 * Python 3.6+
 * dateutil (example.py only)
