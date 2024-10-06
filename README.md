# SubScope

**SubScope** is a Python-based command-line tool that helps you manage domains, subdomains, live urls and IP ranges in workspaces using an SQLite database. This script simplifies the process of adding, listing, and deleting domains and subdomains, along with workspace management. It is especially useful for penetration testers, bug bounty hunters, or anyone who needs to efficiently organize and manage domain data.

## Requirements

- Python 3.x
- SQLite (included with Python)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/hunThubSpace/SubScope.git && cd SubScope
   ```

2. Run the script:

    ```bash
    chmod +x subscope.py
    ./subscope.py -h
    ```

    This will display usage information:

    ```
    usage: subscope.py [-h] {workspace,domain,subdomain,live} ...

    Manage workspaces, domains, and subdomains

    positional arguments:
      {workspace,domain,subdomain,live}
        workspace           Manage workspaces
        domain              Manage domains in a workspace
        subdomain           Manage subdomains in a workspace
        live                Manage live subdomains
        ip                  Manage IPs in a workspace

    options:
      -h, --help            show this help message and exit
    ```

## Usage

The script is executed from the command line. The general syntax is:

```bash
python3 subscope.py <command> <subcommand> [options]
```

| management     |  document                     | managment     | document                  | managment     | document                  |
| -------------- | ------------------------------| ------------- | ------------------------- | ------------- | ------------------------- |
| `Workspace`    | [here](docs/workspace.md)     | `subdomain`   | [here](docs/subdomain.md) | `ip`          | [here](docs/ip.md) |
| `domain`       | [here](docs/domain.md)        | `live url`    | [here](docs/live.md)      |

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.
