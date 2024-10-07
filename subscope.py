#!/usr/bin/python3

import argparse
import sqlite3
import json
import os
import colorama
from datetime import datetime, timedelta
from colorama import Fore, Back, Style


colorama.init()

ERROR_COLOR = colorama.Fore.RED
INFO_COLOR = colorama.Fore.YELLOW
SUCCESS_COLOR = colorama.Fore.GREEN
RESET_COLOR = colorama.Style.RESET_ALL

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS
conn = sqlite3.connect('scopes.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS programs (program TEXT PRIMARY KEY, created_at TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS domains (domain TEXT PRIMARY KEY, program TEXT, scope TEXT, created_at TEXT, updated_at TEXT, FOREIGN KEY(program) REFERENCES programs(program))")
cursor.execute("CREATE TABLE IF NOT EXISTS subdomains (subdomain TEXT, domain TEXT, program TEXT, source TEXT, scope TEXT, resolved TEXT, ip_address TEXT DEFAULT 'none', cdn_status TEXT DEFAULT 'no', cdn_name TEXT DEFAULT 'none', created_at TEXT, updated_at TEXT, PRIMARY KEY(subdomain, domain, program))")
cursor.execute("CREATE TABLE IF NOT EXISTS urls (url TEXT, subdomain TEXT, domain TEXT, program TEXT, scheme TEXT, method TEXT, port INTEGER, status_code INTEGER, scope TEXT, ip_address TEXT, cdn_status TEXT, cdn_name TEXT, title TEXT, webserver TEXT, webtech TEXT, cname TEXT, location TEXT, created_at TIMESTAMP, updated_at TIMESTAMP, PRIMARY KEY(url, subdomain, domain, program))")
cursor.execute("CREATE TABLE IF NOT EXISTS cidrs (ip TEXT NOT NULL, program TEXT NOT NULL, cidr TEXT, asn INTEGER, port TEXT, service TEXT, cves TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(ip, program))")

def add_program(program):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Check if the program already exists with a COUNT query for efficiency
        cursor.execute("SELECT COUNT(1) FROM programs WHERE program = ?", (program,))
        exists = cursor.fetchone()[0]

        if exists:
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding program | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} already exists")
            return

        # If the program does not exist, create a new one
        cursor.execute("INSERT INTO programs (program, created_at) VALUES (?, ?)", (program, timestamp))
        conn.commit()

        print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | adding program | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} created")

    except sqlite3.DatabaseError as e:
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding program | database error: {e}")

def list_programs(program='*', brief=False, count=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # For potential logging
    try:
        # Fetch programs from the database
        if program == '*':
            cursor.execute("SELECT program, created_at FROM programs")
        else:
            cursor.execute("SELECT program, created_at FROM programs WHERE program = ?", (program,))
        
        programs = cursor.fetchall()

        # If no programs exist, display a message
        if not programs:
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | listing program | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} not found")
            return

        # Handle counting records
        if count:
            count_result = len(programs)
            print(count_result)
            return

        # Brief mode: print only program names
        if brief:
            for ws in programs:
                print(ws[0])  # Print each program name in brief mode
        else:
            # Detailed mode: print program with created_at as JSON
            program_list = [{'program': ws[0], 'created_at': ws[1]} for ws in programs]
            print(json.dumps({"programs": program_list}, indent=4))

    except sqlite3.DatabaseError as e:
        print(f"{Fore.RED}error{Style.RESET_ALL} | listing programs | database error: {e}")

def delete_program(program, delete_all=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def count_entries(program=None):
            if program == '*':
                cursor.execute("SELECT COUNT(*) FROM cidrs")
                ip_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM urls")
                url_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM subdomains")
                subdomain_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM domains")
                domain_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM programs")
                program_count = cursor.fetchone()[0]
            else:
                cursor.execute("SELECT COUNT(*) FROM cidrs WHERE program = ?", (program,))
                ip_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM urls WHERE program = ?", (program,))
                url_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM subdomains WHERE program = ?", (program,))
                subdomain_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM domains WHERE program = ?", (program,))
                domain_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM programs WHERE program = ?", (program,))
                program_count = 1 if cursor.fetchone() else 0

            return program_count, domain_count, subdomain_count, url_count, ip_count

    try:
        if program == '*':
            if delete_all:
                # Delete all related data for all programs
                program_count, domain_count, subdomain_count, url_count, ip_count = count_entries('*')

                cursor.execute("DELETE FROM cidrs")
                cursor.execute("DELETE FROM urls")
                cursor.execute("DELETE FROM subdomains")
                cursor.execute("DELETE FROM domains")
                cursor.execute("DELETE FROM programs")
                conn.commit()

                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting all programs | all programs with program: {program_count}, domains: {domain_count}, subdomains: {subdomain_count}, urls: {url_count}, ips: {ip_count}")
            else:
                # Only delete all programs
                cursor.execute("DELETE FROM programs")
                conn.commit()
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting programs | deleted all programs")
        
        else:
            if delete_all:
                # Delete all related data for the specified program
                program_count, domain_count, subdomain_count, url_count, ip_count = count_entries(program)

                cursor.execute("DELETE FROM cidrs WHERE program = ?", (program,))
                cursor.execute("DELETE FROM urls WHERE program = ?", (program,))
                cursor.execute("DELETE FROM subdomains WHERE program = ?", (program,))
                cursor.execute("DELETE FROM domains WHERE program = ?", (program,))
                cursor.execute("DELETE FROM programs WHERE program = ?", (program,))
                conn.commit()

                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting all program of {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} | program: {program_count}, domains: {domain_count}, subdomains: {subdomain_count}, urls: {url_count}, ips: {ip_count}")
                return

            cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
            if not cursor.fetchone():
                print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting program | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} not found")
                return
            else:
                cursor.execute("DELETE FROM programs WHERE program = ?", (program,))
                conn.commit()
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting program | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} deleted")

    except sqlite3.DatabaseError as e:
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting program | database error: {e}")

def add_domain(domain_or_file, program, scope=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the program exists
    cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
    if not cursor.fetchone():
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding domain | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
        return

    # Check if the input is a file
    if os.path.isfile(domain_or_file):
        with open(domain_or_file, 'r') as file:
            domains = [line.strip() for line in file if line.strip()]
    else:
        domains = [domain_or_file]

    for domain in domains:
        cursor.execute("SELECT * FROM domains WHERE domain = ? AND program = ?", (domain, program))
        existing_domain = cursor.fetchone()

        update_fields = {}

        if existing_domain:
            current_scope = existing_domain[2]  # Assuming scope is in the 3rd column

            # Only update the scope if a new scope is provided
            if scope is not None and current_scope != scope:
                update_fields['scope'] = scope

            # Update the domain only if there are changes
            if update_fields:
                update_query = "UPDATE domains SET "
                update_query += ", ".join(f"{col} = ?" for col in update_fields.keys())
                update_query += ", updated_at = ? WHERE domain = ? AND program = ?"
                cursor.execute(update_query, (*update_fields.values(), timestamp, domain, program))
                conn.commit()
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | updating domain | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} updated to {update_fields.get('scope', current_scope)}")
            else:
                print(f"{timestamp} | {Fore.YELLOW}notice{Style.RESET_ALL} | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} unchanged")
        else:
            # Insert new domain with both created_at and updated_at
            new_scope = scope if scope is not None else 'inscope'
            cursor.execute("INSERT INTO domains (domain, program, scope, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", 
                           (domain, program, new_scope, timestamp, timestamp))
            conn.commit()
            print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | adding domain | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} added to program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL}")

def list_domains(domain='*', program='*', brief=False, count=False, scope=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # For potential logging
    
    # Check if the program is specific or all
    if program != '*':
        cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
        if not cursor.fetchone():
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | listing domain | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
            return
        
        query = "SELECT domain, program, scope, created_at, updated_at FROM domains WHERE program = ?"
        params = [program]

        if domain != '*':
            query += " AND domain = ?"
            params.append(domain)

        if scope:
            query += " AND scope = ?"
            params.append(scope)

        cursor.execute(query, params)
    else:
        query = "SELECT domain, program, scope, created_at, updated_at FROM domains"
        params = []

        if domain != '*':
            query += " WHERE domain = ?"
            params.append(domain)

        if scope:
            query += " WHERE scope = ?"
            params.append(scope)

        cursor.execute(query, params)

    domains = cursor.fetchall()

    if not domains:
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | listing domain | no domains found")
        return

    if count:
        count_result = len(domains)
        print(count_result)
        return

    if brief:
        for domain in domains:
            print(domain[0])  # domain[0] will have the domain name
    else:
        # Create a list of domains including all required information
        domain_list = [
            {
                'domain': domain[0],
                'program': domain[1],
                'scope': domain[2],
                'created_at': domain[3],
                'updated_at': domain[4]
            }
            for domain in domains
        ]
        print(json.dumps({"domains": domain_list}, indent=4))

def delete_domain(domain='*', program='*', scope=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # For potential logging

    if program != '*':
        cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
        if not cursor.fetchone():
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting domain | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
            return

    if domain == '*':
        # Deleting all records
        counts = {
            'urls': cursor.execute("SELECT COUNT(*) FROM urls").fetchone()[0],
            'subdomains': cursor.execute("SELECT COUNT(*) FROM subdomains").fetchone()[0],
            'domains': cursor.execute("SELECT COUNT(*) FROM domains").fetchone()[0]
        }

        # Delete records based on scope or all if scope is None
        if scope is None:
            cursor.execute("DELETE FROM urls")
            cursor.execute("DELETE FROM subdomains")
            cursor.execute("DELETE FROM domains")
        else:
            cursor.execute("DELETE FROM urls WHERE scope = ?", (scope,))
            cursor.execute("DELETE FROM subdomains WHERE scope = ?", (scope,))
            cursor.execute("DELETE FROM domains WHERE scope = ?", (scope,))

        conn.commit()

        if counts['domains'] == 0:
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting domain | domain table is empty")
        else:
            print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting domain | deleted {Fore.BLUE}{Style.BRIGHT}{counts['domains']}{Style.RESET_ALL} domains, {Fore.BLUE}{Style.BRIGHT}{counts['subdomains']}{Style.RESET_ALL} subdomains and {Fore.BLUE}{Style.BRIGHT}{counts['urls']}{Style.RESET_ALL} urls")
    else:
        if program == '*':
            # Deleting records across all programs
            counts = {
                'urls': cursor.execute("SELECT COUNT(domain) FROM urls WHERE domain = ?", (domain,)).fetchone()[0],
                'subdomains': cursor.execute("SELECT COUNT(domain) FROM subdomains WHERE domain = ?", (domain,)).fetchone()[0],
                'domains': cursor.execute("SELECT COUNT(domain) FROM domains WHERE domain = ?", (domain,)).fetchone()[0]
            }

            # Delete based on scope or all if scope is None
            if scope is None:
                cursor.execute("DELETE FROM subdomains WHERE domain = ?", (domain,))
                cursor.execute("DELETE FROM urls WHERE domain = ?", (domain,))
                cursor.execute("DELETE FROM domains WHERE domain = ?", (domain,))
            else:
                cursor.execute("DELETE FROM subdomains WHERE domain = ? AND scope = ?", (domain, scope))
                cursor.execute("DELETE FROM urls WHERE domain = ? AND scope = ?", (domain, scope))
                cursor.execute("DELETE FROM domains WHERE domain = ? AND scope = ?", (domain, scope))

            conn.commit()

            if counts['domains'] == 0:
                print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting domain | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} does not exist")
            else:
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting domain | deleted {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} with {Fore.BLUE}{Style.BRIGHT}{counts['subdomains']}{Style.RESET_ALL} subdomains and {Fore.BLUE}{Style.BRIGHT}{counts['urls']}{Style.RESET_ALL} urls")
        else:
            # Deleting records in a specific program
            counts = {
                'urls': cursor.execute("SELECT COUNT(domain) FROM urls WHERE domain = ? AND program = ?", (domain, program)).fetchone()[0],
                'subdomains': cursor.execute("SELECT COUNT(domain) FROM subdomains WHERE domain = ? AND program = ?", (domain, program)).fetchone()[0],
                'domains': cursor.execute("SELECT COUNT(domain) FROM domains WHERE domain = ? AND program = ?", (domain, program)).fetchone()[0]
            }

            # Delete based on scope or all if scope is None
            if scope is None:
                cursor.execute("DELETE FROM subdomains WHERE domain = ? AND program = ?", (domain, program))
                cursor.execute("DELETE FROM domains WHERE domain = ? AND program = ?", (domain, program))
            else:
                cursor.execute("DELETE FROM subdomains WHERE domain = ? AND program = ? AND scope = ?", (domain, program, scope))
                cursor.execute("DELETE FROM domains WHERE domain = ? AND program = ? AND scope = ?", (domain, program, scope))

            conn.commit()

            if counts['domains'] == 0:
                print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting domain | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} does not exist")
            else:
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting domain | deleted {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} from {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} with {Fore.BLUE}{Style.BRIGHT}{counts['subdomains']}{Style.RESET_ALL} subdomains and {Fore.BLUE}{Style.BRIGHT}{counts['urls']}{Style.RESET_ALL} urls")

def add_subdomain(subdomain_or_file, domain, program, sources=None, unsources=None, scope='outscope', resolved='no', ip_address='none', cdn_status='no', cdn_name='none', unip=None, uncdn_name=None):
    # Custom timestamp format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the program exists
    cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
    if not cursor.fetchone():
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding subdomain | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
        return

    # Check if the domain exists
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND program = ?", (domain, program))
    if not cursor.fetchone():
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding subdomain | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} does not exist in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL}")
        return

    # Check if the input is a file
    if os.path.isfile(subdomain_or_file):
        # Read subdomains from the file
        with open(subdomain_or_file, 'r') as file:
            subdomains = [line.strip() for line in file if line.strip()]
    else:
        subdomains = [subdomain_or_file]

    # Process each subdomain
    for subdomain in subdomains:
        cursor.execute("SELECT * FROM subdomains WHERE subdomain = ? AND domain = ? AND program = ?", 
                       (subdomain, domain, program))
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

            # Handle unsourcing
            if unsources:
                current_sources = existing[3].split(", ") if existing[3] else []
                for unsource in unsources:
                    unsource = unsource.strip()
                    if unsource in current_sources:
                        current_sources.remove(unsource)  # Remove specified source
                updated_sources = ", ".join(current_sources) if current_sources else ""
                if updated_sources != existing[3]:  # Check if sources have changed
                    update_fields['source'] = updated_sources

            if scope != existing[4]:  # Assuming 4th column is 'scope'
                update_fields['scope'] = scope

            if resolved != 'no' and resolved != existing[5]:  # Assuming 5th column is 'resolved'
                update_fields['resolved'] = resolved

            if ip_address != 'none' and ip_address != existing[6]:  # Assuming 6th column is 'ip_address'
                update_fields['ip_address'] = ip_address
            
            # Handle removal of ip_address
            if unip and existing[6] != 'none':  # Assuming 6th column is 'ip_address'
                update_fields['ip_address'] = 'none'  # Set to 'none' to indicate removal

            if cdn_status != 'no' and cdn_status != existing[7]:  # Assuming 7th column is 'cdn_status'
                update_fields['cdn_status'] = cdn_status
            
            # Handle removal of cdn_name
            if uncdn_name and existing[8] != 'none':  # Assuming 8th column is 'cdn_name'
                update_fields['cdn_name'] = 'none'  # Set to 'none' to indicate removal

            if cdn_name != 'none' and cdn_name != existing[8]:  # Assuming 8th column is 'cdn_name'
                update_fields['cdn_name'] = cdn_name

            # Always allow updates for 'cdn_status' from yes to no or vice versa
            if cdn_status != existing[7]:  # Assuming 7th column is 'cdn_status'
                update_fields['cdn_status'] = cdn_status

            # Update the subdomain only if there are changes
            if update_fields:
                update_query = "UPDATE subdomains SET "
                update_query += ", ".join(f"{col} = ?" for col in update_fields.keys())
                update_query += ", updated_at = ? WHERE subdomain = ? AND domain = ? AND program = ?"
                cursor.execute(update_query, (*update_fields.values(), timestamp, subdomain, domain, program))
                conn.commit()
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | updating subdomain | subdomain {Fore.BLUE}{Style.BRIGHT}{subdomain}{Style.RESET_ALL} in domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} with updates: {Fore.BLUE}{Style.BRIGHT}{update_fields}{Style.RESET_ALL}")
            else:
                print(f"{timestamp} | {Fore.YELLOW}info{Style.RESET_ALL} | updating subdomain | No any update for subdomain {Fore.BLUE}{Style.BRIGHT}{subdomain}{Style.RESET_ALL} in domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL}")
        else:
            # If the subdomain does not exist, create it with no defaults
            new_source_str = ", ".join(sources) if sources else ""  # No default value
            cursor.execute("""
                INSERT INTO subdomains (subdomain, domain, program, source, scope, resolved, ip_address, cdn_status, cdn_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (subdomain, domain, program, new_source_str, scope, resolved, ip_address, cdn_status, cdn_name, timestamp, timestamp))
            conn.commit()
            print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | adding subdomain | Subdomain {Fore.BLUE}{Style.BRIGHT}{subdomain}{Style.RESET_ALL} added to domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.BRIGHT} with sources: {Fore.BLUE}{Style.BRIGHT}{new_source_str}{Style.RESET_ALL}, scope: {Fore.BLUE}{Style.BRIGHT}{scope}{Style.RESET_ALL}, resolved: {Fore.BLUE}{Style.BRIGHT}{resolved}{Style.RESET_ALL}, IP: {Fore.BLUE}{Style.BRIGHT}{ip_address}{Style.RESET_ALL}, cdn_status: {Fore.BLUE}{Style.BRIGHT}{cdn_status}{Style.RESET_ALL}, CDN Name: {Fore.BLUE}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}")

def list_subdomains(subdomain='*', domain='*', program='*', sources=None, scope=None, resolved=None, brief=False, source_only=False, cdn_status=None, ip=None, cdn_name=None, create_time=None, update_time=None, count=False):
    # Check if program exists if specified
    if program != '*':
        cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
        if not cursor.fetchone():
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | listing subdomain | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
            return

    # Base query and parameters
    query = """
        SELECT subdomain, domain, source, scope, resolved, ip_address, cdn_status, cdn_name, created_at, updated_at, program 
        FROM subdomains 
    """
    parameters = []
    filters = []

    # Add filtering for program if not '*'
    if program != '*':
        filters.append("program = ?")
        parameters.append(program)

    # Handle wildcard for domain and subdomain
    if domain != '*':
        filters.append("domain = ?")
        parameters.append(domain)

    if subdomain != '*':
        filters.append("subdomain = ?")
        parameters.append(subdomain)

    # Add filtering for scope
    if scope:
        filters.append("scope = ?")
        parameters.append(scope)

    # Add filtering for resolved status
    if resolved:
        filters.append("resolved = ?")
        parameters.append(resolved)

    # Add filtering for cdn_status
    if cdn_status:
        filters.append("cdn_status = ?")
        parameters.append(cdn_status)

    # Add filtering for ip_address
    if ip:
        filters.append("ip_address = ?")
        parameters.append(ip)

    # Add filtering for cdn_name
    if cdn_name:
        filters.append("cdn_name = ?")
        parameters.append(cdn_name)

    # Parse create_time and update_time and add time range filters
    if create_time:
        start_time, end_time = parse_time_range(create_time)
        filters.append("created_at BETWEEN ? AND ?")
        parameters.extend([start_time, end_time])

    if update_time:
        start_time, end_time = parse_time_range(update_time)
        filters.append("updated_at BETWEEN ? AND ?")
        parameters.extend([start_time, end_time])

    # Construct final query with filters
    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Execute the query
    cursor.execute(query, parameters)
    subdomains = cursor.fetchall()

    # Handle counting records
    if count:
        count_result = len(subdomains)
        print(count_result)
        return

    # Filter results by source if provided
    filtered_subdomains = []
    if subdomains:
        if sources:
            for sub in subdomains:
                subdomain_sources = [src.strip() for src in sub[2].split(',')]
                if any(source in subdomain_sources for source in sources):
                    filtered_subdomains.append(sub)
        else:
            filtered_subdomains = subdomains

        # Further filter for --source-only
        if source_only and sources:
            filtered_subdomains = [sub for sub in filtered_subdomains if sub[2].strip() == sources[0]]

        # Output results
        if filtered_subdomains:
            if brief:
                print("\n".join(sub[0] for sub in filtered_subdomains))
            else:
                result = [
                    {
                        "subdomain": sub[0], 
                        "domain": sub[1], 
                        "program": sub[10],
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

def delete_subdomain(sub='*', domain='*', program='*', scope=None, source=None, resolved=None, ip_address=None, cdn_status=None, cdn_name=None):
    # Custom timestamp format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if program exists
    if program != '*':
        cursor.execute("SELECT COUNT(1) FROM programs WHERE program = ?", (program,))
        if cursor.fetchone()[0] == 0:
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting subdomain | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
            return

    # Check if domain exists
    if domain != '*':
        cursor.execute("SELECT COUNT(1) FROM domains WHERE domain = ?", (domain,))
        if cursor.fetchone()[0] == 0:
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting subdomain | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} does not exist")
            return

    # Check if subdomain exists before deletion
    if sub != '*':
        cursor.execute("SELECT COUNT(1) FROM subdomains WHERE subdomain = ? AND domain = ? AND program = ?", (sub, domain, program))
        if cursor.fetchone()[0] == 0:
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting subdomain | subdomain {Fore.BLUE}{Style.BRIGHT}{sub}{Style.RESET_ALL} does not exist in domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} and program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL}")
            return

    # Build the filter message to display which filters were used
    filter_msg = f"subdomain={sub}"
    if domain != "*":
        filter_msg += f", domain={domain}"
    if program != "*":
        filter_msg += f", program={program}"
    if scope:
        filter_msg += f", scope={scope}"
    if source:
        filter_msg += f", source={source}"
    if resolved:
        filter_msg += f", resolved={resolved}"
    if ip_address:
        filter_msg += f", ip_address={ip_address}"
    if cdn_status:
        filter_msg += f", cdn_status={cdn_status}"
    if cdn_name:
        filter_msg += f", cdn_name={cdn_name}"

    # Continue with the deletion process in the subdomains table
    total_deleted = 0  # Keep track of total deletions

    if sub == '*':
        # Deleting all subdomains from all domains and programs
        query = "DELETE FROM subdomains WHERE 1=1"
        params = []

        if domain != '*':
            query += " AND domain = ?"
            params.append(domain)

        if program != '*':
            query += " AND program = ?"
            params.append(program)

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

        # Execute delete query for the subdomains table
        cursor.execute(query, params)
        total_deleted = cursor.rowcount  # Get the count of deleted rows
        conn.commit()

        if total_deleted > 0:
            print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting subdomain | deleted {total_deleted} matching entries from {Fore.BLUE}{Style.BRIGHT}subdomains{Style.RESET_ALL} table with filters: {Fore.BLUE}{Style.BRIGHT}{filter_msg}{Style.RESET_ALL}")

    else:
        # Delete a single subdomain with optional filters
        query = "DELETE FROM subdomains WHERE subdomain = ?"
        params = [sub]

        if domain != '*':
            query += " AND domain = ?"
            params.append(domain)

        if program != '*':
            query += " AND program = ?"
            params.append(program)

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

        # Execute delete query for the subdomains table
        cursor.execute(query, params)
        total_deleted = cursor.rowcount  # Get the count of deleted rows
        conn.commit()

        if total_deleted > 0:
            print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting subdomain | deleted {total_deleted} matching entries from {Fore.BLUE}{Style.BRIGHT}subdomains{Style.RESET_ALL} table with filters: {Fore.BLUE}{Style.BRIGHT}{filter_msg}{Style.RESET_ALL}")

    if total_deleted == 0:
        print(f"{timestamp} | {Fore.YELLOW}info{Style.RESET_ALL} | deleting subdomain | no subdomains were deleted with filters: {Fore.BLUE}{Style.BRIGHT}{filter_msg}{Style.RESET_ALL}")

def add_url(url, subdomain, domain, program, scheme=None, method=None, port=None, status_code=None, scope=None, ip_address=None, cdn_status=None, cdn_name=None, title=None, webserver=None, webtech=None, cname=None, location=None):
    # Custom timestamp format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the program exists
    cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
    if not cursor.fetchone():
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding url | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
        return

    # Check if the domain exists
    cursor.execute("SELECT * FROM domains WHERE domain = ? AND program = ?", (domain, program))
    if not cursor.fetchone():
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding url | domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} does not exist in program '{program}'")
        return

    # Check if the subdomain exists
    cursor.execute("SELECT * FROM subdomains WHERE subdomain = ? AND domain = ? AND program = ?", (subdomain, domain, program))
    if not cursor.fetchone():
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding url | subdomain {Fore.BLUE}{Style.BRIGHT}{subdomain}{Style.RESET_ALL} in domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} does not exist in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL}")
        return
    # Check if the url exists
    cursor.execute("SELECT * FROM urls WHERE url = ? AND subdomain = ? AND domain = ? AND program = ?", (url, subdomain, domain, program))
    existing = cursor.fetchone()

    update_fields = {}

    if existing:
        # Subdomain exists, check for updates
        if scheme is not None and scheme != existing[4]:
            update_fields['scheme'] = scheme
        if method is not None and method != existing[5]:
            update_fields['method'] = method
        if port is not None and port != existing[6]:
            update_fields['port'] = port
        if status_code is not None and status_code != existing[7]:
            update_fields['status_code'] = status_code
        if scope is not None and scope != existing[8]:
            update_fields['scope'] = scope
        if ip_address is not None and ip_address != existing[9]:
            update_fields['ip_address'] = ip_address
        if cdn_status is not None and cdn_status != existing[10]:
            update_fields['cdn_status'] = cdn_status
        if cdn_name is not None and cdn_name != existing[11]:
            update_fields['cdn_name'] = cdn_name
        if title is not None and title != existing[12]:
            update_fields['title'] = title
        if webserver is not None and webserver != existing[13]:
            update_fields['webserver'] = webserver
        if webtech is not None and webtech != existing[14]:
            update_fields['webtech'] = webtech
        if cname is not None and cname != existing[15]:
            update_fields['cname'] = cname
        if location is not None and location != existing[16]:
            update_fields['location'] = location

        # Always update the timestamp
        if update_fields:
            update_query = "UPDATE urls SET " + ", ".join(f"{col} = ?" for col in update_fields) + ", updated_at = ? WHERE url = ? AND subdomain = ? AND domain = ? AND program = ?"
            cursor.execute(update_query, (*update_fields.values(), timestamp, url, subdomain, domain, program))
            conn.commit()
            print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | updating url | url {Fore.BLUE}{Style.BRIGHT}{url}{Style.RESET_ALL} in subdomain {Fore.BLUE}{Style.BRIGHT}{subdomain}{Style.RESET_ALL} in domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} with updates: {Fore.BLUE}{Style.BRIGHT}{update_fields}{Style.RESET_ALL}")
        else:
            print(f"{timestamp} | {Fore.YELLOW}info{Style.RESET_ALL} | updating url | No update for url {Fore.BLUE}{Style.BRIGHT}{url}{Style.RESET_ALL}")
    else:
        # Insert new url
        cursor.execute(""" 
            INSERT INTO urls (url, subdomain, domain, program, scheme, method, port, status_code, scope, ip_address, cdn_status, cdn_name, title, webserver, webtech, cname, location, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (url, subdomain, domain, program, 
             scheme if scheme is not None else None, 
             method if method is not None else None, 
             port if port is not None else None, 
             status_code if status_code is not None else None, 
             scope if scope is not None else None,  
             ip_address if ip_address is not None else None, 
             cdn_status if cdn_status is not None else None, 
             cdn_name if cdn_name is not None else None, 
             title if title is not None else None, 
             webserver if webserver is not None else None, 
             webtech if webtech is not None else None, 
             cname if cname is not None else None, 
             location if location is not None else None,  # Add location in insert
             timestamp, timestamp))
        
        conn.commit()
        print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | adding url | url {Fore.BLUE}{Style.BRIGHT}{url}{Style.RESET_ALL} added to subdomain {Fore.BLUE}{Style.BRIGHT}{subdomain}{Style.RESET_ALL} in domain {Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL} in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} with details: scheme={Fore.BLUE}{Style.BRIGHT}{scheme}{Style.RESET_ALL}, method={Fore.BLUE}{Style.BRIGHT}{method}{Style.RESET_ALL}, port={Fore.BLUE}{Style.BRIGHT}{port}{Style.RESET_ALL}, status_code={Fore.BLUE}{Style.BRIGHT}{status_code}{Style.RESET_ALL}, location={Fore.BLUE}{Style.BRIGHT}{location}{Style.RESET_ALL}, scope={Fore.BLUE}{Style.BRIGHT}{scope}{Style.RESET_ALL}, cdn_status={Fore.BLUE}{Style.BRIGHT}{cdn_status}{Style.RESET_ALL}, cdn_name={Fore.BLUE}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}, title={Fore.BLUE}{Style.BRIGHT}{title}{Style.RESET_ALL}, webserver={Fore.BLUE}{Style.BRIGHT}{webserver}{Style.RESET_ALL}, webtech={Fore.BLUE}{Style.BRIGHT}{webtech}{Style.RESET_ALL}, cname={Fore.BLUE}{Style.BRIGHT}{cname}{Style.RESET_ALL}")

def list_urls(url='*', subdomain='*', domain='*', program='*', scheme=None, method=None, port=None, 
               status_code=None, ip=None, cdn_status=None, cdn_name=None, title=None, 
               webserver=None, webtech=None, cname=None, create_time=None, update_time=None, 
               brief=False, scope=None, location=None, count=False):
    # Check if the program exists if program is not '*'
    if program != '*':
        cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
        if not cursor.fetchone():
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | listing url | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
            return

    # Base query for urls
    query = "SELECT url, subdomain, domain, program, scheme, method, port, status_code, ip_address, cdn_status, cdn_name, title, webserver, webtech, cname, location, created_at, updated_at FROM urls"
    parameters = []

    # Building the WHERE clause
    where_clauses = []
    if program != '*':
        where_clauses.append("program = ?")
        parameters.append(program)
    if url != '*':
        where_clauses.append("url = ?")
        parameters.append(url)
    if subdomain != '*':
        where_clauses.append("subdomain = ?")
        parameters.append(subdomain)
    if domain != '*':
        where_clauses.append("domain = ?")
        parameters.append(domain)
    if scope:
        where_clauses.append("scope = ?")
        parameters.append(scope)
    if scheme:
        where_clauses.append("scheme = ?")
        parameters.append(scheme)
    if method:
        where_clauses.append("method = ?")
        parameters.append(method)
    if port:
        where_clauses.append("port = ?")
        parameters.append(port)
    if status_code:
        where_clauses.append("status_code = ?")
        parameters.append(status_code)
    if ip:
        where_clauses.append("ip_address = ?")
        parameters.append(ip)
    if cdn_status:
        where_clauses.append("cdn_status = ?")
        parameters.append(cdn_status)
    if cdn_name:
        where_clauses.append("cdn_name = ?")
        parameters.append(cdn_name)
    if title:
        where_clauses.append("title = ?")
        parameters.append(title)
    if webserver:
        where_clauses.append("webserver = ?")
        parameters.append(webserver)
    if webtech:
        where_clauses.append("webtech LIKE ?")
        parameters.append(f"%{webtech}%")
    if cname:
        where_clauses.append("cname = ?")
        parameters.append(cname)
    if location:
        where_clauses.append("location = ?")
        parameters.append(location)
    if create_time:
        start_time, end_time = parse_time_range(create_time)
        where_clauses.append("created_at BETWEEN ? AND ?")
        parameters.extend([start_time, end_time])
    if update_time:
        start_time, end_time = parse_time_range(update_time)
        where_clauses.append("updated_at BETWEEN ? AND ?")
        parameters.extend([start_time, end_time])

    # Combine base query with where clauses
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # If count is requested, modify the query
    if count:
        query = "SELECT COUNT(*) FROM urls" + (" WHERE " + " AND ".join(where_clauses) if where_clauses else "")
        cursor.execute(query, parameters)
        count_result = cursor.fetchone()[0]
        print(count_result)
        return

    # Execute the final query
    cursor.execute(query, parameters)
    live_urls = cursor.fetchall()

    # Handle output
    if live_urls:
        if brief:
            print("\n".join(sub[0] for sub in live_urls))  # Just print URL for brief
        else:
            result = [
                {
                    "url": sub[0], "subdomain": sub[1], "domain": sub[2], "program": sub[3], "scheme": sub[4],
                    "method": sub[5], "port": sub[6], "status_code": sub[7], "ip_address": sub[8], "cdn_status": sub[9],
                    "cdn_name": sub[10], "title": sub[11], "webserver": sub[12], "webtech": sub[13], "cname": sub[14],
                    "location": sub[15], "created_at": sub[16], "updated_at": sub[17]
                }
                for sub in live_urls
            ]
            print(json.dumps(result, indent=4))

def delete_url(url='*', subdomain='*', domain='*', program='*', scope=None, scheme=None, 
                          method=None, port=None, status_code=None, ip_address=None, 
                          cdn_status=None, cdn_name=None, title=None, webserver=None, 
                          webtech=None, cname=None):
    # Check if the program exists if program is not '*'
    if program != '*':
        cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
        if not cursor.fetchone():
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | deleting url | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
            return

    # Start building the delete query
    query = "DELETE FROM urls"
    params = []
    filters = []

    # Handle filtering for each parameter
    if program != '*':
        filters.append("program = ?")
        params.append(program)

    if subdomain != '*':
        filters.append("subdomain = ?")
        params.append(subdomain)

    if domain != '*':
        filters.append("domain = ?")
        params.append(domain)

    if url != '*':
        filters.append("url = ?")
        params.append(url)

    if scope:
        filters.append("scope = ?")
        params.append(scope)

    if scheme:
        filters.append("scheme = ?")
        params.append(scheme)

    if method:
        filters.append("method = ?")
        params.append(method)

    if port:
        filters.append("port = ?")
        params.append(port)

    if status_code:
        filters.append("status_code = ?")
        params.append(status_code)

    if ip_address:
        filters.append("ip_address = ?")
        params.append(ip_address)

    if cdn_status:
        filters.append("cdn_status = ?")
        params.append(cdn_status)

    if cdn_name:
        filters.append("cdn_name = ?")
        params.append(cdn_name)

    if title:
        filters.append("title = ?")
        params.append(title)

    if webserver:
        filters.append("webserver = ?")
        params.append(webserver)

    if webtech:
        filters.append("webtech = ?")
        params.append(webtech)

    if cname:
        filters.append("cname = ?")
        params.append(cname)

    # Add the filters to the query if there are any
    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Execute the delete query
    cursor.execute(query, params)
    conn.commit()

    # Confirm deletion
    if cursor.rowcount > 0:
        print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | deleting url | deleted {Fore.BLUE}{Style.BRIGHT}{cursor.rowcount}{Style.RESET_ALL} live entries for program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} with filters: "
              f"subdomain={Fore.BLUE}{Style.BRIGHT}{subdomain}{Style.RESET_ALL}, domain={Fore.BLUE}{Style.BRIGHT}{domain}{Style.RESET_ALL}, url={Fore.BLUE}{Style.BRIGHT}{url}{Style.RESET_ALL}, scope={Fore.BLUE}{Style.BRIGHT}{scope}{Style.RESET_ALL}, "
              f"scheme={Fore.BLUE}{Style.BRIGHT}{scheme}{Style.RESET_ALL}, method={Fore.BLUE}{Style.BRIGHT}{method}{Style.RESET_ALL}, "
              f"port='{port}', status_code='{status_code}', ip_address='{ip_address}', cdn_status='{cdn_status}', "
              f"cdn_name={Fore.BLUE}{Style.BRIGHT}{cdn_name}{Style.RESET_ALL}, title={Fore.BLUE}{Style.BRIGHT}{title}{Style.RESET_ALL}, "
              f"webserver={Fore.BLUE}{Style.BRIGHT}{webserver}{Style.RESET_ALL}, webtech={Fore.BLUE}{Style.BRIGHT}{webtech}{Style.RESET_ALL}, "
              f"cname={Fore.BLUE}{Style.BRIGHT}{cname}{Style.RESET_ALL}")

def add_ip(ip, program, cidr=None, asn=None, port=None, service=None, cves=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the program exists
    cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
    if not cursor.fetchone():
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | adding IP | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
        return

    # Process CVEs as a list (if provided)
    cves_list = ', '.join(cves) if cves else None

    # Convert ports to a list of strings if provided and remove duplicates
    ports = list(map(str, port)) if port else None
    if ports:
        ports = list(set(ports))  # Remove duplicates
        ports.sort()

    # Start a transaction
    conn.execute("BEGIN TRANSACTION;")

    try:
        # Check if the IP already exists in the specified program
        cursor.execute("SELECT port, service, cves, cidr, asn FROM cidrs WHERE ip = ? AND program = ?", (ip, program))
        existing_entry = cursor.fetchone()

        update_fields = {}
        
        if existing_entry:
            existing_ports, existing_service, existing_cves, existing_cidr, existing_asn = existing_entry
            
            # Update fields if parameters are provided
            if ports is not None:
                ports_str = ', '.join(ports)
                if sorted(existing_ports.split(',')) != sorted(ports):
                    update_fields['port'] = ports_str

            if service is not None and service != existing_service:
                update_fields['service'] = service
            
            if cves_list is not None and cves_list != existing_cves:
                update_fields['cves'] = cves_list
            
            if cidr is not None and cidr != existing_cidr:
                update_fields['cidr'] = cidr
            
            if asn is not None and asn != existing_asn:
                update_fields['asn'] = asn

            # Update the entry only if there are changes
            if update_fields:
                set_clause = ', '.join(f"{key} = ?" for key in update_fields.keys())
                cursor.execute(f'''UPDATE cidrs 
                                  SET {set_clause}, updated_at = ? 
                                  WHERE ip = ? AND program = ?''',
                               (*[update_fields[key] for key in update_fields.keys()], timestamp, ip, program))
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | updating IP | IP {Fore.BLUE}{Style.BRIGHT}{ip}{Style.RESET_ALL} updated in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} with updates: {Fore.BLUE}{Style.BRIGHT}{update_fields}{Style.RESET_ALL}")
            else:
                print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | updating IP | IP {Fore.BLUE}{Style.BRIGHT}{ip}{Style.RESET_ALL} is unchanged in program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL}")
        else:
            # Insert a new record with the current timestamp
            ports_str = ', '.join(ports) if ports else None
            cursor.execute('''INSERT INTO cidrs (ip, program, cidr, asn, port, service, cves, created_at, updated_at)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (ip, program, cidr, asn, ports_str, service, cves_list, timestamp, timestamp))
            print(f"{timestamp} | {Fore.GREEN}success{Style.RESET_ALL} | adding IP | IP {Fore.BLUE}{Style.BRIGHT}{ip}{Style.RESET_ALL} added to program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} with {{ 'port': {ports_str} }}")

        # Commit the transaction
        conn.commit()

    except sqlite3.IntegrityError as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | updating IP | {str(e)}")
    except Exception as e:
        # Rollback the transaction in case of any other error
        conn.rollback()
        print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | updating IP | {str(e)}")

def list_ip(ip='*', program='*', cidr=None, asn=None, port=None, service=None, 
            cves=None, brief=False, create_time=None, update_time=None, count=False):
    # Get the current timestamp for logging purposes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the program exists if program is not '*'
    if program != '*':
        cursor.execute("SELECT * FROM programs WHERE program = ?", (program,))
        if not cursor.fetchone():
            print(f"{timestamp} | {Fore.RED}error{Style.RESET_ALL} | listing IP | program {Fore.BLUE}{Style.BRIGHT}{program}{Style.RESET_ALL} does not exist")
            return

    # Base query for listing IPs
    query = "SELECT ip, cidr, asn, port, service, created_at, updated_at, program, cves FROM cidrs"
    parameters = []

    # Building the WHERE clause
    where_clauses = []
    if program != '*':
        where_clauses.append("program = ?")
        parameters.append(program)
    if ip != '*':
        where_clauses.append("ip = ?")
        parameters.append(ip)
    if cidr:
        where_clauses.append("cidr = ?")
        parameters.append(cidr)
    if asn:
        where_clauses.append("asn = ?")
        parameters.append(asn)
    if port:
        if isinstance(port, list):
            placeholders = ', '.join('?' for _ in port)
            where_clauses.append(f"(port IN ({placeholders}) OR port LIKE ?)")
            parameters.extend(port)
            parameters.append(f'%{port[0]}%')
        else:
            where_clauses.append(f"(port = ? OR port LIKE ?)")
            parameters.append(port)
            parameters.append(f'%{port}%')
    if service:
        where_clauses.append("service = ?")
        parameters.append(service)
    if cves:
        where_clauses.append("cves LIKE ?")
        parameters.append(f'%{cves}%')
    if create_time:
        start_time, end_time = parse_time_range(create_time)
        where_clauses.append("created_at BETWEEN ? AND ?")
        parameters.extend([start_time, end_time])
    if update_time:
        start_time, end_time = parse_time_range(update_time)
        where_clauses.append("updated_at BETWEEN ? AND ?")
        parameters.extend([start_time, end_time])

    # Combine base query with where clauses
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # If count is requested, modify the query
    if count:
        query = "SELECT COUNT(*) FROM cidrs" + (" WHERE " + " AND ".join(where_clauses) if where_clauses else "")
        cursor.execute(query, parameters)
        count_result = cursor.fetchone()[0]
        print(count_result)
        return

    # Execute the final query
    cursor.execute(query, parameters)
    ips = cursor.fetchall()

    # Handle output
    if ips:
        if brief:
            unique_ips = set(ip_record[0] for ip_record in ips)  # Use a set for unique IPs
            print("\n".join(unique_ips))  # Print unique IP addresses
        else:
            result = [
                {
                    "ip": ip_record[0], "cidr": ip_record[1], "program": ip_record[7], "asn": ip_record[2], 
                    "port": ip_record[3], "service": ip_record[4], "cves": ip_record[8],
                    "created_at": ip_record[5], "updated_at": ip_record[6]
                }
                for ip_record in ips
            ]
            print(json.dumps(result, indent=4))

def delete_ip(ip='*', program='*', asn=None, cidr=None, port=None, service=None, cves=None):
    # Custom timestamp format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build the base query for deletion
    query = "DELETE FROM cidrs"
    parameters = []
    filters = []

    # Handle program filtering
    if program != '*':
        filters.append("program = ?")
        parameters.append(program)

    # Handle IP filtering
    if ip != '*':
        filters.append("ip = ?")
        parameters.append(ip)

    # Handle additional filters
    if asn:
        filters.append("asn = ?")
        parameters.append(asn)

    if cidr:
        filters.append("cidr = ?")
        parameters.append(cidr)

    # Handle port filtering
    if port:
        filters.append("(port = ? OR port LIKE ?)")
        parameters.append(port)
        parameters.append(f'%{port}%')  # Allow partial matches for ports

    if service:
        filters.append("service = ?")
        parameters.append(service)

    if cves:
        filters.append("cves LIKE ?")
        parameters.append(f"%{cves}%")  # Assuming CVEs are stored in a way that supports LIKE query

    # If there are filters, add them to the query
    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Execute the query to check if any rows match the criteria before deletion
    cursor.execute(query, parameters)
    if cursor.rowcount == 0:
        print(f"{timestamp} | error | No matching IP found for deletion with specified filters.")
        return

    # Perform the deletion
    cursor.execute(query, parameters)
    conn.commit()

    print(f"{timestamp} | success | IP '{ip}' deleted from program '{program}' with specified filters.")

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
    parser = argparse.ArgumentParser(description='Manage programs, domains, subdomains, and IPs')
    sub_parser = parser.add_subparsers(dest='command')

    # program commands
    program_parser = sub_parser.add_parser('program', help='Manage programs')
    program_action_parser = program_parser.add_subparsers(dest='action')

    program_action_parser.add_parser('add', help='add a new program').add_argument('program', help='Name of the program')
    
    list_programs_parser = program_action_parser.add_parser('list', help='List programs')
    list_programs_parser.add_argument('program', help="program name or wildcard '*' for all programs")
    list_programs_parser.add_argument('--brief', action='store_true', help='Show only program names')
    list_programs_parser.add_argument('--count', action='store_true', help='Count the number of returned records')


    delete_programs_parser = program_action_parser.add_parser('delete', help='Delete a program')
    delete_programs_parser.add_argument('program', help='Name of the program')
    delete_programs_parser.add_argument('--all', action='store_true', help='Delete all data related to the program')


    # Domain commands
    domain_parser = sub_parser.add_parser('domain', help='Manage domains in a program')
    domain_action_parser = domain_parser.add_subparsers(dest='action')

    add_domain_parser = domain_action_parser.add_parser('add', help='Add a domain')
    add_domain_parser.add_argument('domain', help='Domain name')
    add_domain_parser.add_argument('program', help='Program name')
    add_domain_parser.add_argument('--scope', choices=['inscope', 'outscope'], help='Scope of the domain (leave empty to keep current scope)')


    list_domains_parser = domain_action_parser.add_parser('list', help='List domains in a program')
    list_domains_parser.add_argument('domain', help='Domain name (use "*" for all domains)')
    list_domains_parser.add_argument('program', help='program name (use "*" for all programs)')
    list_domains_parser.add_argument('--scope', choices=['inscope', 'outscope'], help='Filter domains by scope')
    list_domains_parser.add_argument('--brief', action='store_true', help='Show only domain names')
    list_domains_parser.add_argument('--count', action='store_true', help='Count the number of returned records')


    delete_domain_parser = domain_action_parser.add_parser('delete', help='Delete a domain')
    delete_domain_parser.add_argument('domain', help='Domain name')
    delete_domain_parser.add_argument('program', help='program name')
    delete_domain_parser.add_argument('--scope', choices=['inscope', 'outscope'], help='Scope of the domain (default: inscope)')

    # Subdomain commands
    subdomain_parser = sub_parser.add_parser('subdomain', help='Manage subdomains in a program')
    subdomain_action_parser = subdomain_parser.add_subparsers(dest='action')

    add_subdomain_parser = subdomain_action_parser.add_parser('add', help='Add a subdomain')
    add_subdomain_parser.add_argument('subdomain', help='Subdomain name')
    add_subdomain_parser.add_argument('domain', help='Domain name')
    add_subdomain_parser.add_argument('program', help='program name')
    add_subdomain_parser.add_argument('--source', nargs='*', help='Source(s) (comma-separated)')
    add_subdomain_parser.add_argument('--unsource', nargs='*', help='Source(s) to remove (comma-separated)')
    add_subdomain_parser.add_argument('--scope', choices=['inscope', 'outscope'], default='inscope', help='Scope')
    add_subdomain_parser.add_argument('--resolved', choices=['yes', 'no'], default='no', help='Resolved status')
    add_subdomain_parser.add_argument('--ip', default='none', help='IP address of the subdomain')
    add_subdomain_parser.add_argument('--unip', action='store_true', help='Remove IP address from the subdomain')
    add_subdomain_parser.add_argument('--cdn_status', default='no', choices=['yes', 'no'], help='CDN status')
    add_subdomain_parser.add_argument('--cdn_name', default='none', help='Name of the CDN provider')
    add_subdomain_parser.add_argument('--uncdn_name', action='store_true', help='Remove CDN name from the subdomain')


    list_subdomains_parser = subdomain_action_parser.add_parser('list', help='List subdomains')
    list_subdomains_parser.add_argument('subdomain', help='Subdomain name or wildcard')
    list_subdomains_parser.add_argument('domain', help='Domain name or wildcard')
    list_subdomains_parser.add_argument('program', help='program name')
    list_subdomains_parser.add_argument('--source', nargs='*', help='Filter by source(s)')
    list_subdomains_parser.add_argument('--source-only', action='store_true', help='Show only matching subdomains')
    list_subdomains_parser.add_argument('--scope', choices=['inscope', 'outscope'], help='Filter by scope')
    list_subdomains_parser.add_argument('--resolved', choices=['yes', 'no'], help='Filter by resolved status')
    list_subdomains_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Filter by CDN status')
    list_subdomains_parser.add_argument('--ip', help='Filter by IP address')
    list_subdomains_parser.add_argument('--cdn_name', help='Filter by CDN provider name')
    list_subdomains_parser.add_argument('--brief', action='store_true', help='Show only subdomain names')
    list_subdomains_parser.add_argument('--create_time', help='Filter by creation time')
    list_subdomains_parser.add_argument('--update_time', help='Filter by last update time')
    list_subdomains_parser.add_argument('--count', action='store_true', help='Count the number of returned records')


    delete_subdomain_parser = subdomain_action_parser.add_parser('delete', help='Delete subdomains')
    delete_subdomain_parser.add_argument('subdomain', help='Subdomain to delete (use * to delete all)')
    delete_subdomain_parser.add_argument('domain', help='Domain name')
    delete_subdomain_parser.add_argument('program', help='program name')
    delete_subdomain_parser.add_argument('--resolved', choices=['yes', 'no'], help='Filter by resolved status')
    delete_subdomain_parser.add_argument('--source', help='Filter by source')
    delete_subdomain_parser.add_argument('--scope', choices=['inscope', 'outscope'], help='Filter by scope')
    delete_subdomain_parser.add_argument('--ip', help='Filter by IP address')
    delete_subdomain_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Filter by CDN status')
    delete_subdomain_parser.add_argument('--cdn_name', help='Filter by CDN provider name')

    # url commands
    url_parser = sub_parser.add_parser('url', help='Manage urls')
    live_action_parser = url_parser.add_subparsers(dest='action')

    add_url_parser = live_action_parser.add_parser('add', help='Add a live subdomain')
    add_url_parser.add_argument('url', help='URL of the live subdomain')
    add_url_parser.add_argument('subdomain', help='Subdomain')
    add_url_parser.add_argument('domain', help='Domain')
    add_url_parser.add_argument('program', help='program')
    add_url_parser.add_argument('--scheme', help='Scheme (http or https)')
    add_url_parser.add_argument('--method', help='HTTP method')
    add_url_parser.add_argument('--port', type=int, help='Port number')
    add_url_parser.add_argument('--status_code', type=int, help='HTTP status code')
    add_url_parser.add_argument('--scope', choices=['inscope', 'outscope'], help='Scope')
    add_url_parser.add_argument('--ip', help='IP address')
    add_url_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='CDN status')
    add_url_parser.add_argument('--cdn_name', help='Name of the CDN provider')
    add_url_parser.add_argument('--title', help='Title of the live subdomain')
    add_url_parser.add_argument('--webserver', help='Web server type')
    add_url_parser.add_argument('--webtech', help='Web technologies (comma-separated)')
    add_url_parser.add_argument('--cname', help='CNAME of the live subdomain')
    add_url_parser.add_argument('--location', help='Redirect location')

    list_url_parser = live_action_parser.add_parser('list', help='List urls')
    list_url_parser.add_argument('url', help='URL of the live subdomain')
    list_url_parser.add_argument('subdomain', help='Subdomain name or wildcard')
    list_url_parser.add_argument('domain', help='Domain name or wildcard')
    list_url_parser.add_argument('program', help='program name')
    list_url_parser.add_argument('--scheme', help='Filter by scheme')
    list_url_parser.add_argument('--method', help='Filter by HTTP method')
    list_url_parser.add_argument('--port', type=int, help='Filter by port')
    list_url_parser.add_argument('--status_code', type=int, help='Filter by HTTP status code')
    list_url_parser.add_argument('--ip', help='Filter by IP address')
    list_url_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Filter by CDN status')
    list_url_parser.add_argument('--cdn_name', help='Filter by CDN name')
    list_url_parser.add_argument('--title', help='Filter by title')
    list_url_parser.add_argument('--webserver', help='Filter by webserver')
    list_url_parser.add_argument('--webtech', help='Filter by web technologies')
    list_url_parser.add_argument('--cname', help='Filter by CNAME')
    list_url_parser.add_argument('--create_time', help='Filter by creation time')
    list_url_parser.add_argument('--update_time', help='Filter by update time')
    list_url_parser.add_argument('--brief', action='store_true', help='Show only subdomain names')
    list_url_parser.add_argument('--scope', help='Filter by scope')
    list_url_parser.add_argument('--location', help='Filter by redirect location')
    list_url_parser.add_argument('--count', action='store_true', help='Count the number of matching URLs')

    delete_url_parser = live_action_parser.add_parser('delete', help='Delete urls')
    delete_url_parser.add_argument('url', help='URL of the live subdomain')
    delete_url_parser.add_argument('subdomain', help='Subdomain')
    delete_url_parser.add_argument('domain', help='Domain')
    delete_url_parser.add_argument('program', help='program')
    delete_url_parser.add_argument('--scope', help='Filter by scope')
    delete_url_parser.add_argument('--cdn_status', choices=['yes', 'no'], help='Filter by CDN status')
    delete_url_parser.add_argument('--port', type=int, help='Filter by port')
    delete_url_parser.add_argument('--status_code', type=int, help='Filter by HTTP status code')

    # IP commands
    ip_parser = sub_parser.add_parser('ip', help='Manage IPs in a program')
    ip_action_parser = ip_parser.add_subparsers(dest='action')

    add_ip_parser = ip_action_parser.add_parser('add', help='Add an IP to a program')
    add_ip_parser.add_argument('ip', help='IP address')
    add_ip_parser.add_argument('program', help='Program name')
    add_ip_parser.add_argument('--cidr', help='CIDR notation')
    add_ip_parser.add_argument('--asn', help='Autonomous System Number')
    add_ip_parser.add_argument('--port', type=int, nargs='+', help='One or more port numbers')
    add_ip_parser.add_argument('--service', help='Service on the IP')
    add_ip_parser.add_argument('--cves', nargs='+', help='Comma-separated CVEs associated with the IP')

    list_ips_parser = ip_action_parser.add_parser('list', help='List IPs in a program')
    list_ips_parser.add_argument('ip', help='IP or CIDR (use * for all IPs)')
    list_ips_parser.add_argument('program', help='program (use * for all programs)')
    list_ips_parser.add_argument('--cidr', help='Filter by CIDR')
    list_ips_parser.add_argument('--asn', help='Filter by ASN')
    list_ips_parser.add_argument('--port', type=int, help='Filter by port')
    list_ips_parser.add_argument('--service', help='Filter by service')
    list_ips_parser.add_argument('--cves', help='Filter by CVEs')  # Added this line
    list_ips_parser.add_argument('--brief', action='store_true', help='Show only IP addresses')
    list_ips_parser.add_argument('--create_time', help='Filter by creation time')
    list_ips_parser.add_argument('--update_time', help='Filter by update time')
    list_ips_parser.add_argument('--count', action='store_true', help='Show count of matching IPs')

    delete_ip_parser = ip_action_parser.add_parser('delete', help='Delete IPs')
    delete_ip_parser.add_argument('ip', help='IP or CIDR (use * for all IPs)')  # Specify IP or CIDR
    delete_ip_parser.add_argument('program', help='program (use * for all programs)')  # Specify program
    delete_ip_parser.add_argument('--port', type=int, help='Filter by port')  # Optional port filter
    delete_ip_parser.add_argument('--service', help='Filter by service')  # Optional service filter
    delete_ip_parser.add_argument('--asn', help='Filter by ASN')  # Optional ASN filter
    delete_ip_parser.add_argument('--cidr', help='Filter by CIDR')  # Optional CIDR filter
    delete_ip_parser.add_argument('--cves', help='Filter by CVEs')  # Optional CVEs filter

    args = parser.parse_args()

    # Handle commands
    if args.command == 'program':
        if args.action == 'add':
            add_program(program=args.program)
        elif args.action == 'list':
            list_programs(program=args.program, brief=args.brief, count=args.count)
        elif args.action == 'delete':
            delete_program(program=args.program, delete_all=args.all)

    elif args.command == 'domain':
        if args.action == 'add':
            add_domain(args.domain, args.program, scope=args.scope)
        elif args.action == 'list':
            list_domains(args.domain, args.program, brief=args.brief, count=args.count, scope=args.scope)
        elif args.action == 'delete':
            delete_domain(args.domain if args.domain != '*' else '*', args.program, scope=args.scope)

    elif args.command == 'subdomain':
        if args.action == 'add':
            add_subdomain(args.subdomain, args.domain, args.program, sources=args.source, unsources=args.unsource, scope=args.scope, resolved=args.resolved, ip_address=args.ip, unip=args.unip, cdn_status=args.cdn_status, cdn_name=args.cdn_name, uncdn_name=args.uncdn_name)
        elif args.action == 'list':
            list_subdomains(subdomain=args.subdomain, domain=args.domain, program=args.program, sources=args.source, scope=args.scope, resolved=args.resolved, brief=args.brief, source_only=args.source_only, cdn_status=args.cdn_status, ip=args.ip, cdn_name=args.cdn_name, count=args.count, create_time=args.create_time, update_time=args.update_time)
        elif args.action == 'delete':
            if os.path.isfile(args.subdomain):
                with open(args.subdomain, 'r') as file:
                    subdomains = [line.strip() for line in file.readlines() if line.strip()]
                for subdomain in subdomains:
                    delete_subdomain(subdomain, args.domain, args.program, args.scope, args.source, args.resolved)
            else:
                delete_subdomain(args.subdomain, args.domain, args.program, args.scope, args.source, args.resolved, args.ip, args.cdn_status, args.cdn_name) if args.subdomain != '*' else delete_subdomain('*', args.domain, args.program, args.scope, args.source, args.resolved)

    elif args.command == 'url':
        if args.action == 'add':
            add_url(args.url, args.subdomain, args.domain, args.program, scheme=args.scheme, method=args.method, port=args.port, status_code=args.status_code, ip_address=args.ip, cdn_status=args.cdn_status, cdn_name=args.cdn_name, title=args.title, webserver=args.webserver, webtech=args.webtech, cname=args.cname, scope=args.scope, location=args.location)
        elif args.action == 'list':
            list_urls(args.url, args.subdomain, args.domain, args.program, scheme=args.scheme, method=args.method, port=args.port, status_code=args.status_code, ip=args.ip, cdn_status=args.cdn_status, cdn_name=args.cdn_name, title=args.title, webserver=args.webserver, webtech=args.webtech, cname=args.cname, create_time=args.create_time, update_time=args.update_time, brief=args.brief, scope=args.scope, location=args.location, count=args.count)
        elif args.action == 'delete':
            delete_url(args.url, args.subdomain, args.domain, args.program, scheme=args.scheme, method=args.method, port=args.port, status_code=args.status_code, ip_address=args.ip, cdn_status=args.cdn_status, cdn_name=args.cdn_name, title=args.title, webserver=args.webserver, webtech=args.webtech, cname=args.cname, scope=args.scope)
            
    elif args.command == 'ip':
        if args.action == 'add':
            add_ip(args.ip, args.program, args.cidr, args.asn, args.port, args.service, args.cves)
        elif args.action == 'list':
            list_ip(args.ip, args.program, cidr=args.cidr, asn=args.asn, port=args.port, service=args.service, brief=args.brief, cves=args.cves, create_time=args.create_time, update_time=args.update_time, count=args.count)
        elif args.action == 'delete':
            delete_ip(ip=args.ip, program=args.program, asn=args.asn, cidr=args.cidr, port=args.port, service=args.service, cves=args.cves)

if __name__ == "__main__":
    main()

# Close the database connection when done
conn.close()
