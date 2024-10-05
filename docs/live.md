# URLs Management

```bash
➜ ./subscope.py live -h

usage: subscope.py live [-h] {add,list,delete} ...

positional arguments:
  {add,list,delete}
    add              Add a live subdomain
    list             List live subdomains
    delete           Delete live subdomains

options:
  -h, --help         show this help message and exit
```

## Usage
### Adding (updating) urls
#### We have multitple options for adding (updating) a url

```bash
  --scheme SCHEME                 # Scheme (http or https)
  --method METHOD                 # HTTP method
  --port PORT                     # Port number
  --status_code STATUS_CODE       # HTTP status code
  --scope {inscope,outscope}      # Scope of the live subdomain (e.g. inscope, outscope)
  --ip IP                         # IP address of the live subdomain
  --cdn_status {yes,no}           # Whether the live subdomain uses a CDN
  --cdn_name CDN_NAME             # Name of the CDN provider
  --title TITLE                   # Title of the live subdomain
  --webserver WEBSERVER           # Web server type (e.g. nginx)
  --webtech WEBTECH               # Web technologies (comma-separated)
  --cname CNAME                   # CNAME of the live subdomain
```

* Adding a url for a subdomain

  ```bash
  ➜ ./subscope.py live add https://www.tesla.com:443 www.tesla.com tesla.com tesla_wk

  2024-10-05 19:20:26 | success | adding live subdomain | live url https://www.tesla.com:443 added to subdomain www.tesla.com in domain tesla.com in workspace tesla_wk with details: scheme=None, method=None, port=None, status_code=None, scope=None, cdn_status=None, cdn_name=None, title=None, webserver=None, webtech=None, cname=None
  ```

* Add a subdomain with options

  ```bash
  ➜ ./subscope.py live add http://dev.tesla.com:80 dev.tesla.com tesla.com tesla_wk --scheme http --method GET --status_code 200 --port 80

  2024-10-05 19:22:08 | success | adding live subdomain | live url http://dev.tesla.com:80 added to subdomain dev.tesla.com in domain tesla.com in workspace tesla_wk with details: scheme=http, method=GET, port=80, status_code=200, scope=None, cdn_status=None, cdn_name=None, title=None, webserver=None, webtech=None, cname=None
  ```

* Updating a url (if you add an option different with current option, the subdomain updated)

  ```bash
  ➜ ./subscope.py live add http://dev.tesla.com:80 dev.tesla.com tesla.com tesla_wk --status_code 403

  2024-10-05 19:22:55 | success | updating live subdomain | live url http://dev.tesla.com:80 in subdomain dev.tesla.com in domain tesla.com in workspace tesla_wk with updates: {'status_code': 403}
  ```

### Listing urls
#### We have multitple options for listing urls

```bash
--scheme SCHEME               # Filter by scheme (http/https)
--method METHOD               # Filter by HTTP method
--port PORT                   # Filter by port
--status_code STATUS_CODE     # Filter by HTTP status code
--ip IP                       # Filter by IP address
--cdn_status {yes,no}         # Filter by CDN status
--cdn_name CDN_NAME           # Filter by CDN name
--title TITLE                 # Filter by title of the live subdomain
--webserver WEBSERVER         # Filter by webserver (e.g., nginx)
--webtech WEBTECH             # Filter by web technologies (comma-separated)
--cname CNAME                 # Filter by CNAME of the live subdomain
--create_time CREATE_TIME     # Filter by creation time
--update_time UPDATE_TIME     # Filter by last update time
--brief                       # Show only subdomain names (brief output)
--scope SCOPE                 # Filter by scope
```

* Show information about of a url

  ```bash
  ➜ ./subscope.py live list https://www.tesla.com:443 wwww.tesla.com tesla.com tesla_wk

  [
      {
          "url": "https://www.tesla.com:443",
          "subdomain": "www.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "scheme": https,
          "method": GET,
          "port": 443,
          "status_code": 200,
          "ip": 10.10.10.10,
          "cdn_status": yes,
          "cdn_name": aws,
          "title": website,
          "webserver": nginx,
          "webtech": null,
          "cname": null,
          "created_at": "2024-10-05 19:20:26",
          "updated_at": "2024-10-05 19:20:26"
      }
  ]
  ```

* show urls of a subdomain

  ```bash
  ➜ ./subscope.py live list '*' www.tesla.com tesla.com tesla_wk

  [
        {
            "url": "https://www.tesla.com:443",
            "subdomain": "www.tesla.com",
            "domain": "tesla.com",
            "workspace": "tesla_wk",
            "scheme": https,
            "method": GET,
            "port": 443,
            "status_code": 200,
            "ip": 10.10.10.10,
            "cdn_status": yes,
            "cdn_name": aws,
            "title": website,
            "webserver": nginx,
            "webtech": null,
            "cname": null,
            "created_at": "2024-10-05 19:20:26",
            "updated_at": "2024-10-05 19:20:26"
        }
  ]
  ```

* Show urls of a domain
  * Also you can list all urls your database (instead of `tesla_wk` placed `'*'`)

  ```bash
  ➜ ./subscope.py live list '*' '*' tesla.com tesla_wk

  [
      {
            "url": "https://www.tesla.com:443",
            "subdomain": "www.tesla.com",
            "domain": "tesla.com",
            "workspace": "tesla_wk",
            "scheme": https,
            "method": GET,
            "port": 443,
            "status_code": 200,
            "ip": 10.10.10.10,
            "cdn_status": yes,
            "cdn_name": aws,
            "title": website,
            "webserver": nginx,
            "webtech": null,
            "cname": null,
            "created_at": "2024-10-05 19:20:26",
            "updated_at": "2024-10-05 19:20:26"
      },
      {
          "url": "http://dev.tesla.com:80",
          "subdomain": "dev.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "scheme": "http",
          "method": "GET",
          "port": 80,
          "status_code": 403,
          "ip": null,
          "cdn_status": null,
          "cdn_name": null,
          "title": null,
          "webserver": null,
          "webtech": null,
          "cname": null,
          "created_at": "2024-10-05 19:22:08",
          "updated_at": "2024-10-05 19:22:55"
      }
  ]
  ```

* List urls

  ```bash
  ➜ ./subscope.py live list '*' '*' '*' '*' --brief
  https://www.tesla.com:443
  http://dev.tesla.com:80

  ➜ ./subscope.py live list '*' '*' '*' tesla_wk --brief
  https://www.tesla.com:443
  http://dev.tesla.com:80

  ➜ ./subscope.py live list '*' '*' tesla.com tesla_wk --brief
  https://www.tesla.com:443
  http://dev.tesla.com:80

  ➜ ./subscope.py live list '*' www.tesla.com tesla.com tesla_wk --brief
  https://www.tesla.com:443
  ```


* list subdomains based on filtering

  ```bash
  ➜ ./subscope.py live list '*' '*' '*' '*' --brief --status_code 403 
  http://dev.tesla.com:80

  ➜ ./subscope.py live list '*' '*' '*' '*' --brief --cdn_status yes
  https://www.tesla.com:443

  ➜ ./subscope.py live list '*' '*' '*' '*' --port 443 --brief 
  https://www.tesla.com:443
  ```

* list urls based on timestamp

  ```bash
  # All urs create at year 2024
  ➜ ./subscope.py live list '*' '*' '*' '*' --create_time 2024 --brief
  www.tesla.com
  mail.tesla.com
  api.tesla.com
  dev.walmart.com
  api.walmart.com

  # All urls update in data `2024-10-05`
  ➜ ./subscope.py live list '*' '*' '*' '*' --create_time 2024 --brief
  https://www.tesla.com:443
  http://dev.tesla.com:80

  # All urls update in `2024-10-05-18:04`
  ➜ ./subscope.py live list '*' '*' '*' '*' --update_time 2024-10-05-18:04 --brief
  https://www.tesla.com:443

  # All urls update in `2024-10-05-18:05 until 2024-10-05-18:10`
  ➜ ./subscope.py live list '*' '*' '*' '*' --update_time 2024-10-05-18:05,2024-10-05-18:10 --brief
  http://dev.tesla.com:80
  ```

### Deleting urls
#### We have multitple options for deleting urls

```bash
  --scope SCOPE               # Filter by scope (e.g., inscope or outscope)
  --scheme SCHEME             # Filter by scheme (http/https)
  --method METHOD             # Filter by HTTP method
  --port PORT                 # Filter by port
  --status_code STATUS_CODE   # Filter by HTTP status code
  --ip IP                     # Filter by IP address
  --cdn_status {yes,no}       # Filter by CDN status
  --cdn_name CDN_NAME         # Filter by CDN name
  --title TITLE               # Filter by title of the live subdomain
  --webserver WEBSERVER       # Filter by webserver (e.g., nginx)
  --webtech WEBTECH           # Filter by web technologies (comma-separated)
  --cname CNAME               # Filter by CNAME of the live subdomain
  --create_time CREATE_TIME   # Filter by creation time
  --update_time UPDATE_TIME   # Filter by last update time
```

* Deleting a single urls

  ```bash
  ➜ ./subscope.py live delete https://www.tesla.com:443 www.tesla.com tesla.com tesla_wk

  2024-10-05 19:46:25 | success | deleting live subdomain | deleted 1 live entries for workspace tesla_wk with filters: subdomain=www.tesla.com, domain=tesla.com, url=https://www.tesla.com:443, scope=None, scheme=None, method=None, port='None', status_code='None', ip_address='None', cdn_status='None', cdn_name=None, title=None, webserver=None, webtech=None, cname=None
  ```

* Deleting all urls of a subdomain

  ```bash
  ➜ ./subscope.py live delete '*' www.tesla.com tesla.com tesla_wk

  2024-10-05 19:49:11 | success | deleting live subdomain | deleted 1 live entries for workspace tesla_wk with filters: subdomain=www.tesla.com, domain=tesla.com, url=*, scope=None, scheme=None, method=None, port='None', status_code='None', ip_address='None', cdn_status='None', cdn_name=None, title=None, webserver=None, webtech=None, cname=None
  ```

* Deleting all urls of a domain

  ```bash
  ➜ ./subscope.py live delete '*' '*' tesla.com tesla_wk

  2024-10-05 19:49:11 | success | deleting live subdomain | deleted 1 live entries for workspace tesla_wk with filters: subdomain=*, domain=tesla.com, url=*, scope=None, scheme=None, method=None, port='None', status_code='None', ip_address='None', cdn_status='None', cdn_name=None, title=None, webserver=None, webtech=None, cname=None
  ```

* Deleting all urls of a workspace

  ```bash
  ➜ ./subscope.py live delete '*' '*' '*' tesla_wk

  2024-10-05 19:49:11 | success | deleting live subdomain | deleted 1 live entries for workspace tesla_wk with filters: subdomain=*, domain=*, url=*, scope=None, scheme=None, method=None, port='None', status_code='None', ip_address='None', cdn_status='None', cdn_name=None, title=None, webserver=None, webtech=None, cname=None
  ```

* Deleting urls based on filteres

  ```bash
  ➜ ./subscope.py live  delete '*' '*' '*' '*' --status_code 403

  2024-10-05 20:00:01 | success | deleting live subdomain | deleted 1 live entries for workspace * with filters: subdomain=*, domain=*, url=*, scope=None, scheme=None, method=None, port='None', status_code='403', ip_address='None', cdn_status='None', cdn_name=None, title=None, webserver=None, webtech=None, cname=None

  ➜ ./subscope.py live  delete '*' '*' '*' '*' --method GET

  2024-10-05 20:00:01 | success | deleting live subdomain | deleted 1 live entries for workspace * with filters: subdomain=*, domain=*, url=*, scope=None, scheme=None, method='GET', port='None', status_code='None', ip_address='None', cdn_status='None', cdn_name=None, title=None, webserver=None, webtech=None, cname=None
  ```
