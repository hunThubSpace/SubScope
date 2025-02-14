# SubScope

**SubScope** is a Python-based command-line and GUI tool that helps you manage domains, subdomains, live urls and IP ranges in workspaces using an SQLite database. This script simplifies the process of adding, listing, and deleting domains and subdomains, along with workspace management. It is especially useful for penetration testers, bug bounty hunters, or anyone who needs to efficiently organize and manage domain data.

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
   usage: ./subscope.py [-h] {program,domain,subdomain,url,ip} ...
   
   Manage programs, domains, subdomains, and IPs
   
   positional arguments:
     {program,domain,subdomain,url,ip}
       program             Manage programs
       domain              Manage domains in a program
       subdomain           Manage subdomains in a program
       url                 Manage urls
       ip                  Manage IPs in a program
   
   options:
     -h, --help            show this help message and exit
    ```

## Usage

The script is executed from the command line. The general syntax is:

```bash
python3 subscope.py <command> <subcommand> [options]
```

If you want to use above commands, use `-h` or `--help` for help
| Management | Link | Management | Link | Management | Link |
| ---------- | ---- | ---------- | ---- | ---------- | ---- |
| Program    | [Click Here](https://medium.com/@hunthubspace/streamlining-your-bug-bounty-projects-adding-and-managing-programs-via-subscope-e394acfdf711) | Subdomain | [Click Here](https://medium.com/@hunthubspace/a-deep-dive-into-subdomain-management-using-subscope-43f8653b4593) | IP Address | [Click Here]()
| Domain     | [Click Here](https://medium.com/@hunthubspace/effective-domain-management-for-bug-bounty-programs-using-subscope-f74b7a0db428) |  URL | [Click Here](https://medium.com/@hunthubspace/managing-and-modifying-urls-in-subscope-for-bug-bounty-programs-a-comprehensive-guide-667df5ed07ab)



## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.
