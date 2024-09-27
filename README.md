# SubScope

**`SubScope`** is a Python-based command-line tool that helps you manage domains and subdomains in workspaces using an SQLite database. This script simplifies the process of adding, listing, and deleting domains and subdomains, along with workspace management. It is especially useful for penetration testers, bug bounty hunters, or anyone who needs to efficiently organize and manage domain data.

## Features

- **Manage Workspaces**: Create, list, and delete workspaces to organize your domains and subdomains efficiently.
- **Domain Management**: Add, list, and delete domains within specific workspaces.
- **Subdomain Management**: Add, list, and delete subdomains associated with domains in different workspaces.
- **Source Tracking**: Keep track of the sources of subdomains and update them dynamically, allowing you to manage data from multiple discovery tools.
- **Custom Statuses**: Assign custom statuses (`inscope` and `outscope`) to subdomains, helping you differentiate between valid and non-relevant targets.
- **Batch Input Support**: Add multiple domains and subdomains from files, making it easy to bulk manage large datasets.
- **Filter by Source and Status**: Query and list subdomains based on their source and status for granular control and analysis.
- **Comprehensive Deletion**: Delete specific subdomains or clear entire sets of subdomains based on source or status.
- **Timestamps for Tracking**: Automatically track the creation and modification times for each domain and subdomain entry.
- **JSON Output**: Easily export workspaces, domains, and subdomains in JSON format for integration with other tools or for reporting.
- **Command-Line Interface**: Full command-line interface (CLI) support with flexible options for automation in scripts and pipelines.


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
   python3 subscope.py -h
   ```

## Usage

### Command-Line Interface

The script provides a command-line interface for easy management. The basic structure of the commands is:

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
  -h, --help            show this help message and exit
```

### Commands

#### Workspaces
```bash
➜  Scripts python3 subscope.py workspace -h
usage: subscope.py workspace [-h] {create,list,delete} ...

positional arguments:
  {create,list,delete}
    create              Create a new workspace
    list                List workspaces
    delete              Delete a workspace

options:
  -h, --help            show this help message and exit
```

- **Create a new workspace**:
  ```bash
  python3 subscope.py workspace create <workspace_name>
  ```

- **List all workspaces**:
  ```bash
  python3 subscope.py workspace list [--brief]
  ```

- **Delete a workspace**:
  ```bash
  python3 subscope.py workspace delete <workspace_name>
  ```

#### Domains
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
```
- **Add a domain to a workspace**:
  ```bash
  python3 subscope.py domain add <domain> <workspace_name>
  ```
    - you can use a file with domains like `domains.txt` instead of `<domain>`.

- **List all domains in a workspace**:
  ```bash
  python3 subscope.py domain list <workspace_name> [--brief]
  ```
    - The `--brief` option print only domains, good for scripting and piping.

- **Delete a domain from a workspace**:
  ```bash
  python3 subscope.py domain delete <domain> <workspace_name>
  ```

#### Subdomains
```bash
➜  Scripts python3 subscope.py subdomain -h
usage: subscope.py subdomain [-h] {add,list,delete} ...

positional arguments:
  {add,list,delete}
    add              Add a subdomain
    list             List subdomains
    delete           Delete subdomains (supports file or wildcard)

options:
  -h, --help         show this help message and exit
```
- **Add a subdomain to a domain in a workspace**:
  ```bash
  python3 subscope.py subdomain add <subdomain> <domain> <workspace_name> [--source <source>] [--status <inscope|outscope>]
  ```
    - You can use a file with subdoamins like `subdomains.txt` instead of `<subdomain>`.
    - If `--source` does not declare, the defulat is `manual`. also the defulat value for `status` is `inscope`.
    
- **List subdomains of a domain in a workspace**:
  ```bash
  python3 subscope.py subdomain list <domain> <workspace_name> [--source <source>] [--status <status>] [--brief]
  ```
    - For listing all subdomains in a workspace (all domains) placed **'\*'** instead of **\<domain\>**
    - If `--source` does not declare, the script prints all subdomains with different sources also this functioanlity is applied on `--status` option.

- **Delete a subdomain from a domain in a workspace**:
  ```bash
  python3 subscope.py subdomain delete <subdomain> <domain> <workspace_name> [--status <status>] [--source <source>]
  ```
    - You can use `'*'` instad of `<subdomain>` for deleting all subdomains of a domain.
    - Also you can delete a list of subdomains like `dell_subs.txt`, just with replacing your file name with `<subdomain>`


## Sample output
```bash
➜  Scripts python3 subscope.py subdomain list tesla.com wk_tesla --source subfinder --status inscope
[
  {
    "subdomain": "[REDACT].tesla.com",
    "domain": "tesla.com",
    "workspace_name": "wk_tesla",
    "source": "subfinder, crtsh, chaos",
    "status": "inscope",
    "created_at": "2024-09-27 17:38:01",
    "updated_at": "2024-09-27 17:38:01"
  },
  {
    "subdomain": "[REDACT].tesla.com",
    "domain": "tesla.com",
    "workspace_name": "wk_tesla",
    "source": "subfinder, dnsbrute",
    "status": "inscope",
    "created_at": "2024-09-27 17:38:52",
    "updated_at": "2024-09-27 17:38:52"
  }
]
```
## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.

