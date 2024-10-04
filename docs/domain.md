# Domain Management

```bash
➜ ./subscope.py domain -h
usage: subscope.py domain [-h] {add,list,delete} ...

positional arguments:
  {add,list,delete}
    add              Add a domain
    list             List domains in a workspace
    delete           Delete a domain

options:
  -h, --help         show this help message and exit
```

## Usage
* Add a single domain into a workspace

    ```bash
    ➜ ./subscope.py domain add tesla.com tesla_wk
    2024-10-04 23:12:44 | success | adding domain | domain tesla.com added to tesla_wk workspace
    ```

* Add multi-domains with a file (each domain in a separate line)

    ```bash
    ➜ cat domains.txt
    teslamotors.com
    teslaengine.com

    ➜ ./subscope.py domain add domains.txt tesla_wk
    2024-10-04 23:16:30 | success | adding domain | domain teslamotors.com added to tesla_wk workspace
    2024-10-04 23:16:30 | success | adding domain | domain teslaengine.com added to tesla_wk workspace
    ```

* Show informaton about a domain

    ```bash
    ➜ ./subscope.py domain list tesla.com tesla_wk
    {
        "domains": [
            {
                "domain": "tesla.com",
                "created_at": "2024-10-04 23:12:44"
            }
        ]
    }

    # you can use '*' for searching certain domain on all workspaces
    ➜ ./subscope.py domain list tesla.com '*'
    {
        "domains": [
            {
                "domain": "tesla.com",
                "workspace": "tesla_wk",
                "created_at": "2024-10-04 23:12:44"
            }
        ]
    }
    ```

* Listing all domains of a certain workspace

    ```bash
    ➜ ./subscope.py domain list '*' tesla_wk
    {
        "domains": [
            {
                "domain": "tesla.com",
                "created_at": "2024-10-04 23:12:44"
            },
            {
                "domain": "teslamotors.com",
                "created_at": "2024-10-04 23:16:30"
            },
            {
                "domain": "teslaengine.com",
                "created_at": "2024-10-04 23:16:30"
            }
        ]
    }
    ```

* Listing all domain (all workspace)

    ```bash
    ➜ ./subscope.py domain list '*' '*'
    {
        "domains": [
            {
                "domain": "tesla.com",
                "workspace": "tesla_wk",
                "created_at": "2024-10-04 23:12:44"
            },
            {
                "domain": "teslamotors.com",
                "workspace": "tesla_wk",
                "created_at": "2024-10-04 23:16:30"
            },
            {
                "domain": "teslaengine.com",
                "workspace": "tesla_wk",
                "created_at": "2024-10-04 23:16:30"
            }
        ]
    }
    ```

* Listing domain names (suitable for stdin)

    ```bash
    ➜ ./subscope.py domain list '*' '*' --brief
    tesla.com
    teslamotors.com
    teslaengine.com

    # other listing situataion also can apply --brief on output
    ➜ ./subscope.py domain list tesla.com tesla_wk --brief
    ➜ ./subscope.py domain list tesla.com '*' --brief
    ➜ ./subscope.py domain list '*' tesla_wk --brief
    ```

* Delete a domain from a workspace (also delete all subdomains and urls related to it)

    ```bash
    ➜ ./subscope.py domain delete teslaengine.com tesla_wk
    2024-10-04 23:37:22 | success | deleting domain | deleted teslaengine.com from tesla_wk with 0 urls
    ```

* Delete all domains of a workspace (also delete all subdomains and urls related to them)

    ```bash
    ➜ ./subscope.py domain delete '*' tesla_wk
    2024-10-04 23:40:11 | success | deleting domain | deleted 2 domains, 0 subdomains and 0 urls
    ```

* Delete all domains from all workspace (in other words, only workspaces remain)

    ```bash
    ➜ ./subscope.py domain delete '*' '*'
    2024-10-04 23:42:05 | success | deleting domain | deleted 2 domains, 0 subdomains and 0 urls
    ```
