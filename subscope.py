import sqlite3
import json
import argparse
import os
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect('scopes.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_name TEXT PRIMARY KEY,
    created_at TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS domains (
    domain TEXT PRIMARY KEY,
    workspace_name TEXT,
    created_at TEXT,
    FOREIGN KEY(workspace_name) REFERENCES workspaces(workspace_name)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS subdomains (
    subdomain TEXT,
    domain TEXT,
    workspace_name TEXT,
    source TEXT,
    scope TEXT,
    resolved TEXT,
    ip_address TEXT DEFAULT 'none',
    cdn TEXT DEFAULT 'no',
    cdn_name TEXT DEFAULT 'none',
    created_at TEXT,
    updated_at TEXT,
    PRIMARY KEY(subdomain, domain, workspace_name)
)
''')


# Function to create a new workspace
def create_workspace(workspace_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    # Check if the workspace already exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    existing_workspace = cursor.fetchone()

    if existing_workspace:
        print(f"Error: Workspace '{workspace_name}' already exists.")
        return  # Exit the function if the workspace already exists

    # If the workspace does not exist, create a new one
    cursor.execute("INSERT INTO workspaces (workspace_name, created_at) VALUES (?, ?)", (workspace_name, timestamp))
    conn.commit()
    print(f"Workspace '{workspace_name}' created.")


# Function to list all workspaces
def list_workspaces(brief=False):
    cursor.execute("SELECT workspace_name, created_at FROM workspaces")
    workspaces = cursor.fetchall()

    # If no workspaces exist, return early
    if not workspaces:
        return  # No output if there are no workspaces

    if brief:
        for workspace in workspaces:
            print(workspace[0])  # Print each workspace name on a new line
    else:
        workspace_list = [{'workspace_name': workspace[0], 'created_at': workspace[1]} for workspace in workspaces]
        print(json.dumps({"workspaces": workspace_list}, indent=4))

# Function to delete a workspace and all its associated domains and subdomains
def delete_workspace(workspace_name):
    if workspace_name == '*':
        # Delete all subdomains associated with all workspaces
        cursor.execute("DELETE FROM subdomains")

        # Delete all domains associated with all workspaces
        cursor.execute("DELETE FROM domains")

        # Delete all workspaces
        cursor.execute("DELETE FROM workspaces")
        
        conn.commit()
        print("All workspaces, along with their associated domains and subdomains, have been deleted.")
        return  # Exit the function after deleting all

    # Check if the specified workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    if not cursor.fetchone():
        print(f"Workspace '{workspace_name}' does not exist.")
        return  # Exit the function if the workspace does not exist

    # Delete all subdomains associated with the specified workspace
    cursor.execute("DELETE FROM subdomains WHERE workspace_name = ?", (workspace_name,))
    
    # Delete all domains associated with the specified workspace
    cursor.execute("DELETE FROM domains WHERE workspace_name = ?", (workspace_name,))
    
    # Delete the specified workspace
    cursor.execute("DELETE FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    
    conn.commit()
    print(f"Workspace '{workspace_name}', all associated domains, and subdomains deleted.")


# Function to add a domain to a workspace
def add_domain_to_workspace(domain_or_file, workspace_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    existing_workspace = cursor.fetchone()

    if not existing_workspace:
        print(f"Error: Workspace '{workspace_name}' does not exist.")
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
        cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace_name = ?", (domain, workspace_name))
        existing_domain = cursor.fetchone()

        if existing_domain:
            print(f"Domain '{domain}' already exists in workspace '{workspace_name}'.")
        else:
            try:
                cursor.execute("INSERT INTO domains (domain, workspace_name, created_at) VALUES (?, ?, ?)", (domain, workspace_name, timestamp))
                conn.commit()
                print(f"Domain '{domain}' added to workspace '{workspace_name}'.")
            except sqlite3.IntegrityError:
                print(f"Error: Domain '{domain}' already exists in the database.")

# Function to list all domains in a workspace
def list_domains(workspace_name, brief=False):
    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    if not cursor.fetchone():
        print(f"Workspace '{workspace_name}' does not exist.")
        return  # Exit the function if the workspace does not exist

    # Fetch domains associated with the existing workspace
    cursor.execute("SELECT domain, created_at FROM domains WHERE workspace_name = ?", (workspace_name,))
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


# Function to add a subdomain (or subdomains from a file) to a domain in a workspace
def add_subdomain_to_domain(subdomain_or_file, domain, workspace_name, sources=None, scope='outscope', resolved='no', ip_address='none', cdn='no', cdn_name='none'):
    # Custom timestamp format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    if not cursor.fetchone():
        print(f"Workspace '{workspace_name}' does not exist.")
        return  # Exit if the workspace does not exist

    # Check if the domain exists
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace_name = ?", (domain, workspace_name))
    if not cursor.fetchone():
        print(f"Domain '{domain}' does not exist in workspace '{workspace_name}'.")
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
        cursor.execute("SELECT source FROM subdomains WHERE subdomain = ? AND domain = ? AND workspace_name = ?", 
                       (subdomain, domain, workspace_name))
        existing = cursor.fetchone()

        if existing:
            # If the subdomain exists, get the current sources
            current_sources = existing[0].split(", ")
            # Create a set to avoid duplicates
            current_sources_set = set(current_sources)

            # Append new sources to the set
            if sources:
                new_sources = [src.strip() for src in sources]
                current_sources_set.update(new_sources)

            # Create the updated source string
            updated_source_str = ", ".join(current_sources_set)

            # Update the subdomain with the new sources
            cursor.execute("""
                UPDATE subdomains 
                SET source = ?, updated_at = ?, scope = ?, resolved = ?, ip_address = ?, cdn = ?, cdn_name = ?
                WHERE subdomain = ? AND domain = ? AND workspace_name = ?""", 
                (updated_source_str, timestamp, scope, resolved, ip_address, cdn, cdn_name, subdomain, domain, workspace_name))
            conn.commit()
            print(f"Updated subdomain '{subdomain}' in domain '{domain}' with sources: {updated_source_str}, scope: {scope}, resolved: {resolved}, IP: {ip_address}, CDN: {cdn}, CDN Name: {cdn_name}")
        else:
            # Join the sources if provided, otherwise set to 'manual'
            new_source_str = ", ".join(sources) if sources else "manual"
            # Insert the new subdomain with additional columns
            cursor.execute("""
                INSERT INTO subdomains (subdomain, domain, workspace_name, source, scope, resolved, ip_address, cdn, cdn_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (subdomain, domain, workspace_name, new_source_str, scope, resolved, ip_address, cdn, cdn_name, timestamp, timestamp))
            conn.commit()
            print(f"Subdomain '{subdomain}' added to domain '{domain}' in workspace '{workspace_name}' with sources: {new_source_str}, scope: {scope}, resolved: {resolved}, IP: {ip_address}, CDN: {cdn}, CDN Name: {cdn_name}")

def list_subdomains(domain, workspace_name, sources=None, scope=None, resolved=None, brief=False, source_only=False, cdn=None, ip=None, cdn_name=None):
    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    if not cursor.fetchone():
        print(f"Workspace '{workspace_name}' does not exist.")
        return  # Exit if the workspace does not exist

    # Check if the domain exists in the specified workspace
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace_name = ?", (domain, workspace_name))
    if not cursor.fetchone() and domain != '*':
        # Domain does not exist, no output is needed
        return  # Exit if the domain does not exist

    # Base query
    query = """
        SELECT subdomain, domain, source, scope, resolved, ip_address, cdn, cdn_name, created_at, updated_at 
        FROM subdomains 
        WHERE workspace_name = ?
    """
    parameters = [workspace_name]

    # Handle wildcard for domain
    if domain != '*':
        query += " AND domain = ?"
        parameters.append(domain)

    # Add filtering for scope
    if scope:
        query += " AND scope = ?"
        parameters.append(scope)

    # Add filtering for resolved status
    if resolved:
        query += " AND resolved = ?"
        parameters.append(resolved)

    # Add filtering for cdn
    if cdn:
        query += " AND cdn = ?"
        parameters.append(cdn)

    # Add filtering for ip_address
    if ip:
        query += " AND ip_address = ?"
        parameters.append(ip)

    # Add filtering for cdn_name
    if cdn_name:
        query += " AND cdn_name = ?"
        parameters.append(cdn_name)

    # Execute the query
    cursor.execute(query, parameters)
    subdomains = cursor.fetchall()

    if subdomains:
        filtered_subdomains = []
        
        # If sources are provided, filter the results
        if sources:
            for subdomain in subdomains:
                # Check if any source in the list is included in the subdomain source
                subdomain_sources = [src.strip() for src in subdomain[2].split(',')]
                if any(source in subdomain_sources for source in sources):
                    filtered_subdomains.append(subdomain)
        else:
            # If no specific source is provided, keep all subdomains
            filtered_subdomains = subdomains

        # Further filter for --source-only if specified
        if source_only and sources:
            filtered_subdomains = [sub for sub in filtered_subdomains if sub[2].strip() == sources[0]]

        if filtered_subdomains:
            if brief:
                # Print only the subdomain names
                print("\n".join(sub[0] for sub in filtered_subdomains))
            else:
                result = [
                    {
                        "subdomain": sub[0], "domain": sub[1], "workspace_name": workspace_name,
                        "source": sub[2], "scope": sub[3], "resolved": sub[4],
                        "ip_address": sub[5], "cdn": sub[6], "cdn_name": sub[7],
                        "created_at": sub[8], "updated_at": sub[9]
                    }
                    for sub in filtered_subdomains
                ]
                print(json.dumps(result, indent=4))

def delete_subdomain(subdomain, domain, workspace_name, scope=None, source=None):
    # Check if the workspace exists
    cursor.execute("SELECT * FROM workspaces WHERE workspace_name = ?", (workspace_name,))
    if not cursor.fetchone():
        print(f"Workspace '{workspace_name}' does not exist.")
        return  # Exit if the workspace does not exist

    # Check if the domain exists in the specified workspace
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND workspace_name = ?", (domain, workspace_name))
    if not cursor.fetchone() and domain != '*':
        print(f"Domain '{domain}' does not exist in workspace '{workspace_name}'.")
        return  # Exit if the domain does not exist

    if os.path.isfile(subdomain):  # Check if the subdomain is a file
        with open(subdomain, 'r') as file:
            subdomains = [line.strip() for line in file if line.strip()]
        
        for sub in subdomains:
            delete_single_subdomain(sub, domain, workspace_name, scope, source)
    else:
        delete_single_subdomain(subdomain, domain, workspace_name, scope, source)

def delete_single_subdomain(sub, domain, workspace_name, scope=None, source=None, resolved=None, ip_address=None, cdn=None, cdn_name=None):
    # Check if the subdomain exists
    cursor.execute("SELECT * FROM subdomains WHERE subdomain = ? AND domain = ? AND workspace_name = ?", 
                   (sub, domain, workspace_name))
    if not cursor.fetchone():
        print(f"Subdomain '{sub}' does not exist in domain '{domain}' in workspace '{workspace_name}'.")
        return  # Exit if the subdomain does not exist

    if sub == '*':
        # Start building the delete query for all subdomains
        query = "DELETE FROM subdomains WHERE domain = ? AND workspace_name = ?"
        params = [domain, workspace_name]

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

        # Add filtering for CDN status
        if cdn:
            query += " AND cdn = ?"
            params.append(cdn)

        # Add filtering for CDN name
        if cdn_name:
            query += " AND cdn_name = ?"
            params.append(cdn_name)

        cursor.execute(query, params)
        conn.commit()
        print(f"All matching subdomains deleted from domain '{domain}' in workspace '{workspace_name}' with source '{source}', resolved status '{resolved}', scope '{scope}', IP address '{ip_address}', CDN status '{cdn}', and CDN name '{cdn_name}'.")
    else:
        # Delete a single subdomain with optional filters
        query = "DELETE FROM subdomains WHERE subdomain = ? AND domain = ? AND workspace_name = ?"
        params = [sub, domain, workspace_name]

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

        # Add filtering for CDN status
        if cdn:
            query += " AND cdn = ?"
            params.append(cdn)

        # Add filtering for CDN name
        if cdn_name:
            query += " AND cdn_name = ?"
            params.append(cdn_name)

        cursor.execute(query, params)
        conn.commit()
        print(f"Subdomain '{sub}' deleted from domain '{domain}' in workspace '{workspace_name}' with IP address '{ip_address}', CDN status '{cdn}', and CDN name '{cdn_name}'.")

# Function to delete all subdomains with a specific source
def delete_subdomains_by_source(domain, workspace_name, source):
    cursor.execute("DELETE FROM subdomains WHERE domain = ? AND workspace_name = ? AND source LIKE ?", 
                   (domain, workspace_name, f"%{source}%"))
    conn.commit()
    print(f"All subdomains with source '{source}' deleted from domain '{domain}' in workspace '{workspace_name}'.")


# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description='Manage workspaces, domains, and subdomains')
    sub_parser = parser.add_subparsers(dest='command')

    # Workspace commands
    workspace_parser = sub_parser.add_parser('workspace', help='Manage workspaces')
    workspace_action_parser = workspace_parser.add_subparsers(dest='action')

    # Create a new workspace
    workspace_action_parser.add_parser('create', help='Create a new workspace').add_argument('workspace_name', help='Name of the workspace')

    # List all workspaces
    workspace_action_parser.add_parser('list', help='List workspaces').add_argument('--brief', action='store_true', help='Show only workspace names')

    # Delete a workspace
    workspace_action_parser.add_parser('delete', help='Delete a workspace').add_argument('workspace_name', help='Name of the workspace')

    # Domain commands
    domain_parser = sub_parser.add_parser('domain', help='Manage domains in a workspace')
    domain_action_parser = domain_parser.add_subparsers(dest='action')

    # Add a domain
    add_domain_parser = domain_action_parser.add_parser('add', help='Add a domain')
    add_domain_parser.add_argument('domain', help='Domain name')
    add_domain_parser.add_argument('workspace_name', help='Workspace name')

    # List domains in a workspace
    list_domains_parser = domain_action_parser.add_parser('list', help='List domains in a workspace')
    list_domains_parser.add_argument('workspace_name', help='Workspace name')
    list_domains_parser.add_argument('--brief', action='store_true', help='Show only domain names')

    # Delete a domain from a workspace
    delete_domain_parser = domain_action_parser.add_parser('delete', help='Delete a domain')
    delete_domain_parser.add_argument('domain', help='Domain name')
    delete_domain_parser.add_argument('workspace_name', help='Workspace name')

    # Subdomain commands
    subdomain_parser = sub_parser.add_parser('subdomain', help='Manage subdomains in a workspace')
    subdomain_action_parser = subdomain_parser.add_subparsers(dest='action')

    # Add a subdomain
    add_subdomain_parser = subdomain_action_parser.add_parser('add', help='Add a subdomain')
    add_subdomain_parser.add_argument('subdomain', help='Subdomain name')
    add_subdomain_parser.add_argument('domain', help='Domain name')
    add_subdomain_parser.add_argument('workspace_name', help='Workspace name')
    add_subdomain_parser.add_argument('--source', help='Source(s) (comma-separated)', nargs='*')
    add_subdomain_parser.add_argument('--scope', help='Scope (default: inscope)', choices=['inscope', 'outscope'], default='inscope')
    add_subdomain_parser.add_argument('--resolved', help='Resolved status (yes or no)', choices=['yes', 'no'], default='no')  # New resolved argument
    add_subdomain_parser.add_argument('--ip', default='none', help='IP address of the subdomain')
    add_subdomain_parser.add_argument('--cdn', default='no', choices=['yes', 'no'], help='Whether the subdomain uses a CDN')
    add_subdomain_parser.add_argument('--cdn_name', default='none', help='Name of the CDN provider')
    
    # List subdomains
    list_subdomains_parser = subdomain_action_parser.add_parser('list', help='List subdomains')
    list_subdomains_parser.add_argument('domain', help='Domain name')
    list_subdomains_parser.add_argument('workspace_name', help='Workspace name')
    list_subdomains_parser.add_argument('--source', nargs='*', help='Filter by source(s)')
    list_subdomains_parser.add_argument('--source-only', action='store_true', help='Show only subdomains matching the specified source(s)')
    list_subdomains_parser.add_argument('--scope', help='Filter by scope', choices=['inscope', 'outscope'])
    list_subdomains_parser.add_argument('--resolved', choices=['yes', 'no'], help='Filter by resolved status')
    list_subdomains_parser.add_argument('--cdn', choices=['yes', 'no'], help='Filter by CDN status')
    list_subdomains_parser.add_argument('--ip', help='Filter by IP address')
    list_subdomains_parser.add_argument('--cdn_name', help='Filter by CDN provider name')
    list_subdomains_parser.add_argument('--brief', action='store_true', help='Show only subdomain names')


    # Adding subcommands for subdomain actions
    delete_subdomain_parser = subdomain_action_parser.add_parser('delete', help='Delete subdomains')
    delete_subdomain_parser.add_argument('subdomain', help='Subdomain to delete (use * to delete all)')
    delete_subdomain_parser.add_argument('domain', help='Domain name')
    delete_subdomain_parser.add_argument('workspace_name', help='Workspace name')
    delete_subdomain_parser.add_argument('--resolved', help='Filter by resolved status', choices=['yes', 'no'])
    delete_subdomain_parser.add_argument('--source', help='Filter by source')
    delete_subdomain_parser.add_argument('--scope', help='Filter by scope', choices=['inscope', 'outscope'])
    delete_subdomain_parser.add_argument('--ip', help='Filter by IP address')
    delete_subdomain_parser.add_argument('--cdn', help='Filter by CDN status', choices=['yes', 'no'])
    delete_subdomain_parser.add_argument('--cdn_name', help='Filter by CDN name')

    args = parser.parse_args()

    # Handle commands
    if args.command == 'workspace':
        if args.action == 'create':
            create_workspace(args.workspace_name)
        elif args.action == 'list':
            list_workspaces(brief=args.brief)
        elif args.action == 'delete':
            delete_workspace(args.workspace_name)

    elif args.command == 'domain':
        if args.action == 'add':
            add_domain_to_workspace(args.domain, args.workspace_name)
        elif args.action == 'list':
            list_domains(args.workspace_name, brief=args.brief)
        elif args.action == 'delete':
            delete_domain_from_workspace(args.domain, args.workspace_name)

    elif args.command == 'subdomain':
        if args.action == 'add':
            # Include additional parameters for source, scope, resolved, ip_address, cdn, and cdn_name
            add_subdomain_to_domain(args.subdomain, args.domain, args.workspace_name, sources=args.source, scope=args.scope, resolved=args.resolved, ip_address=args.ip, cdn=args.cdn, cdn_name=args.cdn_name)
        elif args.action == 'list':
            # Call the list_subdomains function with the new parameters
            list_subdomains(args.domain, args.workspace_name, args.source, args.scope, args.resolved, args.brief, args.source_only, args.cdn, args.ip, args.cdn_name)
        elif args.action == 'delete':
            # Check if the subdomain argument is a file
            if os.path.isfile(args.subdomain):
                # Read subdomains from file and delete each one
                with open(args.subdomain, 'r') as file:
                    subdomains = [line.strip() for line in file.readlines() if line.strip()]
                for subdomain in subdomains:
                    delete_single_subdomain(subdomain, args.domain, args.workspace_name, args.scope, args.source, args.resolved)
            else:
                # Check if '*' is specified for deleting all subdomains
                if args.subdomain == '*':
                    delete_single_subdomain(args.subdomain, args.domain, args.workspace_name, args.scope, args.source, args.resolved, args.ip, args.cdn, args.cdn_name)
                else:
                    delete_single_subdomain(args.subdomain, args.domain, args.workspace_name)

if __name__ == "__main__":
    main()

# Close the database connection when done
conn.close()
