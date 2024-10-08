# program Management

```bash
➜ ./subscope.py program -h
usage: bb_subscope program [-h] {add,list,delete} ...

positional arguments:
  {add,list,delete}
    add              add a new program
    list             List programs
    delete           Delete a program

options:
  -h, --help         show this help message and exit
```

## Usage
* Create a program (program can be company_name or a program in bugbounty)
    
    ```bash
    ➜ ./subscope.py program add tesla_wk
    2024-10-04 22:56:55 | success | adding program | program tesla_wk created
    ```
* Show information about a program

    ```bash
    ➜ ./subscope.py program list tesla_wk
    {
        "programs": [
            {
                "program": "tesla_wk",
                "created_at": "2024-10-04 22:56:55"
            }
        ]
    }
    ```

* List all programs (placed * instead of program name)

    ```bash
    ➜ ./subscope.py program list '*'
    {
        "programs": [
            {
                "program": "tesla_wk",
                "created_at": "2024-10-04 22:56:55"
            },
            {
                "program": "walmart_wk",
                "created_at": "2024-10-04 23:01:17"
            }
        ]
    }
    ```
* List the program names (suitable for stdin)

    ```bash
    ➜ ./subscope.py program list '*' --brief
    tesla_wk
    walmart_wk
    ```

* Delete a program (also delete all domains, subdomains and live subdomains related to this program)

    ```bash
    ➜ ./subscope.py program delete walmart_wk
    2024-10-04 23:04:56 | success | deleting program | program walmart_wk deleted with 0 domains, 0 subdomains and 0 urls
    ```

* Delete all entries into database (flush)

    ```bash
    ➜ ./subscope.py program delete '*'
    2024-10-04 23:07:32 | success | deleting program | deleted 1 programs, 0 domains, 0 subdomains and 0 urls
    ```
