# SubScope

SubScope is a Python-based command-line tool that helps you manage domains and subdomains in workspaces using an SQLite database. This script simplifies the process of adding, listing, and deleting domains and subdomains, along with workspace management. It is especially useful for penetration testers, bug bounty hunters, or anyone who needs to efficiently organize and manage domain data.

## Features

- Create, list, and delete workspaces.
- Add, list, and delete domains within workspaces.
- Add, list, and delete subdomains associated with domains in workspaces.
- Filter and update subdomains based on source, scope, and resolved status.
- Bulk operations for domains and subdomains from files.

## Requirements

- Python 3.x
- SQLite (included with Python)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/SubScope.git
   cd SubScope
   ```

2. Ensure you have the required dependencies installed. You can use `pip` to install any additional packages if necessary.

3. Run the script:

    ```bash
    ➜ python3 subscope.py -h
    usage: subscope.py [-h] {workspace,domain,subdomain} ...

    Manage workspaces, domains, and subdomains

    positional arguments:
    {workspace,domain,subdomain}
        workspace           Manage workspaces
        domain              Manage domains in a workspace
        subdomain           Manage subdomains in a workspace

    options:
    -h, --help            show this help message and exi
    ```

## Usage

### Command-Line Interface

The script is executed from the command line. The general syntax is:

```bash
python3 subscope.py <command> <subcommand> [options]
```

### Available Commands

- **Workspace Management**
    ```bash
    ➜ python3 subscope.py workspace -h
    usage: subscope.py workspace [-h] {create,list,delete} ...

    positional arguments:
    {create,list,delete}
        create              Create a new workspace
        list                List workspaces
        delete              Delete a workspace

    options:
    -h, --help            show this help message and exit

    # Create a Workspace
    python3 subscope.py workspace create <workspace_name>

    # List Workspaces
    python3 subscope.py workspace list [--brief]
    # Use --brief to display only the workspace names.

    # Delete a Workspace
    python3 subscope.py workspace delete <workspace_name>
    ```


* **Domain Management**
    ```bash
    ➜ python3 subscope.py domain -h
    usage: subscope.py domain [-h] {add,list,delete} ...

    positional arguments:
    {add,list,delete}
        add              Add a domain
        list             List domains in a workspace
        delete           Delete a domain

    options:
    -h, --help         show this help message and exit

    # Add a Domain to a Workspace
    python3 subscope.py domain add <signle_domain|domains.txt> <workspace_name>

    # List Domains in a Workspace
    python3 subscope.py domain list <workspace_name> [--brief]
    # Use `--brief` to display only the domain names.

    # Delete a Domain from a Workspace
    python3 subscope.py domain delete <domain_name|*> <workspace_name>
    ```

- **Subdomain Management**
    ```bash
    ➜ python3 subscope.py subdomain -h
    usage: subscope.py subdomain [-h] {add,list,delete} ...

    positional arguments:
    {add,list,delete}
        add              Add a subdomain
        list             List subdomains
        delete           Delete subdomains

    options:
    -h, --help         show this help message and exit

    # Add a Subdomain to a Domain
    python3 subscope.py subdomain add <single_sub|subdomains.txt> <domain_name> <workspace_name> [--source <source>] [--scope <inscope|outscope>] [--resolved <yes|no>]
    # Default values: --source manual | --scope inscope | --resolved no

    # List Subdomains of a Domain
    python3 subscope.py subdomain list <domain_name|*> <workspace_name> [--source <source>] [--scope <inscope|outscope>] [--resolved <yes|no>] [--brief]
    # Use --brief to display only the subdomain names.

    # Delete a Subdomain
    python3 subscope.py subdomain delete <subdomain_name|*> <domain_name> <workspace_name> [--resolved <yes|no>] [--source <source>] [--scope <inscope|outscope>]
    ```

### Example Usage

- Create a workspace named `tesla_wk`:
    ```bash
    ➜ python3 subscope.py workspace create tesla_wk

    [+] Workspace 'tesla_wk' created.
    ```

- Add a domain "tesla.com" to `tesla_wk`:
    ```bash
    ➜ python3 subscope.py domain add tesla.com tesla_wk

    [+] Domain 'tesla.com' added to workspace 'tesla_wk'
    ```

- Add a subdomain `api.tesla.com` to `tesla.com` in `tesla_wk`:
    ```bash
    ➜ python3 subscope.py subdomain add api.tesla.com tesla.com tesla_wk --source manual --scope inscope --resolved no

    [+] Subdomain 'api.tesla.com' added to domain 'tesla.com' in workspace 'tesla_wk' with sources: manual, scope: inscope, resolved: no
    ```

- Add subdomains from `subs.txt` to `tesla.com` in `tesla_wk`:
    ```bash
    python3 subscope.py subdomain add subs.txt tesla.com tesla_wk --source crtsh manual --scope inscope --resolved yes

    [+] Subdomain 'www.tesla.com' added to domain 'tesla.com' in workspace 'tesla_wk' with sources: crtsh, manual, scope: inscope, resolved: yes
    [+] Subdomain 'mail.tesla.com' added to domain 'tesla.com' in workspace 'tesla_wk' with sources: crtsh, manual, scope: inscope, resolved: yes
    ```

- List all subdomains of `tesla.com` in `tesla_wk`:
    ```bash
    ➜ python3 subscope.py subdomain list tesla.com tesla_wk --source crtsh

    [
        {
            "subdomain": "www.tesla.com",
            "domain": "tesla.com",
            "workspace_name": "tesla_wk",
            "source": "crtsh, manual",
            "scope": "inscope",
            "resolved": "yes",
            "created_at": "2024-09-27 22:21:37",
            "updated_at": "2024-09-27 22:21:37"
        },
        {
            "subdomain": "mail.tesla.com",
            "domain": "tesla.com",
            "workspace_name": "tesla_wk",
            "source": "crtsh, manual",
            "scope": "inscope",
            "resolved": "yes",
            "created_at": "2024-09-27 22:21:37",
            "updated_at": "2024-09-27 22:21:37"
        }
    ]
    ```

- List all subdomains of all domains in `tesla_wk` --resolved no:
    ```bash
    ➜ python3 subscope.py subdomain list '*' tesla_wk

    [
        {
            "subdomain": "api.tesla.com",
            "domain": "tesla.com",
            "workspace_name": "tesla_wk",
            "source": "manual",
            "scope": "inscope",
            "resolved": "no",
            "created_at": "2024-09-27 22:19:02",
            "updated_at": "2024-09-27 22:19:02"
        }
    ]
    ```

- Delete subdomain `www.tesla.com` from `tesla.com` domain, `tesla_wk` workspace:
    ```bash
    ➜ python3 subscope.py subdomain delete www.tesla.com tesla.com tesla_wk

    [+] Subdomain 'www.tesla.com' deleted from domain 'tesla.com' in workspace 'tesla_wk'
    ```

- Delete all subdomains of `tesla.com` with a specific source:
    ```bash
    python3 subscope.py subdomain delete '*' tesla.com tesla_wk --source crtsh

    [+] All matching subdomains deleted from domain 'tesla.com' in workspace 'tesla_wk' with source 'crtsh', resolved status 'None', and scope 'None'.
    ```

- List of subdomains of `tesla.com` in short mode
    ```bash
    ➜ python3 subscope.py subdomain list tesla.com tesla_wk --biref

    api.tesla.com
    www.tesla.com
    mail.tesla.com
    ```


## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.
