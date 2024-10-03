#!/usr/bin/python3

import argparse
import sqlite3
import json
import os
import colorama
from datetime import datetime, timedelta
from colorama import Fore, Back, Style

colorama.init()

conn = sqlite3.connect('scopes.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS workspaces (
    workspace TEXT PRIMARY KEY,
    created_at TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS domains (
    domain TEXT PRIMARY KEY,
    workspace TEXT,
    created_at TEXT,
    FOREIGN KEY(workspace) REFERENCES workspaces(workspace)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS subdomains (
    subdomain TEXT,
    domain TEXT,
    workspace TEXT,
    source TEXT,
    scope TEXT,
    resolved TEXT,
    ip_address TEXT DEFAULT 'none',
    cdn_status TEXT DEFAULT 'no',
    cdn_name TEXT DEFAULT 'none',
    created_at TEXT,
    updated_at TEXT,
    PRIMARY KEY(subdomain, domain, workspace)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS live (
    url TEXT,
    subdomain TEXT,
    domain TEXT,
    workspace TEXT,
    scheme TEXT,
    method TEXT,
    port INTEGER,
    status_code INTEGER,
    ip_address TEXT,
    cdn_status TEXT,
    cdn_name TEXT,
    title TEXT,
    webserver,
    webtech,  -- This column can store multiple values, delimited by commas
    cname TEXT,
    created_at,
    updated_at,
    PRIMARY KEY(url, subdomain, domain, workspace)
)
''')

def create_workspace(workspace):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    # Check if the workspace already exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    existing_workspace = cursor.fetchone()

    if existing_workspace:
        print(f"{Fore.RED}{Style.BRIGHT}[-ER] {Style.RESET_ALL} Workspace '{workspace}' already exists")
        return  # Exit the function if the workspace already exists

    # If the workspace does not exist, create a new one
    cursor.execute("INSERT INTO workspaces (workspace, created_at) VALUES (?, ?)", (workspace, timestamp))
    conn.commit()
    print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Workspace '{workspace}' created at '{timestamp}'")

def list_workspaces(workspace='*', brief=False):
    if workspace == '*':
        cursor.execute("SELECT workspace, created_at FROM workspaces")
    else:
        cursor.execute("SELECT workspace, created_at FROM workspaces WHERE workspace = ?", (workspace,))
    
    workspaces = cursor.fetchall()

    # If no workspaces exist, return early
    if not workspaces:
        return  # No output if there are no workspaces

    if brief:
        for ws in workspaces:
            print(ws[0])  # Print each workspace name in brief mode
    else:
        workspace_list = [{'workspace': ws[0], 'created_at': ws[1]} for ws in workspaces]
        print(json.dumps({"workspaces": workspace_list}, indent=4))

def delete_workspace(workspace):
    if workspace == '*':
        # Delete all subdomains associated with all workspaces
        cursor.execute("DELETE FROM subdomains")

        # Delete all domains associated with all workspaces
        cursor.execute("DELETE FROM domains")

        # Delete all workspaces
        cursor.execute("DELETE FROM workspaces")
        
        conn.commit()
        print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} All workspaces, along with their associated domains and subdomains, have been deleted")
        return  # Exit the function after deleting all

    # Check if the specified workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
        return  # Exit the function if the workspace does not exist

    # Delete all subdomains associated with the specified workspace
    cursor.execute("DELETE FROM subdomains WHERE workspace = ?", (workspace,))
    
    # Delete all domains associated with the specified workspace
    cursor.execute("DELETE FROM domains WHERE workspace = ?", (workspace,))
    
    # Delete the specified workspace
    cursor.execute("DELETE FROM workspaces WHERE workspace = ?", (workspace,))
    
    conn.commit()
    print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}', all associated domains, and subdomains deleted")

def add_domain(domain_or_file, workspace):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    existing_workspace = cursor.fetchone()

    if not existing_workspace:
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
        return  # Exit the function if the workspace does not exist

    # Check if the input is a file
    if os.path.isfile(domain_or_file):
        # If a file is provided, read the domains from the file
        with open(domain_or_file, 'r') as file:
            domains = [line.strip() for line in file if line.strip()]
    else:
        # Otherwise, treat it as a single domain
        domains = [domain_or_file]

    for domain in domains:
        # Check if the domain already exists in the specified workspace
        cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace = ?", (domain, workspace))
        existing_domain = cursor.fetchone()

        if existing_domain:
            print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Domain '{domain}' already exists in workspace '{workspace}'")
        else:
            try:
                cursor.execute("INSERT INTO domains (domain, workspace, created_at) VALUES (?, ?, ?)", (domain, workspace, timestamp))
                conn.commit()
                print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Domain '{domain}' added to workspace '{workspace}' at '{timestamp}'")
            except sqlite3.IntegrityError:
                print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Domain '{domain}' already exists in the database")

def list_domains(workspace='*', brief=False):
    # Check if the workspace is specific or all
    if workspace != '*':
        # Check if the workspace exists
        cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
        if not cursor.fetchone():
            print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
            return  # Exit the function if the workspace does not exist
        
        # Fetch domains associated with the specific workspace
        cursor.execute("SELECT domain, created_at FROM domains WHERE workspace = ?", (workspace,))
    else:
        # Fetch all domains from all workspaces
        cursor.execute("SELECT domain, workspace, created_at FROM domains")

    domains = cursor.fetchall()

    # Check if there are any domains to display
    if not domains:
        print(f"{Fore.YELLOW}No domains found.{Style.RESET_ALL}")
        return  # Exit if there are no domains; no output will be printed

    if brief:
        # Print only the domain names, considering the case of multiple workspaces
        for domain in domains:
            print(domain[0])  # domain[0] will have the domain name
    else:
        # Create a list of domains including workspace information
        domain_list = [{'domain': domain[0], 'workspace': domain[1], 'created_at': domain[2]} for domain in domains]
        print(json.dumps({"domains": domain_list}, indent=4))

def delete_domain(domain='*', workspace='*'):
    if domain == '*':
        if workspace == '*':
            # Delete all subdomains from all workspaces
            cursor.execute("DELETE FROM subdomains")
            
            # Delete all domains from all workspaces
            cursor.execute("DELETE FROM domains")
            
            conn.commit()
            print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} All domains and their subdomains deleted from all workspaces")
        else:
            # Delete all subdomains from a specific workspace
            cursor.execute("DELETE FROM subdomains WHERE workspace = ?", (workspace,))
            
            # Delete all domains from a specific workspace
            cursor.execute("DELETE FROM domains WHERE workspace = ?", (workspace,))
            
            conn.commit()
            print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} All domains and their subdomains deleted from workspace '{workspace}'")
    else:
        if workspace == '*':
            # Delete all subdomains associated with the domain across all workspaces
            cursor.execute("DELETE FROM subdomains WHERE domain = ?", (domain,))
            
            # Delete the domain itself from all workspaces
            cursor.execute("DELETE FROM domains WHERE domain = ?", (domain,))
            
            conn.commit()
            print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Domain '{domain}' and all its subdomains deleted from all workspaces")
        else:
            # Delete all subdomains associated with the domain in the specified workspace
            cursor.execute("DELETE FROM subdomains WHERE domain = ? AND workspace = ?", (domain, workspace))
            
            # Delete the domain itself from the specified workspace
            cursor.execute("DELETE FROM domains WHERE domain = ? AND workspace = ?", (domain, workspace))
            
            conn.commit()
            print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Domain '{domain}' and all its subdomains deleted from workspace '{workspace}'")

def add_subdomain(subdomain_or_file, domain, workspace, sources=None, scope='outscope', resolved='no', ip_address='none', cdn_status='no', cdn_name='none'):
    # Custom timestamp format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
        return  # Exit if the workspace does not exist

    # Check if the domain exists
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace = ?", (domain, workspace))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Domain '{domain}' does not exist in workspace '{workspace}'")
        return  # Exit if the domain does not exist

    # Check if the input is a file
    if os.path.isfile(subdomain_or_file):
        # Read subdomains from the file
        with open(subdomain_or_file, 'r') as file:
            subdomains = [line.strip() for line in file if line.strip()]
    else:
        subdomains = [subdomain_or_file]

    # Process each subdomain
    for subdomain in subdomains:
        cursor.execute("SELECT * FROM subdomains WHERE subdomain = ? AND domain = ? AND workspace = ?", 
                       (subdomain, domain, workspace))
        existing = cursor.fetchone()

        # Prepare for updates
        update_fields = {}
        if existing:
            # Update fields if parameters are provided
            if sources:
                current_sources = existing[3].split(", ") if existing[3] else []
                current_sources_set = set(current_sources)
                new_sources = [src.strip() for src in sources if src.strip()]
                current_sources_set.update(new_sources)
                updated_sources = ", ".join(sorted(current_sources_set)) if current_sources_set else ""
                if updated_sources != existing[3]:  # Check if sources have changed
                    update_fields['source'] = updated_sources

            if resolved != 'no' and resolved != existing[5]:  # Assuming 5th column is 'resolved'
                update_fields['resolved'] = resolved

            if ip_address != 'none' and ip_address != existing[6]:  # Assuming 6th column is 'ip_address'
                update_fields['ip_address'] = ip_address
            
            if cdn_status != 'no' and cdn_status != existing[7]:  # Assuming 7th column is 'cdn_status'
                update_fields['cdn_status'] = cdn_status
            
            if cdn_name != 'none' and cdn_name != existing[8]:  # Assuming 8th column is 'cdn_name'
                update_fields['cdn_name'] = cdn_name

            # Always allow updates for 'cdn_status' from yes to no or vice versa
            if cdn_status != existing[7]:  # Assuming 7th column is 'cdn_status'
                update_fields['cdn_status'] = cdn_status

            # Update the subdomain only if there are changes
            if update_fields:
                update_query = "UPDATE subdomains SET "
                update_query += ", ".join(f"{col} = ?" for col in update_fields.keys())
                update_query += ", updated_at = ? WHERE subdomain = ? AND domain = ? AND workspace = ?"
                cursor.execute(update_query, (*update_fields.values(), timestamp, subdomain, domain, workspace))
                conn.commit()
                print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Updated subdomain '{Fore.YELLOW}{Style.BRIGHT}{subdomain}{Style.RESET_ALL}' in domain '{Fore.YELLOW}{Style.BRIGHT}{domain}{Style.RESET_ALL}' in workspace '{Fore.YELLOW}{Style.BRIGHT}{workspace}{Style.RESET_ALL}' with updates: {Fore.YELLOW}{Style.BRIGHT}{update_fields}{Style.RESET_ALL}")

        else:
            # If the subdomain does not exist, create it with no defaults
            new_source_str = ", ".join(sources) if sources else ""  # No default value
            cursor.execute("""
                INSERT INTO subdomains (subdomain, domain, workspace, source, scope, resolved, ip_address, cdn_status, cdn_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (subdomain, domain, workspace, new_source_str, scope, resolved, ip_address, cdn_status, cdn_name, timestamp, timestamp))
            conn.commit()
            print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Subdomain '{Fore.YELLOW}{Style.BRIGHT}{subdomain}{Style.RESET_ALL}' added to domain '{Fore.YELLOW}{Style.BRIGHT}{domain}{Style.RESET_ALL}' in workspace '{Fore.YELLOW}{Style.BRIGHT}{workspace}{Style.RESET_ALL}' with sources: {Fore.YELLOW}{Style.BRIGHT}{new_source_str}{Style.RESET_ALL}, scope: {Fore.YELLOW}{Style.BRIGHT}{scope}{Style.RESET_ALL}, resolved: {Fore.YELLOW}{Style.BRIGHT}{resolved}{Style.RESET_ALL}, IP: {Fore.YELLOW}{Style.BRIGHT}{ip_address}{Style.RESET_ALL}, cdn_status: {Fore.YELLOW}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}, CDN Name: {Fore.YELLOW}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}")

def list_subdomains(subdomain='*', domain='*', workspace='*', sources=None, scope=None, resolved=None, brief=False, source_only=False, cdn_status=None, ip=None, cdn_name=None, create_time=None, update_time=None):
    # If workspace is '*', we won't filter by workspace
    workspaces_to_query = []

    if workspace != '*':
        # Check if the workspace exists
        cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
        if not cursor.fetchone():
            print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
            return
        workspaces_to_query.append(workspace)

    # Base query
    query = """
        SELECT subdomain, domain, source, scope, resolved, ip_address, cdn_status, cdn_name, created_at, updated_at, workspace 
        FROM subdomains 
    """
    parameters = []

    # Add filtering for workspace if not '*'
    if workspaces_to_query:
        query += "WHERE workspace IN (" + ",".join(["?"] * len(workspaces_to_query)) + ")"
        parameters.extend(workspaces_to_query)

    # Handle wildcard for domain and subdomain
    if domain != '*':
        query += " AND domain = ?" if 'WHERE' in query else " WHERE domain = ?"
        parameters.append(domain)

    if subdomain != '*':
        query += " AND subdomain = ?" if 'WHERE' in query else " WHERE subdomain = ?"
        parameters.append(subdomain)

    # If listing all subdomains for all domains and workspaces
    if domain == '*' and subdomain == '*' and workspace == '*':
        # We don't need to filter by workspace or any subdomain/domain
        query = """
            SELECT subdomain, domain, source, scope, resolved, ip_address, cdn_status, cdn_name, created_at, updated_at, workspace 
            FROM subdomains
        """
        parameters = []  # No parameters needed since we're selecting everything

    # Add filtering for scope
    if scope:
        query += " AND scope = ?"
        parameters.append(scope)

    # Add filtering for resolved status
    if resolved:
        query += " AND resolved = ?"
        parameters.append(resolved)

    # Add filtering for cdn_status
    if cdn_status:
        query += " AND cdn_status = ?"
        parameters.append(cdn_status)

    # Add filtering for ip_address
    if ip:
        query += " AND ip_address = ?"
        parameters.append(ip)

    # Add filtering for cdn_name
    if cdn_name:
        query += " AND cdn_name = ?"
        parameters.append(cdn_name)

    # Parse create_time and update_time and add time range filters
    if create_time:
        start_time, end_time = parse_time_range(create_time)
        query += " AND created_at BETWEEN ? AND ?"
        parameters.extend([start_time, end_time])

    if update_time:
        start_time, end_time = parse_time_range(update_time)
        query += " AND updated_at BETWEEN ? AND ?"
        parameters.extend([start_time, end_time])

    # Execute the query
    cursor.execute(query, parameters)
    subdomains = cursor.fetchall()

    if subdomains:
        filtered_subdomains = []

        # Filter by source if provided
        if sources:
            for subdomain in subdomains:
                subdomain_sources = [src.strip() for src in subdomain[2].split(',')]
                if any(source in subdomain_sources for source in sources):
                    filtered_subdomains.append(subdomain)
        else:
            filtered_subdomains = subdomains

        # Further filter for --source-only
        if source_only and sources:
            filtered_subdomains = [sub for sub in filtered_subdomains if sub[2].strip() == sources[0]]

        if filtered_subdomains:
            if brief:
                print("\n".join(sub[0] for sub in filtered_subdomains))
            else:
                result = [
                    {
                        "subdomain": sub[0], 
                        "domain": sub[1], 
                        "workspace": sub[10],
                        "source": sub[2], 
                        "scope": sub[3], 
                        "resolved": sub[4],
                        "ip_address": sub[5], 
                        "cdn_status": sub[6], 
                        "cdn_name": sub[7],
                        "created_at": sub[8], 
                        "updated_at": sub[9]
                    }
                    for sub in filtered_subdomains
                ]
                print(json.dumps(result, indent=4))
    else:
        print(f"{Fore.YELLOW}No subdomains found.{Style.RESET_ALL}")

def delete_subdomain(sub='*', domain='*', workspace='*', scope=None, source=None, resolved=None, ip_address=None, cdn_status=None, cdn_name=None):
    # Start building the delete query
    if sub == '*':
        # Deleting all subdomains from all domains and workspaces
        query = "DELETE FROM subdomains WHERE 1=1"
        params = []

        if domain != '*':
            query += " AND domain = ?"
            params.append(domain)

        if workspace != '*':
            query += " AND workspace = ?"
            params.append(workspace)

        # Add filtering for source
        if source:
            query += " AND source LIKE ?"
            params.append(f"%{source}%")

        # Add filtering for resolved status
        if resolved:
            query += " AND resolved = ?"
            params.append(resolved)

        # Add filtering for scope
        if scope:
            query += " AND scope = ?"
            params.append(scope)

        # Add filtering for IP address
        if ip_address:
            query += " AND ip_address = ?"
            params.append(ip_address)

        # Add filtering for cdn_status
        if cdn_status:
            query += " AND cdn_status = ?"
            params.append(cdn_status)

        # Add filtering for CDN name
        if cdn_name:
            query += " AND cdn_name = ?"
            params.append(cdn_name)

        cursor.execute(query, params)
        conn.commit()
        print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} All matching subdomains deleted from domain '{Fore.YELLOW}{Style.BRIGHT}{domain}{Style.RESET_ALL}' across all workspaces with filters: sources={source}, scope={scope}, resolved={resolved}, IP={ip_address}, cdn_status={cdn_status}, CDN Name={cdn_name}")
    else:
        # Delete a single subdomain with optional filters
        query = "DELETE FROM subdomains WHERE subdomain = ?"
        params = [sub]

        if domain != '*':
            query += " AND domain = ?"
            params.append(domain)

        if workspace != '*':
            query += " AND workspace = ?"
            params.append(workspace)

        # Add filtering for resolved status
        if resolved:
            query += " AND resolved = ?"
            params.append(resolved)

        # Add filtering for scope
        if scope:
            query += " AND scope = ?"
            params.append(scope)

        # Add filtering for IP address
        if ip_address:
            query += " AND ip_address = ?"
            params.append(ip_address)

        # Add filtering for cdn_status
        if cdn_status:
            query += " AND cdn_status = ?"
            params.append(cdn_status)

        # Add filtering for CDN name
        if cdn_name:
            query += " AND cdn_name = ?"
            params.append(cdn_name)

        cursor.execute(query, params)
        conn.commit()
        print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Subdomain '{Fore.YELLOW}{Style.BRIGHT}{sub}{Style.RESET_ALL}' deleted from domain '{Fore.YELLOW}{Style.BRIGHT}{domain}{Style.RESET_ALL}' in workspace '{Fore.YELLOW}{Style.BRIGHT}{workspace}{Style.RESET_ALL}' with IP address '{Fore.YELLOW}{Style.BRIGHT}{ip_address}{Style.RESET_ALL}', cdn_status '{Fore.YELLOW}{Style.BRIGHT}{cdn_status}{Style.RESET_ALL}', and CDN name '{Fore.YELLOW}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}'")

def add_live_subdomain(url, subdomain, domain, workspace, scheme=None, method=None, port=None, status_code=None, ip_address=None, cdn_status=None, cdn_name=None, title=None, webserver=None, webtech=None, cname=None):
    # Custom timestamp format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
        return  # Exit if the workspace does not exist

    # Check if the domain exists
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace = ?", (domain, workspace))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Domain '{domain}' does not exist in workspace '{workspace}'")
        return  # Exit if the domain does not exist

    # Check if the live subdomain exists
    cursor.execute("SELECT * FROM live WHERE url = ? AND subdomain = ? AND domain = ? AND workspace = ?", 
                   (url, subdomain, domain, workspace))
    existing = cursor.fetchone()

    update_fields = {}
    
    if existing:
        # Subdomain exists, check for updates
        if scheme is not None and scheme != existing[4]:  # Scheme (5th column)
            update_fields['scheme'] = scheme

        if method is not None and method != existing[5]:  # Method (6th column)
            update_fields['method'] = method

        if port is not None and port != existing[6]:  # Port (7th column)
            update_fields['port'] = port

        if status_code is not None and status_code != existing[7]:  # Status code (8th column)
            update_fields['status_code'] = status_code

        if ip_address is not None and ip_address != existing[8]:  # IP Address (9th column)
            update_fields['ip_address'] = ip_address

        if cdn_status is not None and cdn_status != existing[9]:  # CDN Status (10th column)
            update_fields['cdn_status'] = cdn_status

        if cdn_name is not None and cdn_name != existing[10]:  # CDN Name (11th column)
            update_fields['cdn_name'] = cdn_name

        if title is not None and title != existing[11]:  # Title (12th column)
            update_fields['title'] = title

        if webserver is not None and webserver != existing[12]:  # Webserver (13th column)
            update_fields['webserver'] = webserver

        if webtech is not None and webtech != existing[13]:  # Webtech (14th column)
            update_fields['webtech'] = webtech

        if cname is not None and cname != existing[14]:  # CNAME (15th column)
            update_fields['cname'] = cname

        # Always update the timestamp when we modify the entry
        if update_fields:
            update_query = "UPDATE live SET " + ", ".join(f"{col} = ?" for col in update_fields) + ", updated_at = ? WHERE url = ? AND subdomain = ? AND domain = ? AND workspace = ?"
            cursor.execute(update_query, (*update_fields.values(), timestamp, url, subdomain, domain, workspace))
            conn.commit()
            print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Updated live subdomain '{url}' in domain '{domain}' in workspace '{workspace}' with updates: {update_fields}")

    else:
        # Subdomain does not exist, insert it
        cursor.execute(""" 
            INSERT INTO live (url, subdomain, domain, workspace, scheme, method, port, status_code, ip_address, cdn_status, cdn_name, title, webserver, webtech, cname, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            (url, subdomain, domain, workspace, 
             scheme if scheme is not None else None, 
             method if method is not None else None, 
             port if port is not None else None, 
             status_code if status_code is not None else None, 
             ip_address if ip_address is not None else None, 
             cdn_status if cdn_status is not None else None, 
             cdn_name if cdn_name is not None else None, 
             title if title is not None else None, 
             webserver if webserver is not None else None, 
             webtech if webtech is not None else None, 
             cname if cname is not None else None, 
             timestamp, timestamp))
        
        conn.commit()
        print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Live subdomain '{url}' added to domain '{domain}' in workspace '{workspace}' with details: scheme={scheme}, method={method}, port={port}, status_code={status_code}, cdn_status={cdn_status}, cdn_name={cdn_name}, title={title}, webserver={webserver}, webtech={webtech}, cname={cname}")
 
def list_live_subdomain(url='*', subdomain='*', domain='*', workspace='*', scheme=None, method=None, port=None, status_code=None, ip=None, cdn_status=None, cdn_name=None, title=None, webserver=None, webtech=None, cname=None, create_time=None, update_time=None, brief=False):
    # Check if the workspace exists if workspace is not '*'
    if workspace != '*':
        cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
        if not cursor.fetchone():
            print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
            return

    # Base query for live subdomains
    query = """
        SELECT url, subdomain, domain, workspace, scheme, method, port, status_code, ip_address, cdn_status, 
               cdn_name, title, webserver, webtech, cname, created_at, updated_at 
        FROM live
    """
    parameters = []

    # If listing all assets, do not filter by workspace
    if workspace != '*':
        query += " WHERE workspace = ?"
        parameters.append(workspace)

    # Filter by specific URL
    if url != '*':
        query += " AND url = ?" if 'WHERE' in query else " WHERE url = ?"
        parameters.append(url)

    # Filter by subdomain
    if subdomain != '*':
        query += " AND subdomain = ?" if 'WHERE' in query else " WHERE subdomain = ?"
        parameters.append(subdomain)

    # Filter by domain
    if domain != '*':
        query += " AND domain = ?" if 'WHERE' in query else " WHERE domain = ?"
        parameters.append(domain)

    # Add other filters only if they are provided
    if scheme:
        query += " AND scheme = ?" if 'WHERE' in query else " WHERE scheme = ?"
        parameters.append(scheme)

    if method:
        query += " AND method = ?" if 'WHERE' in query else " WHERE method = ?"
        parameters.append(method)

    if port:
        query += " AND port = ?" if 'WHERE' in query else " WHERE port = ?"
        parameters.append(port)

    if status_code:
        query += " AND status_code = ?" if 'WHERE' in query else " WHERE status_code = ?"
        parameters.append(status_code)

    if ip:
        query += " AND ip_address = ?" if 'WHERE' in query else " WHERE ip_address = ?"
        parameters.append(ip)

    if cdn_status:
        query += " AND cdn_status = ?" if 'WHERE' in query else " WHERE cdn_status = ?"
        parameters.append(cdn_status)

    if cdn_name:
        query += " AND cdn_name = ?" if 'WHERE' in query else " WHERE cdn_name = ?"
        parameters.append(cdn_name)

    if title:
        query += " AND title = ?" if 'WHERE' in query else " WHERE title = ?"
        parameters.append(title)

    if webserver:
        query += " AND webserver = ?" if 'WHERE' in query else " WHERE webserver = ?"
        parameters.append(webserver)

    if webtech:
        query += " AND webtech LIKE ?" if 'WHERE' in query else " WHERE webtech LIKE ?"
        parameters.append(f"%{webtech}%")

    if cname:
        query += " AND cname = ?" if 'WHERE' in query else " WHERE cname = ?"
        parameters.append(cname)

    # Parse create_time and update_time and add time range filters
    if create_time:
        start_time, end_time = parse_time_range(create_time)
        query += " AND created_at BETWEEN ? AND ?" if 'WHERE' in query else " WHERE created_at BETWEEN ? AND ?"
        parameters.extend([start_time, end_time])

    if update_time:
        start_time, end_time = parse_time_range(update_time)
        query += " AND updated_at BETWEEN ? AND ?" if 'WHERE' in query else " WHERE updated_at BETWEEN ? AND ?"
        parameters.extend([start_time, end_time])

    # Execute the query
    cursor.execute(query, parameters)
    live_subdomains = cursor.fetchall()

    # Handle output
    if live_subdomains:
        if brief:
            print("\n".join(sub[0] for sub in live_subdomains))  # Just print URL for brief
        else:
            result = [
                {
                    "url": sub[0], "subdomain": sub[1], "domain": sub[2], "workspace": sub[3], "scheme": sub[4],
                    "method": sub[5], "port": sub[6], "status_code": sub[7], "ip": sub[8], "cdn_status": sub[9],
                    "cdn_name": sub[10], "title": sub[11], "webserver": sub[12], "webtech": sub[13], "cname": sub[14],
                    "created_at": sub[15], "updated_at": sub[16]
                }
                for sub in live_subdomains
            ]
            print(json.dumps(result, indent=4))
    else:
        print(f"{Fore.YELLOW}No live subdomains found.{Style.RESET_ALL}")

def delete_live_subdomain(url='*', subdomain='*', domain='*', workspace='*', scheme=None, method=None, port=None, status_code=None, ip_address=None, cdn_status=None, cdn_name=None, title=None, webserver=None, webtech=None, cname=None):
    # Check if the workspace exists if workspace is not '*'
    if workspace != '*':
        cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
        if not cursor.fetchone():
            print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
            return

    # Start building the delete query
    query = "DELETE FROM live WHERE workspace = ?" if workspace != '*' else "DELETE FROM live"
    params = []

    if workspace != '*':
        params.append(workspace)

    # Handle wildcards
    if subdomain != '*':
        query += " AND subdomain = ?"
        params.append(subdomain)

    if domain != '*':
        query += " AND domain = ?"
        params.append(domain)

    if url != '*':
        query += " AND url = ?"
        params.append(url)

    # Add filtering for each optional parameter
    if scheme:
        query += " AND scheme = ?"
        params.append(scheme)

    if method:
        query += " AND method = ?"
        params.append(method)

    if port:
        query += " AND port = ?"
        params.append(port)

    if status_code:
        query += " AND status_code = ?"
        params.append(status_code)

    if ip_address:
        query += " AND ip_address = ?"
        params.append(ip_address)

    if cdn_status:
        query += " AND cdn_status = ?"
        params.append(cdn_status)

    if cdn_name:
        query += " AND cdn_name = ?"
        params.append(cdn_name)

    if title:
        query += " AND title = ?"
        params.append(title)

    if webserver:
        query += " AND webserver = ?"
        params.append(webserver)

    if webtech:
        query += " AND webtech = ?"
        params.append(webtech)

    if cname:
        query += " AND cname = ?"
        params.append(cname)

    # Execute the delete query
    cursor.execute(query, params)
    conn.commit()

    # Confirm deletion
    if cursor.rowcount > 0:
        print(f"[+OK] Deleted {cursor.rowcount} live entries for workspace '{workspace}' with filters: "
              f"subdomain='{subdomain}', domain='{domain}', url='{url}', scheme='{scheme}', method='{method}', "
              f"port='{port}', status_code='{status_code}', ip_address='{ip_address}', cdn_status='{cdn_status}', "
              f"cdn_name='{cdn_name}', title='{title}', webserver='{webserver}', webtech='{webtech}', cname='{cname}'")
    else:
        print(f"[+INFO] No matching live entries found to delete for workspace '{workspace}' with the specified filters.")

def parse_time_range(time_range_str):
    # Handle time ranges in the format 'start_time,end_time'
    times = time_range_str.split(',')
    if len(times) == 1:
        # If only one time is provided, assume the end time is the same and use the entire range of that time point
        start_time, end_time = parse_single_time(times[0])
    elif len(times) == 2:
        # If two times are provided, parse the start and end times
        start_time = parse_single_time(times[0])[0]
        end_time = parse_single_time(times[1])[1]
    else:
        raise ValueError(f"Invalid time range format: {time_range_str}")
    return start_time, end_time

def parse_single_time(time_str):
    # Parse a single time and return start and end times
    formats = ['%Y-%m-%d-%H:%M', '%Y-%m-%d-%H', '%Y-%m-%d', '%Y-%m', '%Y']
    for fmt in formats:
        try:
            start_time = datetime.strptime(time_str, fmt)
            if fmt == '%Y-%m-%d-%H:%M':
                end_time = start_time + timedelta(minutes=1) - timedelta(seconds=1)
            elif fmt == '%Y-%m-%d-%H':
                end_time = start_time + timedelta(hours=1) - timedelta(seconds=1)
            elif fmt == '%Y-%m-%d':
                end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
            elif fmt == '%Y-%m':
                end_time = start_time.replace(month=start_time.month % 12 + 1, day=1) - timedelta(seconds=1)
            elif fmt == '%Y':
                end_time = start_time.replace(year=start_time.year + 1, month=1, day=1) - timedelta(seconds=1)
            return start_time, end_time
        except ValueError:
            continue
    raise ValueError(f"Invalid time format: {time_str}")

def main():
    parser = argparse.ArgumentParser(description='Manage workspaces, domains, and subdomains')
    sub_parser = parser.add_subparsers(dest='command')

    # Workspace commands
    workspace_parser = sub_parser.add_parser('workspace', help='Manage workspaces')
    workspace_action_parser = workspace_parser.add_subparsers(dest='action')

    # Create a new workspace
    workspace_action_parser.add_parser('create', help='Create a new workspace').add_argument('workspace', help='Name of the workspace')

    # List workspaces, with optional brief output
    list_workspaces_parser = workspace_action_parser.add_parser('list', help='List workspaces')
    list_workspaces_parser.add_argument('workspace', help="Workspace name or wildcard '*' for all workspaces")
    list_workspaces_parser.add_argument('--brief', action='store_true', help='Show only workspace names')
    
    # Delete a workspace
    workspace_action_parser.add_parser('delete', help='Delete a workspace').add_argument('workspace', help='Name of the workspace')

    # Domain commands
    domain_parser = sub_parser.add_parser('domain', help='Manage domains in a workspace')
    domain_action_parser = domain_parser.add_subparsers(dest='action')

    # Add a domain
    add_domain_parser = domain_action_parser.add_parser('add', help='Add a domain')
    add_domain_parser.add_argument('domain', help='Domain name')
    add_domain_parser.add_argument('workspace', help='Workspace name')

    # List domains in a workspace
    list_domains_parser = domain_action_parser.add_parser('list', help='List domains in a workspace')
    list_domains_parser.add_argument('workspace', help='Workspace name')
    list_domains_parser.add_argument('--brief', action='store_true', help='Show only domain names')

    # Delete a domain from a workspace
    delete_domain_parser = domain_action_parser.add_parser('delete', help='Delete a domain')
    delete_domain_parser.add_argument('domain', help='Domain name')
    delete_domain_parser.add_argument('workspace', help='Workspace name')

    # Subdomain commands
    subdomain_parser = sub_parser.add_parser('subdomain', help='Manage subdomains in a workspace')
    subdomain_action_parser = subdomain_parser.add_subparsers(dest='action')

    # Add a subdomain
    add_subdomain_parser = subdomain_action_parser.add_parser('add', help='Add a subdomain')
    add_subdomain_parser.add_argument('subdomain', help='Subdomain name')
    add_subdomain_parser.add_argument('domain', help='Domain name')
    add_subdomain_parser.add_argument('workspace', help='Workspace name')
    add_subdomain_parser.add_argument('--source', help='Source(s) (comma-separated)', nargs='*')
    add_subdomain_parser.add_argument('--scope', help='Scope (default: inscope)', choices=['inscope', 'outscope'], default='inscope')
    add_subdomain_parser.add_argument('--resolved', help='Resolved status (yes or no)', choices=['yes', 'no'], default='no')  # New resolved argument
    add_subdomain_parser.add_argument('--ip', default='none', help='IP address of the subdomain')
    add_subdomain_parser.add_argument('--cdn_status', default='no', choices=['yes', 'no'], help='Whether the subdomain uses a cdn_status')
    add_subdomain_parser.add_argument('--cdn_name', default='none', help='Name of the CDN provider')
    
    # List subdomains
    list_subdomains_parser = subdomain_action_parser.add_parser('list', help='List subdomains')
    list_subdomains_parser.add_argument('subdomain', help='Subdomain name or wildcard')
    list_subdomains_parser.add_argument('domain', help='Domain name or wildcard')
    list_subdomains_parser.add_argument('workspace', help='Workspace name')
    list_subdomains_parser.add_argument('--source', nargs='*', help='Filter by source(s)')
    list_subdomains_parser.add_argument('--source-only', action='store_true', help='Show only subdomains matching the specified source(s)')
    list_subdomains_parser.add_argument('--scope', help='Filter by scope', choices=['inscope', 'outscope'])
    list_subdomains_parser.add_argument('--resolved', choices=['yes', 'no'], help='Filter by resolved status')
    list_subdomains_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Filter by cdn_status status')
    list_subdomains_parser.add_argument('--ip', help='Filter by IP address')
    list_subdomains_parser.add_argument('--cdn_name', help='Filter by CDN provider name')
    list_subdomains_parser.add_argument('--brief', action='store_true', help='Show only subdomain names')
    list_subdomains_parser.add_argument('--create_time', help='Filter by creation time (e.g., 2024-09-29 or 2024-09). Supports time ranges (e.g., 2023-12-03-12:30,2024-03-10-12:30)')
    list_subdomains_parser.add_argument('--update_time', help='Filter by last update time (e.g., 2024-09-29 or 2024-09). Supports time ranges (e.g., 2023,2024)')


    # Adding subcommands for subdomain actions
    delete_subdomain_parser = subdomain_action_parser.add_parser('delete', help='Delete subdomains')
    delete_subdomain_parser.add_argument('subdomain', help='Subdomain to delete (use * to delete all)')
    delete_subdomain_parser.add_argument('domain', help='Domain name')
    delete_subdomain_parser.add_argument('workspace', help='Workspace name')
    delete_subdomain_parser.add_argument('--resolved', help='Filter by resolved status', choices=['yes', 'no'])
    delete_subdomain_parser.add_argument('--source', help='Filter by source')
    delete_subdomain_parser.add_argument('--scope', help='Filter by scope', choices=['inscope', 'outscope'])
    delete_subdomain_parser.add_argument('--ip', help='Filter by IP address')
    delete_subdomain_parser.add_argument('--cdn_status', help='Filter by cdn_status', choices=['yes', 'no'])
    delete_subdomain_parser.add_argument('--cdn_name', help='Filter by CDN name')
    
    live_parser = sub_parser.add_parser('live', help='Manage live subdomains')
    live_action_parser = live_parser.add_subparsers(dest='action')
    
    # Add live subdomain action
    add_live_subdomain_parser = live_action_parser.add_parser('add', help='Add a live subdomain')
    add_live_subdomain_parser.add_argument('url', help='URL of the live subdomain (e.g. https://www.google.com:443)')
    add_live_subdomain_parser.add_argument('subdomain', help='Subdomain (e.g. www.google.com)')
    add_live_subdomain_parser.add_argument('domain', help='Domain (e.g. google.com)')
    add_live_subdomain_parser.add_argument('workspace', help='Workspace (e.g. google_wk)')
    add_live_subdomain_parser.add_argument('--scheme', help='Scheme (http or https)')
    add_live_subdomain_parser.add_argument('--method', help='HTTP method')
    add_live_subdomain_parser.add_argument('--port', help='Port number', type=int)
    add_live_subdomain_parser.add_argument('--status_code', help='HTTP status code', type=int)
    add_live_subdomain_parser.add_argument('--ip', help='IP address of the live subdomain')
    add_live_subdomain_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Whether the live subdomain uses a CDN')
    add_live_subdomain_parser.add_argument('--cdn_name', help='Name of the CDN provider')
    add_live_subdomain_parser.add_argument('--title', help='Title of the live subdomain')
    add_live_subdomain_parser.add_argument('--webserver', help='Web server type (e.g. nginx)')
    add_live_subdomain_parser.add_argument('--webtech', help='Web technologies (comma-separated)')
    add_live_subdomain_parser.add_argument('--cname', help='CNAME of the live subdomain')

    # Add live subdomain list action
    list_live_subdomain_parser = live_action_parser.add_parser('list', help='List live subdomains')
    list_live_subdomain_parser.add_argument('url', help='URL of the live subdomain (e.g. https://www.google.com:443)')
    list_live_subdomain_parser.add_argument('subdomain', help='Subdomain name or wildcard (*)')
    list_live_subdomain_parser.add_argument('domain', help='Domain name or wildcard (*)')
    list_live_subdomain_parser.add_argument('workspace', help='Workspace name')
    list_live_subdomain_parser.add_argument('--scheme', help='Filter by scheme (http/https)')
    list_live_subdomain_parser.add_argument('--method', help='Filter by HTTP method')
    list_live_subdomain_parser.add_argument('--port', help='Filter by port', type=int)
    list_live_subdomain_parser.add_argument('--status_code', help='Filter by HTTP status code', type=int)
    list_live_subdomain_parser.add_argument('--ip', help='Filter by IP address')
    list_live_subdomain_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Filter by CDN status')
    list_live_subdomain_parser.add_argument('--cdn_name', help='Filter by CDN name')
    list_live_subdomain_parser.add_argument('--title', help='Filter by title of the live subdomain')
    list_live_subdomain_parser.add_argument('--webserver', help='Filter by webserver (e.g., nginx)')
    list_live_subdomain_parser.add_argument('--webtech', help='Filter by web technologies (comma-separated)')
    list_live_subdomain_parser.add_argument('--cname', help='Filter by CNAME of the live subdomain')
    list_live_subdomain_parser.add_argument('--create_time', help='Filter by creation time (e.g., 2024-09-29 or 2024-09). Supports time ranges (e.g., 2023-12-03-12:30,2024-03-10-12:30)')
    list_live_subdomain_parser.add_argument('--update_time', help='Filter by last update time (e.g., 2024-09-29 or 2024-09). Supports time ranges (e.g., 2023,2024)')
    list_live_subdomain_parser.add_argument('--brief', action='store_true', help='Show only subdomain names (brief output)')

    # Adding subcommands for live subdomain actions
    delete_live_subdomain_parser = live_action_parser.add_parser('delete', help='Delete live subdomains')
    delete_live_subdomain_parser.add_argument('url', help='URL of the live subdomain (use * to delete all for a subdomain)')
    delete_live_subdomain_parser.add_argument('subdomain', help='Subdomain (e.g. www.example.com)')
    delete_live_subdomain_parser.add_argument('domain', help='Domain (e.g. example.com)')
    delete_live_subdomain_parser.add_argument('workspace', help='Workspace (e.g. example_workspace)')
    delete_live_subdomain_parser.add_argument('--scheme', help='Filter by scheme (http/https)')
    delete_live_subdomain_parser.add_argument('--method', help='Filter by HTTP method')
    delete_live_subdomain_parser.add_argument('--port', help='Filter by port', type=int)
    delete_live_subdomain_parser.add_argument('--status_code', help='Filter by HTTP status code', type=int)
    delete_live_subdomain_parser.add_argument('--ip', help='Filter by IP address')
    delete_live_subdomain_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Filter by CDN status')
    delete_live_subdomain_parser.add_argument('--cdn_name', help='Filter by CDN name')
    delete_live_subdomain_parser.add_argument('--title', help='Filter by title of the live subdomain')
    delete_live_subdomain_parser.add_argument('--webserver', help='Filter by webserver (e.g., nginx)')
    delete_live_subdomain_parser.add_argument('--webtech', help='Filter by web technologies (comma-separated)')
    delete_live_subdomain_parser.add_argument('--cname', help='Filter by CNAME of the live subdomain')
    delete_live_subdomain_parser.add_argument('--create_time', help='Filter by creation time (e.g., 2024-09-29 or 2024-09). Supports time ranges (e.g., 2023-12-03-12:30,2024-03-10-12:30)')
    delete_live_subdomain_parser.add_argument('--update_time', help='Filter by last update time (e.g., 2024-09-29 or 2024-09). Supports time ranges (e.g., 2023,2024)')

    args = parser.parse_args()

    # Handle commands
    if args.command == 'workspace':
        if args.action == 'create':
            create_workspace(args.workspace)
        elif args.action == 'list':
            list_workspaces(workspace=args.workspace, brief=args.brief)
        elif args.action == 'delete':
            delete_workspace(args.workspace)

    elif args.command == 'domain':
        if args.action == 'add':
            add_domain(args.domain, args.workspace)
        elif args.action == 'list':
            list_domains(args.workspace, brief=args.brief)
        elif args.action == 'delete':
            delete_domain(args.domain if args.domain != '*' else '*', args.workspace)

    elif args.command == 'subdomain':
        if args.action == 'add':
            add_subdomain(
                args.subdomain,
                args.domain,
                args.workspace,
                sources=args.source,
                scope=args.scope,
                resolved=args.resolved,
                ip_address=args.ip,
                cdn_status=args.cdn_status,
                cdn_name=args.cdn_name
            )
        elif args.action == 'list':
            list_subdomains(
                args.subdomain,
                args.domain,
                args.workspace,
                args.source,
                args.scope,
                args.resolved,
                args.brief,
                args.source_only,
                args.cdn_status,
                args.ip,
                args.cdn_name,
                args.create_time,
                args.update_time
            )
        elif args.action == 'delete':
            if os.path.isfile(args.subdomain):
                with open(args.subdomain, 'r') as file:
                    subdomains = [line.strip() for line in file.readlines() if line.strip()]
                for subdomain in subdomains:
                    delete_subdomain(subdomain, args.domain, args.workspace, args.scope, args.source, args.resolved)
            else:
                delete_subdomain(
                    args.subdomain,
                    args.domain,
                    args.workspace,
                    args.scope,
                    args.source,
                    args.resolved,
                    args.ip,
                    args.cdn_status,
                    args.cdn_name
                ) if args.subdomain != '*' else delete_subdomain('*', args.domain, args.workspace, args.scope, args.source, args.resolved)

    elif args.command == 'live':
        if args.action == 'add':
            add_live_subdomain(
                args.url, args.subdomain, args.domain, args.workspace,
                scheme=args.scheme, method=args.method, port=args.port,
                status_code=args.status_code, ip_address=args.ip,
                cdn_status=args.cdn_status, cdn_name=args.cdn_name,
                title=args.title, webserver=args.webserver,
                webtech=args.webtech, cname=args.cname
            )
        elif args.action == 'list':
            list_live_subdomain(
                args.url,
                args.subdomain,
                args.domain,
                args.workspace,
                scheme=args.scheme,
                method=args.method,
                port=args.port,
                status_code=args.status_code,
                ip=args.ip,
                cdn_status=args.cdn_status,
                cdn_name=args.cdn_name,
                title=args.title,
                webserver=args.webserver,
                webtech=args.webtech,
                cname=args.cname,
                create_time=args.create_time,
                update_time=args.update_time,
                brief=args.brief
            )
        elif args.action == 'delete':
            delete_live_subdomain(
                args.url,
                args.subdomain,
                args.domain,
                args.workspace,
                scheme=args.scheme,
                method=args.method,
                port=args.port,
                status_code=args.status_code,
                ip_address=args.ip,
                cdn_status=args.cdn_status,
                cdn_name=args.cdn_name,
                title=args.title,
                webserver=args.webserver,
                webtech=args.webtech,
                cname=args.cname
            )
            
if __name__ == "__main__":
    main()

# Close the database connection when done
conn.close()
