#!/usr/bin/python3

import argparse
import sqlite3
import json
import os
import colorama
from datetime import datetime, timedelta
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init()

# Connect to SQLite database
conn = sqlite3.connect('scopes.db')
cursor = conn.cursor()

# Create tables if they don't exist
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

# Function to create a new workspace
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

# Function to list workspaces
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

# Function to delete a workspace and all its associated domains and subdomains
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

# Function to add a domain to a workspace
def add_domain_to_workspace(domain_or_file, workspace):
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

# Function to list all domains in a workspace
def list_domains(workspace, brief=False):
    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
        return  # Exit the function if the workspace does not exist

    # Fetch domains associated with the existing workspace
    cursor.execute("SELECT domain, created_at FROM domains WHERE workspace = ?", (workspace,))
    domains = cursor.fetchall()

    # Check if there are any domains to display
    if not domains:
        return  # Exit if there are no domains; no output will be printed

    if brief:
        for domain in domains:
            print(domain[0])  # Print only the domain names
    else:
        domain_list = [{'domain': domain[0], 'created_at': domain[1]} for domain in domains]
        print(json.dumps({"domains": domain_list}, indent=4))

# Function to delete a domain and its subdomains from a workspace
def delete_domain_from_workspace(domain, workspace):
    if domain == '*':
        # Delete all subdomains from the workspace
        cursor.execute("DELETE FROM subdomains WHERE workspace = ?", (workspace,))
        
        # Delete all domains from the workspace
        cursor.execute("DELETE FROM domains WHERE workspace = ?", (workspace,))
        
        conn.commit()
        print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} All domains and their subdomains deleted from workspace '{workspace}'")
    else:
        # Delete all subdomains associated with the domain in the workspace
        cursor.execute("DELETE FROM subdomains WHERE domain = ? AND workspace = ?", (domain, workspace))
        
        # Delete the domain itself from the workspace
        cursor.execute("DELETE FROM domains WHERE domain = ? AND workspace = ?", (domain, workspace))
        
        conn.commit()
        print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} Domain '{domain}' and all its subdomains deleted from workspace '{workspace}'")

# Function to add a subdomain (or subdomains from a file) to a domain in a workspace
def add_subdomain_to_domain(subdomain_or_file, domain, workspace, sources=None, scope='outscope', resolved='no', ip_address='none', cdn_status='no', cdn_name='none'):
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


def list_subdomains(subdomain, domain, workspace, sources=None, scope=None, resolved=None, brief=False, source_only=False, cdn_status=None, ip=None, cdn_name=None, create_time=None, update_time=None):
    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
        return

    # Base query
    query = """
        SELECT subdomain, domain, source, scope, resolved, ip_address, cdn_status, cdn_name, created_at, updated_at 
        FROM subdomains 
        WHERE workspace = ?
    """
    parameters = [workspace]

    # Handle wildcard for domain and subdomain
    if domain != '*':
        query += " AND domain = ?"
        parameters.append(domain)

    if subdomain != '*':
        query += " AND subdomain = ?"
        parameters.append(subdomain)

    # If listing all subdomains for all domains
    if domain == '*' and subdomain == '*':
        # No extra filters applied
        query = """
            SELECT subdomain, domain, source, scope, resolved, ip_address, cdn_status, cdn_name, created_at, updated_at 
            FROM subdomains 
            WHERE workspace = ?
        """
        parameters = [workspace]
    
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
                        "subdomain": sub[0], "domain": sub[1], "workspace": workspace,
                        "source": sub[2], "scope": sub[3], "resolved": sub[4],
                        "ip_address": sub[5], "cdn_status": sub[6], "cdn_name": sub[7],
                        "created_at": sub[8], "updated_at": sub[9]
                    }
                    for sub in filtered_subdomains
                ]
                print(json.dumps(result, indent=4))

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

def delete_subdomain(subdomain, domain, workspace, scope=None, source=None):
    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace = ?", (workspace,))
    if not cursor.fetchone():
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Workspace '{workspace}' does not exist")
        return  # Exit if the workspace does not exist
    # Check if the domain exists in the specified workspace
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace = ?", (domain, workspace))
    if not cursor.fetchone() and domain != '*':
        print(f"{Fore.RED}{Style.BRIGHT}[-ER]{Style.RESET_ALL} Domain '{domain}' does not exist in workspace '{workspace}'")
        return  # Exit if the domain does not exist
    if os.path.isfile(subdomain):  # Check if the subdomain is a file
        with open(subdomain, 'r') as file:
            subdomains = [line.strip() for line in file if line.strip()]
        for sub in subdomains:
            delete_single_subdomain(sub, domain, workspace, scope, source)
    else:
        delete_single_subdomain(subdomain, domain, workspace, scope, source)

def delete_single_subdomain(sub, domain, workspace, scope=None, source=None, resolved=None, ip_address=None, cdn_status=None, cdn_name=None):
    if sub == '*':
        # Start building the delete query for all subdomains
        query = "DELETE FROM subdomains WHERE domain = ? AND workspace = ?"
        params = [domain, workspace]

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
        print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} All matching subdomains deleted from domain '{Fore.YELLOW}{Style.BRIGHT}{domain}{Style.RESET_ALL}' in workspace '{Fore.YELLOW}{Style.BRIGHT}{workspace}{Style.RESET_ALL}' with sources: {Fore.YELLOW}{Style.BRIGHT}{source}{Style.RESET_ALL}, scope: {Fore.YELLOW}{Style.BRIGHT}{scope}{Style.RESET_ALL}, resolved: {Fore.YELLOW}{Style.BRIGHT}{resolved}{Style.RESET_ALL}, IP: {Fore.YELLOW}{Style.BRIGHT}{ip_address}{Style.RESET_ALL}, cdn_status: {Fore.YELLOW}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}, CDN Name: {Fore.YELLOW}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}")
    else:
        # Delete a single subdomain with optional filters
        query = "DELETE FROM subdomains WHERE subdomain = ? AND domain = ? AND workspace = ?"
        params = [sub, domain, workspace]

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

# Function to delete all subdomains with a specific source
def delete_subdomains_by_source(domain, workspace, source):
    cursor.execute("DELETE FROM subdomains WHERE domain = ? AND workspace = ? AND source LIKE ?", 
                   (domain, workspace, f"%{source}%"))
    conn.commit()
    print(f"{Fore.GREEN}{Style.BRIGHT}[+OK]{Style.RESET_ALL} All subdomains with source '{source}' deleted from domain '{domain}' in workspace '{workspace}'")


# Main function to handle command-line arguments
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
            add_domain_to_workspace(args.domain, args.workspace)
        elif args.action == 'list':
            list_domains(args.workspace, brief=args.brief)
        elif args.action == 'delete':
            # Check if the user wants to delete all domains in the workspace
            if args.domain == '*':
                delete_domain_from_workspace('*', args.workspace)
            else:
                delete_domain_from_workspace(args.domain, args.workspace)

    elif args.command == 'subdomain':
        if args.action == 'add':
            # Handle the addition of subdomains
            add_subdomain_to_domain(
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
            # Call the modified list_subdomains function
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
            # Check if the subdomain argument is a file
            if os.path.isfile(args.subdomain):
                # Read subdomains from file and delete each one
                with open(args.subdomain, 'r') as file:
                    subdomains = [line.strip() for line in file.readlines() if line.strip()]
                for subdomain in subdomains:
                    delete_single_subdomain(subdomain, args.domain, args.workspace, args.scope, args.source, args.resolved)
            else:
                # Check if '*' is specified for deleting all subdomains
                if args.subdomain == '*':
                    delete_single_subdomain(args.subdomain, args.domain, args.workspace, args.scope, args.source, args.resolved, args.ip, args.cdn_status, args.cdn_name)
                else:
                    delete_single_subdomain(args.subdomain, args.domain, args.workspace)

if __name__ == "__main__":
    main()

# Close the database connection when done
conn.close()
