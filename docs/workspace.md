# Workspace Management

```bash
➜ ./subscope.py workspace -h
usage: subscope.py workspace [-h] {create,list,delete} ...

positional arguments:
  {create,list,delete}
    create              Create a new workspace
    list                List workspaces
    delete              Delete a workspace

options:
  -h, --help            show this help message and exit
```

## Usage
* Create a Workspace (workspace can be company_name or a program in bugbounty)
    
    ```bash
    ➜ ./subscope.py workspace create tesla_wk
    2024-10-04 22:56:55 | success | adding workspace | workspace tesla_wk created
    ```
* Show information about a workspace

    ```bash
    ➜ ./subscope.py workspace list tesla_wk
    {
        "workspaces": [
            {
                "workspace": "tesla_wk",
                "created_at": "2024-10-04 22:56:55"
            }
        ]
    }
    ```

* List all workspaces (placed * instead of workspace name)

    ```bash
    ➜ ./subscope.py workspace list '*'
    {
        "workspaces": [
            {
                "workspace": "tesla_wk",
                "created_at": "2024-10-04 22:56:55"
            },
            {
                "workspace": "walmart_wk",
                "created_at": "2024-10-04 23:01:17"
            }
        ]
    }
    ```
* List the workspace names (suitable for stdin)

    ```bash
    ➜ ./subscope.py workspace list '*' --brief
    tesla_wk
    walmart_wk
    ```

* Delete a workspace (also delete all domains, subdomains and live subdomains related to this workspace)

    ```bash
    ➜ ./subscope.py workspace delete walmart_wk
    2024-10-04 23:04:56 | success | deleting workspace | workspace walmart_wk deleted with 0 domains, 0 subdomains and 0 urls
    ```

* Delete all entries into database (flush)

    ```bash
    ➜ ./subscope.py workspace delete '*'
    2024-10-04 23:07:32 | success | deleting workspace | deleted 1 workspaces, 0 domains, 0 subdomains and 0 urls
    ```