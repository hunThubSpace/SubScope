# SubScope

**SubScope** is a Python-based command-line tool that helps you manage domains and subdomains in workspaces using an SQLite database. This script simplifies the process of adding, listing, and deleting domains and subdomains, along with workspace management. It is especially useful for penetration testers, bug bounty hunters, or anyone who needs to efficiently organize and manage domain data.

## Features

- Create, list, and delete workspaces.
- Add, list, and delete domains within workspaces.
- Add, list, and delete subdomains associated with domains in workspaces.
- Filter and update subdomains based on various criteria.
- Perform bulk operations for domains and subdomains from files.

## Requirements

- Python 3.x
- SQLite (included with Python)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/hunThubSpace/SubScope.git
   cd SubScope
   ```

2. Ensure you have the required dependencies installed. You can use `pip` to install any additional packages if necessary.

3. Run the script:

    ```bash
    python3 subscope.py -h
    ```

    This will display usage information:

    ```
    usage: subscope.py [-h] {workspace,domain,subdomain} ...
    
    Manage workspaces, domains, and subdomains
    
    positional arguments:
    {workspace,domain,subdomain}
        workspace           Manage workspaces
        domain              Manage domains in a workspace
        subdomain           Manage subdomains in a workspace
    
    options:
    -h, --help            show this help message and exit
    ```

## Usage

The script is executed from the command line. The general syntax is:

```bash
python3 subscope.py <command> <subcommand> [options]
```

### Workspace Management

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

➜ python3 subscope.py workspace create <workspace_name>    # Create a Workspace (e.g., tesla, hackerone)
➜ python3 subscope.py workspace list                       # List Workspaces | JSON with workspace_name and create_at timestamp
➜ python3 subscope.py workspace list --brief               # List Workspaces | TXT, Only display the workspace names
➜ python3 subscope.py workspace delete <workspace_name>    # Delete a Workspace
➜ python3 subscope.py workspace delete '*'                 # Delete all workspaces (Flush Database)
```

### Domain Management

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

➜ python3 subscope.py domain add <single_domain> <workspace_name>      # Add a single domain to a Workspace (e.g., tesla.com)
➜ python3 subscope.py domain add <domains.txt> <workspace_name>        # Add bulk domains via file to a Workspace (each domain in a separate line)
➜ python3 subscope.py domain list <workspace_name>                     # List Domains in a Workspace | JSON with domain_name and create_at timestamp
➜ python3 subscope.py domain list <workspace_name> --brief             # List Domains in a Workspace | TXT, Only display the domain names
➜ python3 subscope.py domain delete <domain_name> <workspace_name>     # Delete a Domain from a Workspace
➜ python3 subscope.py domain delete <domain.txt> <workspace_name>      # Delete a Domain from a Workspace
➜ python3 subscope.py domain delete '*' <workspace_name>               # Delete all Domains from a Workspace
```

### Subdomain Management

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

# Default State: --source [Empty] | --scope inscope | --resolved no | --ip none | --cdn no | --cdn_name none

➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name>                                  # Add a Subdomain to a Domain (Default State)
➜ python3 subscope.py subdomain add <subdomains.txt> <domain_name> <workspace_name>                                    # Add bulk subdomains via file to a domain (Default State)
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --source <source>                # Add a subdomain with a source (e.g., crtsh, subfinder)
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --source <source1 source2>       # Add a subdomain with multiple sources (space-separated)
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --scope <inscope|outscope>       # Add a subdomain with a scope
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --resolved <yes|no>              # Add a subdomain with a resolved status
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --ip <IP_Address>                # Add a subdomain with an IP address
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --cdn <yes|no>                   # Add a subdomain with a CDN status
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --cdn_name <CDN_Name>            # Add a subdomain with a CDN name (e.g., CloudFlare)
# You can combine options:
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --source dns4char --resolved yes --ip 10.34.110.54

# List Commands
➜ python3 subscope.py subdomain list <domain_name> <workspace_name>                                                  # List Subdomains of a Domain | JSON
➜ python3 subscope.py subdomain list '*' <workspace_name>                                                            # List all Subdomains in a Workspace | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --brief                                          # List Subdomains of a Domain | TXT, Only display the subdomains
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --source crtsh                                   # List Subdomains of a Domain for crtsh source | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --source crtsh --source-only                     # List Subdomains of a Domain for crtsh source (exclusively) | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --source crtsh --source-only --brief             # List Subdomains of a Domain for crtsh source (exclusively) | TXT
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --resolved yes --cdn_name akamai                 # List resolved subdomains of a Domain with akamai CDN | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --ip 10.2.1.4                                    # List resolved subdomains of a Domain with 10.2.1.4 in IP | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024                               # List subdomains of a Domain updated in year 2024 | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024-09                            # List subdomains of a Domain updated from 2024-09-00-00:00:00 to 2024-12-31-23:59:59 | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024-09-10-12                      # List subdomains of a Domain updated from 2024-09-10-12:00:00 to 2024-09-10-12:59:59 | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024-09-10,2024-12-10              # List subdomains of a Domain updated from 2024-09-10-00:00:00 to 2024-09-12-23:59:59 | JSON

# Delete Commands
➜ python3 subscope.py subdomain delete <subdomain_name> <domain_name> <workspace_name>              # Delete a subdomain
➜ python3 subscope.py subdomain delete '*' <domain_name> <workspace_name>                           # Delete all subdomains of a domain
➜ python3 subscope.py subdomain delete subs.txt <domain_name> <workspace_name>                      # Delete subdomains of a domain from a file
➜ python3 subscope.py subdomain delete '*' <domain_name> <workspace_name> --scope outscope          # Delete all outscope subdomains of a domain
➜ python3 subscope.py subdomain delete '*' <domain_name> <workspace_name> --resolved no             # Delete all unresolved subdomains of a domain
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.
