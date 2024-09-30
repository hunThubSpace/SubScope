# SubScope

SubScope is a Python-based command-line tool that helps you manage domains and subdomains in workspaces using an SQLite database. This script simplifies the process of adding, listing, and deleting domains and subdomains, along with workspace management. It is especially useful for penetration testers, bug bounty hunters, or anyone who needs to efficiently organize and manage domain data.

## Features

- Create, list, and delete workspaces.
- Add, list, and delete domains within workspaces.
- Add, list, and delete subdomains associated with domains in workspaces.
- Filter and update subdomains based on different filters.
- Bulk operations for domains and subdomains from files.

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


The script is executed from the command line. The general syntax is:

```bash
➜ python3 subscope.py <command> <subcommand> [options]
```

### Workspace Management

```bash
➜ python3 subscope.py workspace create <workspace_name>    # Create a Workspace (program name like tesla, hackerone and etc)
➜ python3 subscope.py workspace list                       # List Workspaces | JSON with workspace_name and Create_at timestamp
➜ python3 subscope.py workspace list --brief               # List Workspaces | TXT, Only display the workspaces name
➜ python3 subscope.py workspace delete <workspace_name>    # Delete a Workspace
➜ python3 subscope.py workspace delete '*'                 # Delete all workspaces (Flush Database)
```

### Domain Management
```bash
➜ python3 subscope.py domain add <signle_domain> <workspace_name>      # Add a single domain to a Workspace (single domain like tesla.com, hackerone.com)
➜ python3 subscope.py domain add <domains.txt> <workspace_name>        # Add bulk domains via file to a Workspace (every domain in a separate line)
➜ python3 subscope.py domain list <workspace_name>                     # List Domains in a Workspace | JSON with domain_name and Create_at timestamp
➜ python3 subscope.py domain list <workspace_name> --brief             # List Domains in a Workspace | TXT, Only display the domain name
➜ python3 subscope.py domain delete <domain_name> <workspace_name>     # Delete a Domain from a Workspace
➜ python3 subscope.py domain delete '*' <workspace_name>               # Delete all Domains from a Workspace
```

### Subdomain Management
```bash
# Default State: --source manual | --scope inscope | --resolved no | --ip none | --cdn no | --cdn_name none

➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name>                                  # Add a Subdomain to a Domain (*Default State)
➜ python3 subscope.py subdomain add <subdomains.txt> <domain_name> <workspace_name>                                    # Add bulk subdomains via file to a domain (every domain in a separate line) - (*Default State)


➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --source <source>                # Add a subdomain with a source (source like crtsh, subfinder, rapiddns and etc)
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --source <source1 source2>       # Add a subdomain with multiple source (placed space between sources)
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --scope <inscope|outscope>       # Add a subdomain with a scope
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --resolved <yes|no>              # Add a subdomain with a resolved status (resolved means the subdomain has a dns query like A, CNAME, MX and etc)
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --ip <IP_Address>                # Add a subdomain with a IP address
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --cdn <yes|no>                   # Add a subdomain with a CDN status
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --cdn_name <CDN_Name>            # Add a subdomain with a CDN name (like CloudFlare, CloudFront, AKAMAI and etc)
➜ python3 subscope.py subdomain add <single_subdomain> <domain_name> <workspace_name> --source dns4char --reolved yes --ip 10.34.110.54           # You can use all options
# All above commands also can be used for adding subdomains using file

➜ python3 subscope.py subdomain list <domain_name> <workspace_name>                                                  # List Subdomains of a Domain | JSON with extra data
➜ python3 subscope.py subdomain list '*' <workspace_name>                                                            # List of all Subdomains in a workstaion  | JSON with extra data
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --brief                                          # List Subdomains of a Domain | Txt, Only display the subdomains
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --source crtsh                                   # List Subdomains of a Domain for crtsh source | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --source crtsh --source-only                     # List Subdomains of a Domain for crtsh source (exclusively) | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --source crtsh --source-only --brief             # List Subdomains of a Domain for crtsh source (exclusively) | TXT
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --resolved yes --cdn_name akamai                 # List resolved subdomains of a Domain with akamai cdn | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --ip 10.2.1.4                                    # List resolved subdomains of a Domain with 10.2.1.4 in IP | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024                               # List subdomains of a Domain updated in year 2024 | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024-09                            # List subdomains of a Domain updated from 2024-09-00-00:00:00 to 2024-12-31-23:59:59 | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024-09-10-12                      # List subdomains of a Domain updated from 2024-09-10-12:00:00 to 2024-09-10-12:59:59 | JSON
➜ python3 subscope.py subdomain list <domain_name> <workspace_name> --update_time 2024-09-10,2024-12-10              # List subdomains of a Domain updated from 2024-09-10-00:00:00 to 2024-09-12-23:59:59 | JSON

# Delete a Subdomain
python3 subscope.py subdomain delete <subdomain_name> <domain_name> <workspace_name>              # Delete a subdomain
python3 subscope.py subdomain delete '*' <domain_name> <workspace_name>                           # Delete all subdomains of a domain
python3 subscope.py subdomain delete subs.txt <domain_name> <workspace_name>                      # Delete subdomains of a domain from a file
python3 subscope.py subdomain delete '*' <domain_name> <workspace_name> --scope outscope          # Delete all outscope subdomains of a domain
python3 subscope.py subdomain delete '*' <domain_name> <workspace_name> --resolved no             # Ddelete all unresolved subdomains of a domain
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.
