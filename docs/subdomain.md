# Subdomain Management

```bash
➜ ./subscope.py subdomain -h

usage: subscope.py subdomain [-h] {add,list,delete} ...

positional arguments:
  {add,list,delete}
    add              Add a subdomain
    list             List subdomains
    delete           Delete subdomains

options:
  -h, --help         show this help message and exit
```

## Usage
### Adding (updating) subdomain
#### We have multitple options for adding (updating) a subdomain

```bash
--source [SOURCE ...]         # Source(s) (comma-separated)
--scope {inscope,outscope}    # Scope (default: inscope)
--resolved {yes,no}           # Resolved status (yes or no)
--ip IP                       # IP address of the subdomain
--cdn_status {yes,no}         # Whether the subdomain uses a cdn_status
--cdn_name CDN_NAME           # Name of the CDN provider
```

* Adding a subdomain for a domain in a workspace (Default mode)

  ```bash
  ➜ ./subscope.py subdomain add www.tesla.com tesla.com tesla_wk

  2024-10-05 05:40:42 | success | adding subdomain | Subdomain www.tesla.com added to domain tesla.com in workspace tesla_wk with sources: , scope: inscope, resolved: no, IP: none, cdn_status: no, CDN Name: none

  # The souce column is Empty
  # Source can set to `crtsh`, `subfinder`, `dns_bruteforce` and etc
  ```

* Add a subdomain with options

  ```bash
  ➜ ./subscope.py subdomain add mail.tesla.com tesla.com tesla_wk --ip 10.10.10.10 --resolved yes --source dns_bruteforce

  2024-10-05 05:46:51 | success | adding subdomain | Subdomain mail.tesla.com added to domain tesla.com in workspace tesla_wk with sources: dns_bruteforce, scope: inscope, resolved: yes, IP: 10.10.10.10, cdn_status: no, CDN Name: none
  ```

* Updating a subdomain (if you add an option different with current option, the subdomain updated)

  ```bash
  ➜ ./subscope.py subdomain add mail.tesla.com tesla.com tesla_wk --ip 10.20.30.40

  2024-10-05 05:49:05 | success | updating subdomain | subdomain mail.tesla.com in domain tesla.com in workspace tesla_wk with updates: {'ip_address': '10.20.30.40'}
  ```

* Add a subdomain with multitle sources

  ```bash
  ➜ ./subscope.py subdomain add api.tesla.com tesla.com tesla_wk --scope outscope --source crtsh dns_bruteforce

  2024-10-05 05:56:51 | success | adding subdomain | Subdomain api.tesla.com added to domain tesla.com in workspace tesla_wk with sources: crtsh, dns_bruteforce, scope: outscope, resolved: no, IP: none, cdn_status: no, CDN Name: none
  ```

### Listing subdomains
#### We have multitple options for listing subdomains

```bash
--source [SOURCE ...]           # Filter by source(s)
--source-only                   # Show only subdomains matching the specified source(s)
--scope {inscope,outscope}      # Filter by scope
--resolved {yes,no}             # Filter by resolved status
--cdn_status {yes,no}           # Filter by cdn_status status
--ip IP                         # Filter by IP address
--cdn_name CDN_NAME             # Filter by CDN provider name
--brief                         # Show only subdomain names
--create_time CREATE_TIME       # Filter by creation time
--update_time UPDATE_TIME       # Filter by last update time
```

* Show information about of a subdomain

  ```bash
  ➜ ./subscope.py subdomain list api.tesla.com tesla.com tesla_wk

  [
      {
          "subdomain": "api.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "source": "crtsh, dns_bruteforce",
          "scope": "outscope",
          "resolved": "no",
          "ip_address": "none",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 05:56:51",
          "updated_at": "2024-10-05 05:56:51"
      }
  ]
  ```

* show subdomains of a domain

  ```bash
  ➜ ./subscope.py subdomain list '*' tesla.com tesla_wk

  [
      {
          "subdomain": "mail.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "source": "dns_bruteforce",
          "scope": "inscope",
          "resolved": "yes",
          "ip_address": "10.20.30.40",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 05:46:51",
          "updated_at": "2024-10-05 05:49:05"
      },
      {
          "subdomain": "api.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "source": "crtsh, dns_bruteforce",
          "scope": "outscope",
          "resolved": "no",
          "ip_address": "none",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 05:56:51",
          "updated_at": "2024-10-05 05:56:51"
      }
  ]
  ```

* Show subdomains of a workspace
  * Also you can list all subdomains your database (instead of `tesla_wk` placed `'*'`)

  ```bash
  ➜ ./subscope.py subdomain list '*' '*' tesla_wk

  [
      {
          "subdomain": "www.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "source": "",
          "scope": "inscope",
          "resolved": "no",
          "ip_address": "none",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 05:40:42",
          "updated_at": "2024-10-05 05:40:42"
      },
      {
          "subdomain": "api.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "source": "crtsh, dns_bruteforce",
          "scope": "outscope",
          "resolved": "no",
          "ip_address": "none",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 05:56:51",
          "updated_at": "2024-10-05 05:56:51"
      },
      {
          "subdomain": "www.teslamotor.com",
          "domain": "teslamotor.com",
          "workspace": "tesla_wk",
          "source": "crtsh",
          "scope": "inscope",
          "resolved": "no",
          "ip_address": "none",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 06:04:19",
          "updated_at": "2024-10-05 06:04:52"
      }
  ]
  ```

* list subdomain names

  ```bash
  ➜ ./subscope.py subdomain list '*' '*' '*' --brief
  www.tesla.com
  api.tesla.com
  www.teslamotor.com
  dev.walmart.com

  ➜ ./subscope.py subdomain list '*' '*' tesla_wk --brief
  www.tesla.com
  api.tesla.com
  www.teslamotor.com

  ➜ ./subscope.py subdomain list '*' tesla.com tesla_wk --brief
  www.tesla.com
  api.tesla.com

  ➜ ./subscope.py subdomain list www.tesla.com tesla.com tesla_wk --brief
  www.tesla.com
  ```

* list subdomains based on `source` filtering

  ```bash
  ➜ ./subscope.py subdomain list '*' tesla.com tesla_wk --source crtsh

  [
      {
          "subdomain": "api.tesla.com",
          "domain": "tesla.com",
          "workspace": "tesla_wk",
          "source": "crtsh, dns_bruteforce",
          "scope": "outscope",
          "resolved": "no",
          "ip_address": "none",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 05:56:51",
          "updated_at": "2024-10-05 05:56:51"
      }
  ]

  # only `crtsh` in source column
  ➜ ./subscope.py subdomain list '*' '*' '*' --source crtsh --source-only

  [
      {
          "subdomain": "www.teslamotor.com",
          "domain": "teslamotor.com",
          "workspace": "tesla_wk",
          "source": "crtsh",
          "scope": "inscope",
          "resolved": "no",
          "ip_address": "none",
          "cdn_status": "no",
          "cdn_name": "none",
          "created_at": "2024-10-05 06:04:19",
          "updated_at": "2024-10-05 06:04:52"
      }
  ]
  ```

* list subdomains based on other filtering

  ```bash
  ➜ ./subscope.py subdomain list '*' '*' '*' --resolved no --brief 
  www.tesla.com
  api.tesla.com
  www.teslamotor.com

  ➜ ./subscope.py subdomain list '*' '*' '*' --ip 20.3.1.99 --brief
  dev.walmart.com

  ➜ ./subscope.py subdomain list '*' '*' '*' --scope inscope --brief 
  www.tesla.com
  www.teslamotor.com

  ➜ ./subscope.py subdomain list '*' '*' '*' --scope outscope --brief
  api.tesla.com

  ➜ ./subscope.py subdomain list '*' '*' '*' --cdn_status yes --brief
  dev.walmart.com
  api.walmart.com

  ➜ ./subscope.py subdomain list '*' '*' '*' --cdn_name aws --brief
  dev.walmart.com
  ```

* list subdomains based on timestamp

  ```bash
  # All subdomains create at year 2024
  ➜ ./subscope.py subdomain list '*' '*' '*' --create_time 2024 --brief
  www.tesla.com
  mail.tesla.com
  api.tesla.com
  dev.walmart.com
  api.walmart.com

  # All subdomains update in data `2024-10-05`
  ➜ ./subscope.py subdomain list '*' '*' '*' --update_time 2024-10-05 --brief
  www.tesla.com
  mail.tesla.com
  api.tesla.com
  dev.walmart.com
  api.walmart.com

  # All subdomains update in `2024-10-05-18:04`
  ➜ ./subscope.py subdomain list '*' '*' '*' --update_time 2024-10-05-18:04 --brief
  www.tesla.com
  mail.tesla.com
  api.tesla.com

  # All subdomains update in `2024-10-05-18:05 until 2024-10-05-18:10`
  ➜ ./subscope.py subdomain list '*' '*' '*' --update_time 2024-10-05-18:05,2024-10-05-18:10 --brief
  dev.walmart.com
  api.walmart.com
  ```

### Deleting subdomains
#### We have multitple options for deleting subdomains

```bash
--resolved {yes,no}           # Filter by resolved status
--source SOURCE               # Filter by source
--scope {inscope,outscope}    # Filter by scope
--ip IP                       # Filter by IP address
--cdn_status {yes,no}         # Filter by cdn_status
--cdn_name CDN_NAME           # Filter by CDN name
```

* Deleting a single subdomain
  
  ```bash
  ➜ ./subscope.py subdomain delete www.tesla.com tesla.com tesla_wk

  2024-10-05 18:29:43 | success | deleting subdomain | deleted 1 matching entries from subdomains table with filters: subdomain=www.tesla.com, domain=tesla.com, workspace=tesla_wk
  2024-10-05 18:29:43 | success | deleting subdomain | deleted 1 matching entries from live table with filters: subdomain=www.tesla.com, domain=tesla.com, workspace=tesla_wk
  ```

* Deleting all subdomains of a domain

  ```bash
  ➜ ./subscope.py subdomain delete '*' tesla.com tesla_wk

  2024-10-05 18:36:03 | success | deleting subdomain | deleted 2 matching entries from subdomains table with filters: subdomain=*, domain=tesla.com, workspace=tesla_wk
  ```

* Deleting all subdomains of a workspace

  ```bash
  ➜ ./subscope.py subdomain delete '*' '*' tesla_wk

  2024-10-05 18:36:03 | success | deleting subdomain | deleted 2 matching entries from subdomains table with filters: subdomain=*, domain='*', workspace=tesla_wk
  ```

* Deleting subdomains based on filteres

  ```bash
  ➜ ./subscope.py subdomain delete '*' '*' '*' --scope outscope

  2024-10-05 18:38:59 | success | deleting subdomain | deleted 1 matching entries from subdomains table with filters: subdomain=*, scope=outscope

  ➜ ./subscope.py subdomain delete '*' '*' '*' --resolved no

  2024-10-05 18:48:53 | success | deleting subdomain | deleted 1 matching entries from subdomains table with filters: subdomain=*, resolved=no

  ➜ ./subscope.py subdomain delete '*' '*' '*' --ip 10.10.10.10

  2024-10-05 18:48:53 | success | deleting subdomain | deleted 1 matching entries from subdomains table with filters: subdomain=*, ip_address=10.10.10.10

  ➜ ./subscope.py subdomain delete '*' '*' '*' --cdn_status yes

  2024-10-05 18:48:53 | success | deleting subdomain | deleted 1 matching entries from subdomains table with filters: subdomain=*, cdn_status=yes

  ➜ ./subscope.py subdomain delete '*' '*' '*' --cdn_name aws

  2024-10-05 18:48:53 | success | deleting subdomain | deleted 1 matching entries from subdomains table with filters: subdomain=*, cdn_name=aws
  ```
